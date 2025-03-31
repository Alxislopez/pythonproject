"""
Text processing utilities for NLP
"""

import re
import string
from collections import Counter
from summa import summarizer as text_rank_summarizer
import nltk
from nltk.tokenize import sent_tokenize

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing punctuation,
    and normalizing whitespace.
    
    Args:
        text: Input text string
        
    Returns:
        Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

import re  # Ensure regex is imported

def extract_features(text, feature_type='words', n=2):
    """
    Extract features from text.

    Args:
        text: Preprocessed text
        feature_type: Type of features to extract ('words', 'sentences', 'numbers', or 'ngrams')
        n: Size of n-grams if feature_type is 'ngrams'

    Returns:
        List of extracted features
    """
    features = []  # Ensure features is always initialized

    if feature_type == 'words':
        # Split text into words
        features = text.split()

    elif feature_type == 'sentences':
        # Split text into sentences
        features = re.split(r'[.!?]+', text)
        features = [s.strip() for s in features if s.strip()]

    elif feature_type == 'numbers':
        # Extract numbers using regex
        features = re.findall(r'\d+', text)  # Finds all numeric sequences

    elif feature_type == 'ngrams':
        # Generate n-grams
        words = text.split()
        features = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]

    else:
        raise ValueError(f"Unknown feature_type: {feature_type}")

    # Remove duplicates while preserving order
    unique_features = []
    seen = set()
    for feature in features:
        if feature not in seen:
            seen.add(feature)
            unique_features.append(feature)

    return unique_features

def analyze_features(features):
    """
    Analyze features to get statistics.
    
    Args:
        features: List of extracted features
        
    Returns:
        Dictionary with feature statistics
    """
    # Count frequency of each feature
    feature_counts = Counter(features)
    
    # Calculate statistics
    stats = {
        'total_features': len(features),
        'unique_features': len(feature_counts),
        'most_common': feature_counts.most_common(10)
    }
    
    return stats

def summarize_text(text, ratio=0.2):
    """
    Generate a summary of the input text.
    
    Args:
        text: Input text to summarize
        ratio: Proportion of the original text to keep (0.0 to 1.0)
        
    Returns:
        Summarized text
    """
    if not text.strip():
        return ""
    
    # Use TextRank algorithm for summarization
    try:
        summary = text_rank_summarizer.summarize(text, ratio=ratio)
        if not summary.strip():
            # Fallback to a simple extractive summary if TextRank fails
            sentences = sent_tokenize(text)
            if len(sentences) <= 3:
                return text  # Text is already short enough
            
            # Take the first sentence and approximately ratio% of the remaining ones
            num_sentences = max(2, int(len(sentences) * ratio))
            summary = " ".join(sentences[:num_sentences])
        
        return summary
    except Exception as e:
        print(f"Summarization error: {e}")
        # Simple fallback - just return the first few sentences
        sentences = sent_tokenize(text)
        num_sentences = max(1, int(len(sentences) * ratio))
        return " ".join(sentences[:num_sentences]) 