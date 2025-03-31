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
    """
    try:
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
        # Limit to 1000 items to avoid huge PDFs
        max_features = min(1000, len(sorted_features))
        
        for i, feature in enumerate(sorted_features[:max_features], 1):
            # Ensure the feature is a string and not too long
            feature_str = str(feature)
            if len(feature_str) > 100:
                feature_str = feature_str[:97] + "..."
            data.append([str(i), feature_str])
        
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
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating PDF: {str(e)}\n{error_details}")
        
        # Create a simple error PDF instead
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Error Generating PDF Report", styles["Heading1"]),
            Paragraph(f"An error occurred: {str(e)}", styles["Normal"])
        ]
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

def generate_excel_report(sorted_features, processing_time, feature_count, summary=None):
    """
    Generate an Excel report with the processing results.
    
    Args:
        sorted_features: List of sorted features
        processing_time: Time taken to process the text
        feature_count: Number of features processed
        summary: Optional summary of the text
        
    Returns:
        Excel file content as bytes
    """
    try:
        import pandas as pd
        import io
        
        # Create a buffer
        buffer = io.BytesIO()
        
        # Create a pandas Excel writer using the buffer
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        
        # Convert the data to a DataFrame
        data = {'#': range(1, len(sorted_features) + 1), 'Feature': sorted_features}
        df = pd.DataFrame(data)
        
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Sorted Features', index=False)
        
        # Get a reference to the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sorted Features']
        
        # Add a summary sheet if available
        if summary:
            # Create a summary DataFrame
            summary_data = {'Summary': [summary]}
            summary_df = pd.DataFrame(summary_data)
            
            # Write the summary to a new sheet
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format the summary sheet
            summary_worksheet = writer.sheets['Summary']
            summary_worksheet.set_column('A:A', 100)
        
        # Add metadata sheet
        metadata = {
            'Metric': ['Processing Time', 'Features Processed', 'Sorting Method'],
            'Value': [f"{processing_time:.4f} seconds", str(feature_count), "Optimized Radix Sort"]
        }
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        # Format columns
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 50)
        
        # Close the writer and get the content
        writer.close()
        buffer.seek(0)
        
        return buffer.getvalue()
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating Excel report: {str(e)}\n{error_details}")
        
        # Create a simple error Excel file
        buffer = io.BytesIO()
        df = pd.DataFrame({'Error': [f"Error generating Excel report: {str(e)}"]})
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue() 