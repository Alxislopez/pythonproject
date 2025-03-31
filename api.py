from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import time
import re
from typing import List, Optional
import uvicorn
import os
from text_utils import preprocess_text, extract_features, summarize_text
from radix_sort import radix_sort_numeric, radix_sort_strings
from file_processor import extract_text_from_pdf, extract_text_from_excel, generate_pdf_report, generate_excel_report, generate_csv_report
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ML Data Convertor API")

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)
    print(f"Created static directory at: {os.path.abspath('static')}")

# Serve static files (for PDF downloads)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for request/response
class ProcessTextRequest(BaseModel):
    text: str
    feature_type: str = "numbers"  # 'words', 'sentences', 'ngrams', 'numbers'
    ngram_size: int = 2
    base: int = 10
    summarize: bool = False
    summary_ratio: float = 0.2  # Percentage of original text to keep in summary

class ProcessResponse(BaseModel):
    sorted_features: List[str]
    processing_time: float
    feature_count: int
    summary: Optional[str] = None

def extract_numbers_from_text(text):
    """Extract all numbers from text."""
    number_strings = re.findall(r'-?\d+(?:\.\d+)?', text)
    
    numbers = []
    for num_str in number_strings:
        if '.' in num_str:
            num = float(num_str)
            numbers.append(int(num * 1000))
        else:
            numbers.append(int(num_str))
    
    return numbers

@app.post("/api/process", response_model=ProcessResponse)
async def process_text(request: ProcessTextRequest):
    """Process text with the specified feature extraction and sorting method.
    Uses optimized radix sort exclusively for all sorting operations.
    """
    try:
        start_time = time.time()
        summary = None
        
        # Generate summary if requested
        if request.summarize:
            summary = summarize_text(request.text, request.summary_ratio)
        
        if request.feature_type == 'numbers':
            # Extract and sort numbers
            features = extract_numbers_from_text(request.text)
            # Using radix_sort_numeric for optimal performance
            sorted_features = radix_sort_numeric(features, base=request.base)
            # Convert back to strings with proper formatting
            sorted_features = [str(num) if num % 1000 == 0 else f"{num/1000:.3f}" 
                              for num in sorted_features]
        else:
            # Process text for other feature types
            processed_text = preprocess_text(request.text)
            
            # Extract features
            if request.feature_type == 'ngrams':
                features = extract_features(processed_text, 
                                           feature_type=request.feature_type, 
                                           n=request.ngram_size)
            else:
                features = extract_features(processed_text, 
                                           feature_type=request.feature_type)
            
            # Using radix_sort_strings for all string sorting
            sorted_features = radix_sort_strings(features)
        
        processing_time = time.time() - start_time
        
        return {
            "sorted_features": sorted_features,
            "processing_time": processing_time,
            "feature_count": len(sorted_features),
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/upload-file")
async def upload_file(
    file: UploadFile = File(...), 
    feature_type: str = Form("numbers"),
    ngram_size: int = Form(2),
    base: int = Form(10),
    summarize: bool = Form(False),
    summary_ratio: float = Form(0.2)
):
    """Process text from an uploaded file."""
    try:
        content = await file.read()
        
        # Extract text based on file type
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            text = extract_text_from_pdf(content)
        elif file_ext in ['xlsx', 'xls']:
            text = extract_text_from_excel(content)
        else:
            # Default to UTF-8 text decoding for other file types
            text = content.decode("utf-8")
        
        # Process using the same logic as the text endpoint
        request = ProcessTextRequest(
            text=text,
            feature_type=feature_type,
            ngram_size=ngram_size,
            base=base,
            summarize=summarize,
            summary_ratio=summary_ratio
        )
        return await process_text(request)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.post("/api/download-pdf")
async def download_results_as_pdf(request: ProcessTextRequest):
    """Process text and return results as a downloadable PDF."""
    try:
        # Process the text first
        response = await process_text(request)
        
        # Generate PDF
        pdf_content = generate_pdf_report(
            response["sorted_features"],
            response["processing_time"],
            response["feature_count"],
            response.get("summary")
        )
        
        # Return PDF file
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=nlp_processing_results.pdf"
            }
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.post("/api/create-pdf-file")
async def create_pdf_file(request: ProcessTextRequest):
    """Process text and save a PDF file on the server."""
    try:
        print(f"PDF file creation requested with feature type: {request.feature_type}")
        
        # Process the text first
        response = await process_text(request)
        
        # Generate a unique filename
        import uuid
        import os
        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join("static", filename)
        
        # Make sure the directory exists with proper permissions
        if not os.path.exists("static"):
            print("Creating static directory")
            os.makedirs("static", exist_ok=True, mode=0o777)
        
        print(f"Generating PDF file at: {filepath}")
        
        # Generate PDF content
        pdf_content = generate_pdf_report(
            response["sorted_features"],
            response["processing_time"],
            response["feature_count"],
            response.get("summary")
        )
        
        print(f"PDF content generated, size: {len(pdf_content)} bytes")
        
        # Save the PDF file
        with open(filepath, "wb") as f:
            f.write(pdf_content)
            
        print(f"PDF file saved successfully: {filepath}")
        
        # Return the file path for downloading
        download_url = f"/static/{filename}"
        print(f"Download URL: {download_url}")
        return {"download_url": download_url, "filename": filename}
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF file creation error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.post("/api/create-excel-file")
async def create_excel_file(request: ProcessTextRequest):
    """Process text and save an Excel file on the server."""
    try:
        # Process the text first
        response = await process_text(request)
        
        # Generate a unique filename
        import uuid
        import os
        filename = f"report_{uuid.uuid4().hex[:8]}.xlsx"
        filepath = os.path.join("static", filename)
        
        # Make sure the directory exists
        os.makedirs("static", exist_ok=True)
        
        # Import the Excel generator
        from file_processor import generate_excel_report
        
        # Generate Excel content
        excel_content = generate_excel_report(
            response["sorted_features"],
            response["processing_time"],
            response["feature_count"],
            response.get("summary")
        )
        
        # Save the Excel file
        with open(filepath, "wb") as f:
            f.write(excel_content)
        
        # Return the file path for downloading
        download_url = f"/static/{filename}"
        return {"download_url": download_url, "filename": filename}
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Excel file creation error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Excel generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "API is healthy"}

@app.get("/test")
async def simple_test():
    """A simple test endpoint."""
    return {"message": "API is working"}

@app.get("/api/test-pdf")
async def test_pdf():
    """Generate a simple test PDF to verify PDF generation works."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import io
        
        # Create a simple PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Test PDF Document", styles["Heading1"]),
            Paragraph("If you can see this, PDF generation is working.", styles["Normal"])
        ]
        doc.build(story)
        buffer.seek(0)
        
        # Return the PDF
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=test.pdf"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF generation error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.get("/api/simple-pdf")
async def simple_pdf_download():
    """Generate a simple PDF without any text processing."""
    try:
        # Generate a simple PDF with sample data
        sample_features = ["apple", "banana", "cherry", "date", "elderberry"]
        pdf_content = generate_pdf_report(
            sorted_features=sample_features,
            processing_time=0.1234,
            feature_count=len(sample_features),
            summary="This is a sample summary text to test PDF generation functionality."
        )
        
        # Return PDF file
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=sample_report.pdf"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Simple PDF error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.get("/api/super-simple-pdf")
async def super_simple_pdf():
    """Generate the simplest possible PDF."""
    try:
        from reportlab.pdfgen import canvas
        import io
        
        # Create a buffer
        buffer = io.BytesIO()
        
        # Create a canvas
        c = canvas.Canvas(buffer)
        
        # Add text
        c.drawString(100, 750, "Super Simple PDF Test")
        c.drawString(100, 730, "If you can see this, PDF generation works at its most basic level.")
        
        # Save the PDF
        c.save()
        
        # Get the PDF content
        buffer.seek(0)
        
        # Return the PDF
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=super_simple.pdf"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Super simple PDF error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.get("/api/files/{filename}")
async def get_file(filename: str):
    """Serve a generated file directly."""
    import os
    filepath = os.path.join("static", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    # Determine content type based on file extension
    content_type = "application/octet-stream"  # Default
    if filename.endswith(".pdf"):
        content_type = "application/pdf"
    elif filename.endswith(".xlsx"):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Read the file
    with open(filepath, "rb") as f:
        content = f.read()
    
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.post("/api/direct-pdf-download")
async def direct_pdf_download(request: ProcessTextRequest):
    """Process text and return PDF directly in response."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate PDF content
        pdf_content = generate_pdf_report(
            response["sorted_features"],
            response["processing_time"],
            response["feature_count"],
            response.get("summary")
        )
        
        # Generate a filename
        import uuid
        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        
        # Return the PDF directly in the response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Direct PDF download error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.post("/api/direct-excel-download")
async def direct_excel_download(request: ProcessTextRequest):
    """Process text and return Excel directly in response."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate Excel content
        excel_content = generate_excel_report(
            response["sorted_features"],
            response["processing_time"],
            response["feature_count"],
            response.get("summary")
        )
        
        # Generate a filename
        import uuid
        filename = f"report_{uuid.uuid4().hex[:8]}.xlsx"
        
        # Return the Excel directly in the response
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Direct Excel download error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Excel generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.post("/api/simple-download")
async def simple_download(request: ProcessTextRequest):
    """A very simple file download endpoint for testing."""
    try:
        # Generate a simple text file
        content = f"""NLP Processing Results
        
Time: {time.time()}
Text: {request.text[:100] + '...' if len(request.text) > 100 else request.text}
Feature Type: {request.feature_type}
        
This is a test file to verify downloads are working.
"""
        # Return as text file
        return Response(
            content=content,
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=test_download.txt"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@app.get("/api/test-endpoint")
async def test_endpoint():
    """Simple test endpoint to verify API is accessible."""
    return {"status": "ok", "message": "API is working", "time": time.time()}

@app.post("/api/csv")
async def csv_download(request: ProcessTextRequest):
    """Generate a simple CSV file for download."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate CSV content as byte string (not StringIO)
        import csv
        import io
        
        # Use BytesIO instead of StringIO to handle binary response
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Write header
        writer.writerow(["Rank", "Feature"])
        
        # Write data
        for i, feature in enumerate(response["sorted_features"], 1):
            writer.writerow([i, feature])
        
        # Convert to string
        csv_content = buffer.getvalue()
        
        # Return as CSV
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=features.csv"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Simple CSV error: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"CSV generation error: {str(e)}\n\nDetails: {error_details}"
        )

@app.post("/api/text")
async def text_download(request: ProcessTextRequest):
    """Generate a simple text file with the sorted features."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate plain text content
        text_content = "NLP Text Processing Results\n\n"
        text_content += f"Processing Time: {response['processing_time']:.4f} seconds\n"
        text_content += f"Features Processed: {response['feature_count']}\n"
        text_content += f"Sorting Method: Optimized Radix Sort\n\n"
        
        if response.get("summary"):
            text_content += "Text Summary:\n"
            text_content += response["summary"] + "\n\n"
        
        text_content += "Sorted Features:\n"
        for i, feature in enumerate(response["sorted_features"], 1):
            text_content += f"{i}. {feature}\n"
        
        # Return as plain text
        return Response(
            content=text_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=features.txt"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation error: {str(e)}")

@app.post("/api/raw-csv")
async def raw_csv(request: ProcessTextRequest):
    """Process text and return raw CSV content."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate CSV content
        import csv
        import io
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Write header
        writer.writerow(["Rank", "Feature"])
        
        # Write data
        for i, feature in enumerate(response["sorted_features"], 1):
            writer.writerow([i, feature])
        
        # Return raw CSV as text
        csv_content = buffer.getvalue()
        
        return {"content": csv_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV generation error: {str(e)}")

@app.post("/api/raw-text")
async def raw_text(request: ProcessTextRequest):
    """Process text and return plain text results."""
    try:
        # Process the text
        response = await process_text(request)
        
        # Generate text content
        text_content = "NLP Text Processing Results\n\n"
        text_content += f"Processing Time: {response['processing_time']:.4f} seconds\n"
        text_content += f"Features Processed: {response['feature_count']}\n"
        text_content += f"Sorting Method: Optimized Radix Sort\n\n"
        
        if response.get("summary"):
            text_content += "Text Summary:\n"
            text_content += response["summary"] + "\n\n"
        
        text_content += "Sorted Features:\n"
        for i, feature in enumerate(response["sorted_features"], 1):
            text_content += f"{i}. {feature}\n"
        
        return {"content": text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation error: {str(e)}")

@app.get("/api/text-test")
async def text_test():
    """Simple endpoint to test text response."""
    return {"content": "This is a test response from the API server."}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 