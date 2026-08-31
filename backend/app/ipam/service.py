"""
Domain service for IPAM Subnets, IP allocation, Conflict detection, and Subnet Split/Merge.
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.ipam.models import Subnet, IpAddress, IpConflict, Vrf, SubnetStatus, IpStatus
from backend.app.ipam.schemas import (
    SubnetCreate, SubnetResponse, SubnetSplitRequest, SubnetMergeRequest,
    IpAddressCreate, IpAddressResponse, IpConflictResponse
)
from backend.app.ipam.cidr_engine import CidrEngine


class IpamService:
    @staticmethod
    async def list_subnets(db: AsyncSession, vrf_id: Optional[int] = None, site_id: Optional[int] = None) -> List[SubnetResponse]:
        """List all managed subnets with dynamic utilization metrics calculated."""
        stmt = select(Subnet).options(selectinload(Subnet.ip_addresses))
        if vrf_id:
            stmt = stmt.where(Subnet.vrf_id == vrf_id)
        if site_id:
            stmt = stmt.where(Subnet.site_id == site_id)
        
        res = await db.execute(stmt)
        subnets = res.scalars().all()
        responses = []

        for s in subnets:
            used = sum(1 for ip in s.ip_addresses if ip.status == IpStatus.ALLOCATED)
            reserved = sum(1 for ip in s.ip_addresses if ip.status == IpStatus.RESERVED)
            avail = max(0, s.total_ips - (used + reserved))
            util = round(((used + reserved) / max(1, s.total_ips)) * 100.0, 1)

            responses.append(
                SubnetResponse(
                    id=s.id,
                    network_address=s.network_address,
                    prefix_len=s.prefix_len,
                    ip_version=s.ip_version,
                    vrf_id=s.vrf_id,
                    site_id=s.site_id,
                    vlan_id=s.vlan_id,
                    name=s.name,
                    description=s.description,
                    gateway_ip=s.gateway_ip,
                    total_ips=s.total_ips,
                    used_ips=used,
                    reserved_ips=reserved,
                    available_ips=avail,
                    utilization_pct=util,
                    status=s.status,
                    created_at=s.created_at,
                )
            )
        return responses

    @staticmethod
    async def create_subnet(db: AsyncSession, data: SubnetCreate) -> SubnetResponse:
        """Create new subnet and calculate total addresses."""
        cidr_calc = CidrEngine.calculate_cidr(f"{data.network_address}/{data.prefix_len}")
        gateway = data.gateway_ip or cidr_calc.first_usable_ip

        subnet = Subnet(
            network_address=cidr_calc.network_address,
            prefix_len=data.prefix_len,
            ip_version=data.ip_version,
            vrf_id=data.vrf_id,
            site_id=data.site_id,
            vlan_id=data.vlan_id,
            name=data.name,
            description=data.description,
            gateway_ip=gateway,
            total_ips=cidr_calc.total_addresses,
            used_ips=0,
            reserved_ips=0,
            status=data.status,
        )
        db.add(subnet)
        await db.commit()
        await db.refresh(subnet)

        # Allocate gateway IP
        gw_ip = IpAddress(
            subnet_id=subnet.id,
            address=gateway,
            status=IpStatus.RESERVED,
            description="Default Gateway",
        )
        db.add(gw_ip)
        await db.commit()

        return SubnetResponse(
            id=subnet.id,
            network_address=subnet.network_address,
            prefix_len=subnet.prefix_len,
            ip_version=subnet.ip_version,
            vrf_id=subnet.vrf_id,
            site_id=subnet.site_id,
            vlan_id=subnet.vlan_id,
            name=subnet.name,
            description=subnet.description,
            gateway_ip=subnet.gateway_ip,
            total_ips=subnet.total_ips,
            used_ips=0,
            reserved_ips=1,
            available_ips=subnet.total_ips - 1,
            utilization_pct=round((1 / max(1, subnet.total_ips)) * 100.0, 1),
            status=subnet.status,
            created_at=subnet.created_at,
        )

    @staticmethod
    async def split_subnet(db: AsyncSession, req: SubnetSplitRequest) -> List[SubnetResponse]:
        """Split existing subnet into smaller prefix blocks."""
        stmt = select(Subnet).where(Subnet.id == req.subnet_id)
        res = await db.execute(stmt)
        parent = res.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Subnet not found")

        parent_cidr = f"{parent.network_address}/{parent.prefix_len}"
        try:
            new_cidrs = CidrEngine.split_subnet(parent_cidr, req.new_prefix_len)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Delete parent and create child subnets
        await db.delete(parent)
        created_subnets = []

        for idx, cidr_str in enumerate(new_cidrs, start=1):
            calc = CidrEngine.calculate_cidr(cidr_str)
            child = Subnet(
                network_address=calc.network_address,
                prefix_len=req.new_prefix_len,
                ip_version=parent.ip_version,
                vrf_id=parent.vrf_id,
                site_id=parent.site_id,
                vlan_id=parent.vlan_id,
                name=f"{parent.name} - Part {idx}",
                description=f"Split from {parent_cidr}",
                gateway_ip=calc.first_usable_ip,
                total_ips=calc.total_addresses,
                used_ips=0,
                reserved_ips=0,
            )
            db.add(child)
            created_subnets.append(child)

        await db.commit()
        for c in created_subnets:
            await db.refresh(c)

        return [
            SubnetResponse(
                id=s.id,
                network_address=s.network_address,
                prefix_len=s.prefix_len,
                ip_version=s.ip_version,
                vrf_id=s.vrf_id,
                site_id=s.site_id,
                vlan_id=s.vlan_id,
                name=s.name,
                description=s.description,
                gateway_ip=s.gateway_ip,
                total_ips=s.total_ips,
                used_ips=0,
                reserved_ips=0,
                available_ips=s.total_ips,
                utilization_pct=0.0,
                status=s.status,
                created_at=s.created_at,
            )
            for s in created_subnets
        ]

    @staticmethod
    async def allocate_ip(db: AsyncSession, data: IpAddressCreate) -> IpAddressResponse:
        """Allocate or reserve specific IP address within subnet."""
        # Check conflict
        stmt = select(IpAddress).where(IpAddress.subnet_id == data.subnet_id, IpAddress.address == data.address)
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            if existing.status == IpStatus.ALLOCATED and existing.mac_address != data.mac_address:
                # Record IP conflict
                conflict = IpConflict(
                    ip_address=data.address,
                    subnet_id=data.subnet_id,
                    conflicting_macs=[existing.mac_address, data.mac_address],
                    conflicting_device_ids=[existing.device_id, data.device_id],
                )
                db.add(conflict)
                await db.commit()
                raise HTTPException(status_code=409, detail=f"IP address {data.address} is already allocated to MAC {existing.mac_address}")
            else:
                existing.status = data.status
                existing.description = data.description
                existing.allocated_to = data.allocated_to
                await db.commit()
                return existing

        ip_obj = IpAddress(**data.model_dump())
        db.add(ip_obj)
        await db.commit()
        await db.refresh(ip_obj)
        return ip_obj

    @staticmethod
    async def release_ip(db: AsyncSession, ip_id: int):
        """Release allocated IP address back to available pool."""
        stmt = select(IpAddress).where(IpAddress.id == ip_id)
        res = await db.execute(stmt)
        ip_obj = res.scalar_one_or_none()
        if not ip_obj:
            raise HTTPException(status_code=404, detail="IP address record not found")
        await db.delete(ip_obj)
        await db.commit()

    @staticmethod
    async def list_conflicts(db: AsyncSession) -> List[IpConflictResponse]:
        """Fetch all recorded IP address conflicts."""
        stmt = select(IpConflict).order_by(IpConflict.detected_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())
