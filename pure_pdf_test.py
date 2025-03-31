"""
Pure PDF generation test with minimal dependencies.
"""

def create_simple_pdf(output_file="simple_test.pdf"):
    try:
        from reportlab.pdfgen import canvas
        
        # Create a canvas
        c = canvas.Canvas(output_file)
        
        # Add text
        c.drawString(100, 750, "PDF Test - Direct Canvas Method")
        c.drawString(100, 730, "If you can see this, PDF generation works.")
        
        # Save the PDF
        c.save()
        return True
    except Exception as e:
        print(f"Error creating simple PDF: {e}")
        return False

if __name__ == "__main__":
    success = create_simple_pdf()
    if success:
        print("PDF created successfully!")
    else:
        print("PDF creation failed!") 