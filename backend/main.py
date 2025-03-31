from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from summa import summarizer
import os
from text_utils import preprocess_text, extract_features
from radix_sort import radix_sort_strings, radix_sort_numeric

# Initialize FastAPI app
app = FastAPI()

# Ensure necessary NLTK resources are available
nltk.download('punkt')

# Directory to save processed files
RESULTS_DIR = "processed_files"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NLP Text Processor API with Radix Sort!"}

def extract_keywords(text, top_n=10):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()
    sorted_indices = tfidf_scores.argsort()[::-1]
    keywords = [feature_array[i] for i in sorted_indices[:top_n]]
    return keywords

@app.post("/process")
async def process_text(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    
    # Summarization
    summary = summarizer.summarize(text, ratio=0.3)
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Extract words and sort using radix sort
    words = extract_features(processed_text, feature_type='words')
    sorted_words = radix_sort_strings(words)
    
    # Extract numbers and sort using radix sort
    numbers = extract_features(processed_text, feature_type='numbers')
    sorted_numbers = radix_sort_numeric(numbers)
    
    # Keyword Extraction
    keywords = extract_keywords(text)
    
    # Convert results to a DataFrame and save as Excel
    filename = f"{file.filename.split('.')[0]}_processed.xlsx"
    file_path = os.path.join(RESULTS_DIR, filename)
    
    df = pd.DataFrame({
        "Sorted Words": sorted_words,
        "Sorted Numbers": sorted_numbers,
        "Keywords": keywords,
        "Summary": [summary]
    })
    df.to_excel(file_path, index=False)
    
    return {
        "summary": summary, 
        "keywords": keywords, 
        "sorted_words": sorted_words,
        "sorted_numbers": sorted_numbers,
        "download_url": f"/download/{filename}"
    }

@app.get("/download/{filename}")
def download_file(filename: str):
    file
