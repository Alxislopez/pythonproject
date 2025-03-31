from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import time
import re
from typing import List, Optional
import os
from text_utils import preprocess_text, extract_features, summarize_text
from radix_sort import radix_sort_numeric, radix_sort_strings
from file_processor import extract_text_from_pdf, extract_text_from_excel, generate_pdf_report, generate_excel_report, generate_csv_report

# Remove StaticFiles import and mounting since it's not compatible with serverless
# from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ML Data Convertor API")

# Don't create static directory - serverless functions have ephemeral filesystem
# We'll use in-memory storage instead

# Configure CORS to allow requests from any origin (Vercel deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, you might want to limit this to your Vercel domain
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

# Simplified direct download endpoints for Vercel
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

@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "API is healthy"}

# Export the FastAPI app for Vercel
# Remove the if __name__ == "__main__" block as it's not needed for serverless 