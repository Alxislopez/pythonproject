"""
Test script for PDF generation functionality.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def create_test_pdf():
    """Create a simple test PDF file"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add a simple paragraph to the PDF
    story.append(Paragraph("This is a test PDF document", styles["Heading1"]))
    story.append(Paragraph("If you can see this text, PDF generation is working correctly.", styles["Normal"]))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF content
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    # Create a test PDF and save it
    pdf_content = create_test_pdf()
    
    with open("test_pdf.pdf", "wb") as f:
        f.write(pdf_content)
    
    print("Test PDF created successfully. Check test_pdf.pdf file.") 