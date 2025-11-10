import csv
import io
from datetime import datetime
from typing import Dict, Iterable

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


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


def build_csv(headers: Iterable[str], rows: Iterable[Iterable[str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")
