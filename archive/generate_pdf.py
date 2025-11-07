#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate professional PDF from markdown file."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import markdown2
import re
from datetime import datetime

def create_pdf(md_file, output_file):
    """Create a professional PDF from markdown."""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Container for the 'Flowable' objects
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        spaceAfter=40,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#2c5aa0'),
        borderWidth=1,
        borderPadding=5,
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10,
        fontName='Helvetica'
    )

    # Parse markdown into lines
    lines = md_content.split('\n')

    in_list = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            if not in_list:
                story.append(Spacer(1, 6))
            continue

        # Title (first H1)
        if line.startswith('# ') and i < 5:
            title_text = line[2:].strip()
            # Remove any markdown formatting
            title_text = re.sub(r'\*\*', '', title_text)
            story.append(Paragraph(title_text, title_style))
            continue

        # Subtitle (italic text right after title)
        if line.startswith('**') and line.endswith('**') and i < 10:
            subtitle_text = line[2:-2].strip()
            story.append(Paragraph(subtitle_text, subtitle_style))
            continue

        # Horizontal rules
        if line == '---':
            story.append(Spacer(1, 12))
            continue

        # H2 headers
        if line.startswith('## '):
            in_list = False
            header_text = line[3:].strip()
            header_text = re.sub(r'\*\*', '', header_text)
            story.append(Paragraph(header_text, h1_style))
            continue

        # H3 headers
        if line.startswith('### '):
            in_list = False
            header_text = line[4:].strip()
            header_text = re.sub(r'\*\*', '', header_text)
            story.append(Paragraph(header_text, h2_style))
            continue

        # H4 headers
        if line.startswith('#### '):
            in_list = False
            header_text = line[5:].strip()
            header_text = re.sub(r'\*\*', '', header_text)
            story.append(Paragraph(header_text, h3_style))
            continue

        # Bullet points
        if line.startswith('- ') or line.startswith('* '):
            in_list = True
            bullet_text = line[2:].strip()
            # Convert markdown bold to HTML
            bullet_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', bullet_text)
            bullet_text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', bullet_text)
            story.append(Paragraph(f'• {bullet_text}', bullet_style))
            continue

        # Regular paragraph
        in_list = False
        para_text = line
        # Convert markdown formatting to HTML
        para_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', para_text)
        para_text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#d14">\1</font>', para_text)
        para_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', para_text)

        story.append(Paragraph(para_text, body_style))

    # Add footer with date
    footer_text = f'<i>Generated on {datetime.now().strftime("%B %d, %Y")}</i>'
    story.append(Spacer(1, 20))
    story.append(Paragraph(footer_text, subtitle_style))

    # Build PDF
    doc.build(story)
    print(f"PDF created successfully: {output_file}")

if __name__ == '__main__':
    create_pdf(
        'twinzo_capabilities_summary.md',
        'twinzo_capabilities_summary.pdf'
    )
