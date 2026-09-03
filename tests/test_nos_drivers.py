"""
Unit tests for Multi-Vendor Network Operating System (NOS) Drivers.
"""

import pytest
from backend.app.adapters.drivers.cisco_iosxe import CiscoIosXeDriver
from backend.app.adapters.drivers.arista_eos import AristaEosDriver
from backend.app.adapters.drivers.juniper_junos import JuniperJunosDriver
from backend.app.adapters.drivers.paloalto_panos import PaloAltoPanOsDriver


def test_cisco_iosxe_driver():
    driver = CiscoIosXeDriver(hostname="HQ-CORE-R01", ip_address="10.100.0.1")
    ver = driver.parse_show_version()
    assert ver["vendor"] == "Cisco Systems"
    assert ver["hostname"] == "HQ-CORE-R01"

    banner = driver.generate_banner()
    assert "Cisco Catalyst 9300" in banner

    interfaces = [
        {"name": "HundredGigE1/0/1", "ip": "10.100.0.1", "admin_status": "up", "oper_status": "up"},
        {"name": "GigabitEthernet0/0/0", "ip": "unassigned", "admin_status": "down", "oper_status": "down"},
    ]
    brief = driver.parse_show_ip_interface_brief(interfaces)
    assert "HundredGigE1/0/1" in brief
    assert "administratively down" in brief

    cfg = driver.parse_show_running_config()
    assert "hostname HQ-CORE-R01" in cfg
    assert "router bgp 65001" in cfg


def test_arista_eos_driver():
    driver = AristaEosDriver(hostname="HQ-SPINE-SW01", ip_address="10.100.0.11")
    ver = driver.parse_show_version()
    assert ver["vendor"] == "Arista Networks"
    assert "4.30.2F" in ver["version"]

    interfaces = [
        {"name": "Ethernet1/1", "description": "Uplink", "speed_mbps": 100000, "oper_status": "up"}
    ]
    status = driver.parse_show_interfaces_status(interfaces)
    assert "connected" in status
    assert "100G" in status

    cfg = driver.parse_show_running_config()
    assert "vxlan udp-port 4789" in cfg
    assert "address-family evpn" in cfg


def test_juniper_junos_driver():
    driver = JuniperJunosDriver(hostname="LON-EDGE-R01", ip_address="10.200.0.1")
    ver = driver.parse_show_version()
    assert ver["vendor"] == "Juniper Networks"
    assert "MX204" in ver["model"]

    cfg = driver.parse_show_configuration()
    assert "host-name LON-EDGE-R01;" in cfg
    assert "autonomous-system 65003;" in cfg


def test_paloalto_panos_driver():
    driver = PaloAltoPanOsDriver(hostname="HQ-FW01", ip_address="10.100.0.50")
    info = driver.parse_show_system_info()
    assert info["vendor"] == "Palo Alto Networks"
    assert "PA-5450" in info["model"]

    rules = driver.parse_show_security_rules()
    assert "ALLOW-OUTBOUND-WEB" in rules
    assert "DENY-ALL-OTHER" in rules
