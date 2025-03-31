"""
File processor module for handling different file types.
"""

import io
import pandas as pd
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def extract_text_from_pdf(file_content):
    """
    Extract text from a PDF file.
    
    Args:
        file_content: Binary content of the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_excel(file_content):
    """
    Extract text from an Excel file.
    
    Args:
        file_content: Binary content of the Excel file
        
    Returns:
        Extracted text as a string
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        # Convert DataFrame to string, handling different data types
        text = ""
        for _, row in df.iterrows():
            for item in row:
                if pd.notna(item):  # Skip NaN values
                    text += str(item) + " "
            text += "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from Excel: {str(e)}")

def generate_pdf_report(sorted_features, processing_time, feature_count, summary=None):
    """
    Generate a PDF report with the processing results.
    
    Args:
        sorted_features: List of sorted features
        processing_time: Time taken to process the text
        feature_count: Number of features processed
        summary: Optional summary of the text
        
    Returns:
        PDF file content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    )
    elements.append(Paragraph("NLP Text Processing Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Processing info
    elements.append(Paragraph(f"<b>Processing Time:</b> {processing_time:.4f} seconds", styles["Normal"]))
    elements.append(Paragraph(f"<b>Features Processed:</b> {feature_count}", styles["Normal"]))
    elements.append(Paragraph("<b>Sorting Method:</b> Optimized Radix Sort", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Summary section if available
    if summary:
        elements.append(Paragraph("<b>Text Summary:</b>", styles["Heading2"]))
        elements.append(Paragraph(summary, styles["Normal"]))
        elements.append(Spacer(1, 12))
    
    # Sorted features
    elements.append(Paragraph("<b>Sorted Features:</b>", styles["Heading2"]))
    
    # Create table data
    data = [["#", "Feature"]]
    for i, feature in enumerate(sorted_features[:1000], 1):  # Limit to 1000 items to avoid huge PDFs
        data.append([str(i), feature])
    
    # Create table
    if len(data) > 1:
        table = Table(data, colWidths=[30, 450])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No features found.", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue() 