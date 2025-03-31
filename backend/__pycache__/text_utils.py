"""
Text processing utilities for NLP
"""

import re
import string
from collections import Counter

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