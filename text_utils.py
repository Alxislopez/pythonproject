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
    Create a simple summary by taking the most important sentences.
    This is a basic extractive summarization.
    
    Args:
        text: The text to summarize
        ratio: Proportion of original text to keep (0.0-1.0)
    
    Returns:
        A summary of the text
    """
    import re
    from collections import Counter
    
    if not text or ratio >= 1.0:
        return text
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= 3:
        return text  # Text is already short enough
    
    # Count word frequency
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    
    # Score each sentence
    sentence_scores = []
    for sentence in sentences:
        score = 0
        for word in re.findall(r'\w+', sentence.lower()):
            score += word_freq[word]
        sentence_scores.append((score, sentence))
    
    # Sort by score and select top sentences
    sorted_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)
    num_sentences = max(1, int(len(sentences) * ratio))
    top_sentences = sorted_sentences[:num_sentences]
    
    # Reorder sentences to maintain original flow
    original_order = []
    for _, sentence in top_sentences:
        original_order.append((sentences.index(sentence), sentence))
    
    original_order.sort()  # Sort by position in original text
    summary = ' '.join([sentence for _, sentence in original_order])
    
    return summary 