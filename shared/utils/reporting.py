import csv
import io
import textwrap
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _draw_wrapped_lines(pdf, text: str, x: float, y: float, width: int = 95) -> float:
    for line in textwrap.wrap(text, width=width):
        pdf.drawString(x, y, line)
        y -= 14
    return y


def build_pdf(content: Dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    pdf.setTitle(content.get("title", "PixelCheck Report"))
    pdf.drawString(50, 750, content.get("title", "PixelCheck Report"))
    pdf.drawString(50, 730, f"Generated: {datetime.utcnow().isoformat()}Z")
    y = 700
    for key, value in content.items():
        if key == "title":
            continue
        pdf.drawString(50, y, f"{key}: {value}")
        y -= 20
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def build_analysis_pdf(
    title: str,
    summary: Dict[str, str],
    features: Dict[str, float],
    observations: Dict[str, str],
    recommendation: str,
    image_bytes: Optional[bytes] = None,
    narrative_lines: Optional[List[str]] = None,
    conclusion: Optional[str] = None,
) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    pdf.setTitle(title)

    # Header
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 770, title)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 755, f"Generated: {datetime.utcnow().isoformat()}Z")

    y = 730

    # Image thumbnail if provided
    if image_bytes:
        try:
            img_reader = ImageReader(io.BytesIO(image_bytes))
            pdf.drawImage(img_reader, 50, 520, width=2.5 * inch, height=2.5 * inch, preserveAspectRatio=True)
            y = 520
        except Exception:
            # Fallback: ignore image if cannot be rendered
            pass

    # Summary section
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(300, 700, "Resumen")
    pdf.setFont("Helvetica", 10)
    offset = 685
    for key, val in summary.items():
        pdf.drawString(300, offset, f"{key}: {val}")
        offset -= 14

    # Narrative
    pdf.setFont("Helvetica-Bold", 12)
    context_start = y - 30
    pdf.drawString(50, context_start, "Contexto del análisis")
    pdf.setFont("Helvetica", 10)
    context_y = context_start - 16
    if narrative_lines:
        for paragraph in narrative_lines:
            context_y = _draw_wrapped_lines(pdf, paragraph, 50, context_y)
            context_y -= 4
    else:
        context_y -= 14

    # Features (bars)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, context_y - 10, "Métricas clave")
    pdf.setFont("Helvetica", 10)
    bar_y = context_y - 30
    bar_width = 200
    for name, val in features.items():
        pdf.drawString(50, bar_y, f"{name.replace('_', ' ').title()}: {val:.2f}")
        pdf.setStrokeColor(colors.grey)
        pdf.rect(180, bar_y - 8, bar_width, 8, stroke=1, fill=0)
        pdf.setFillColor(colors.HexColor("#3b82f6"))
        pdf.rect(180, bar_y - 8, bar_width * min(max(val, 0), 1), 8, stroke=0, fill=1)
        pdf.setFillColor(colors.black)
        bar_y -= 16

    # Observations
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, bar_y - 10, "Observaciones")
    pdf.setFont("Helvetica", 10)
    obs_y = bar_y - 26
    for key, val in observations.items():
        pdf.drawString(50, obs_y, f"- {val}")
        obs_y -= 14
    obs_y -= 4

    if conclusion:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, obs_y - 10, "Conclusión")
        pdf.setFont("Helvetica", 10)
        obs_y = _draw_wrapped_lines(pdf, conclusion, 50, obs_y - 26) - 6

    # Recommendation
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, obs_y - 10, "Recomendación")
    pdf.setFont("Helvetica", 10)
    _draw_wrapped_lines(pdf, recommendation, 50, obs_y - 26)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def build_csv(headers: Iterable[str], rows: Iterable[Iterable[str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")
