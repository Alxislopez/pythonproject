from fastapi import FastAPI, UploadFile, File
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from summa import summarizer
import os

# Initialize FastAPI app
app = FastAPI()

# Ensure necessary NLTK resources are available
nltk.download('punkt')


@app.get("/")
def read_root():
    return {"message": "Welcome to the NLP Text Processor API!"}
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
    
    # Keyword Extraction
    keywords = extract_keywords(text)
    
    # Convert results to a DataFrame and save as Excel
    output_file = "results.xlsx"
    df = pd.DataFrame({"Keywords": keywords})
    df.to_excel(output_file, index=False)
    
    return {"summary": summary, "keywords": keywords, "file_saved": output_file}
