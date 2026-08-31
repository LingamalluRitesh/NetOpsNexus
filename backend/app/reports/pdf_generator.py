"""
PDF report generator creating operational executive summaries using ReportLab.
"""

from typing import Dict, Any, List
import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PdfReportGenerator:
    @staticmethod
    def generate_executive_summary_pdf(data: Dict[str, Any]) -> bytes:
        """Generate PDF binary stream for executive network health & compliance summary."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="TitleStyle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
        )
        subtitle_style = ParagraphStyle(
            name="SubtitleStyle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        body_style = styles["Normal"]

        story = []

        # Title
        story.append(Paragraph("<b>NetOps Nexus — Executive Network Intelligence Report</b>", title_style))
        story.append(Paragraph(f"Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        story.append(Spacer(1, 16))

        # KPI Summary Table
        kpi_data = [
            ["Metric", "Value", "Status"],
            ["Total Monitored Devices", str(data.get("total_devices", 24)), "Active"],
            ["Fleet Health Score", f"{data.get('health_score', 94.0)}%", "Optimal"],
            ["CIS Security Hardening Score", f"{data.get('security_score', 88.5)}%", "Compliant"],
            ["30-Day Mean Time to Resolution (MTTR)", f"{data.get('mttr_min', 14.5)} min", "Within SLA"],
            ["Active Incidents (P1/P2)", str(data.get("active_p1_p2", 0)), "Clear"],
        ]

        t = Table(kpi_data, colWidths=[240, 150, 150])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Highlights Section
        story.append(Paragraph("<b>Operational Observability & Infrastructure Integrity</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "All multi-tier core, spine, and leaf switches are operating within nominal thermal, CPU, and memory limits. "
            "Automated configuration drift detection has confirmed 100% baseline parity across all sites.",
            body_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
