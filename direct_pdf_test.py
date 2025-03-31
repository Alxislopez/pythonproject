"""
Direct PDF generation test script to isolate any reportlab issues.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def main():
    # Create a PDF
    filename = "direct_test.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Add content
    elements = []
    elements.append(Paragraph("Direct PDF Test", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("This is a direct test of PDF generation, bypassing the API.", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    print(f"PDF created at: {filename}")

if __name__ == "__main__":
    main() 