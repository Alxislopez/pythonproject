#!/usr/bin/env python3
"""
NLP Text Processor with Radix Sort
This program processes text data from a dataset file and uses radix sort for efficient sorting.
"""

import argparse
import time
import re
from text_utils import preprocess_text, extract_features
from radix_sort import radix_sort_strings, radix_sort_numeric
from dataset_handler import load_dataset, save_results

def extract_numbers_from_text(text):
    """
    Extract all numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of numbers found in the text
    """
    # Find all numbers in the text
    number_strings = re.findall(r'-?\d+(?:\.\d+)?', text)
    
    # Convert to integers or floats
    numbers = []
    for num_str in number_strings:
        if '.' in num_str:
            # Handle floating point numbers by scaling
            num = float(num_str)
            # Scale to integer for radix sort
            numbers.append(int(num * 1000))
        else:
            numbers.append(int(num_str))
    
    return numbers

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process text data using radix sort')
    parser.add_argument('--input', '-i', required=True, help='Input dataset file path')
    parser.add_argument('--output', '-o', default='results.txt', help='Output file path')
    parser.add_argument('--feature', '-f', default='words', 
                        choices=['words', 'sentences', 'ngrams', 'numbers'],
                        help='Text feature to extract and sort')
    parser.add_argument('--ngram-size', '-n', type=int, default=2, help='Size of n-grams if feature is ngrams')
    parser.add_argument('--base', '-b', type=int, default=10, help='Base to use for radix sort (for numbers)')
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.input}...")
    text_data = load_dataset(args.input)
    
    # Extract and sort features
    if args.feature == 'numbers':
        # Extract numbers and sort them
        print("Extracting numbers...")
        features = extract_numbers_from_text(text_data)
        
        print(f"Sorting {len(features)} numbers using radix sort (base {args.base})...")
        start_time = time.time()
        sorted_features = radix_sort_numeric(features, base=args.base)
        end_time = time.time()
        
        # Convert back to original representation for output
        sorted_features = [str(num) if num % 1000 == 0 else f"{num/1000:.3f}" for num in sorted_features]
    else:
        # Preprocess text for other feature types
        print("Preprocessing text...")
        processed_text = preprocess_text(text_data)
        
        # Extract features
        print(f"Extracting {args.feature}...")
        if args.feature == 'ngrams':
            features = extract_features(processed_text, feature_type=args.feature, n=args.ngram_size)
        else:
            features = extract_features(processed_text, feature_type=args.feature)
        
        # Sort using radix sort
        print("Sorting features using radix sort...")
        start_time = time.time()
        sorted_features = radix_sort_strings(features)
        end_time = time.time()
    
    print(f"Sorting completed in {end_time - start_time:.4f} seconds")
    print(f"Sorted {len(sorted_features)} items")
    
    # Save results
    print(f"Saving results to {args.output}...")
    save_results(sorted_features, args.output)
    
    print("Processing complete!")

if __name__ == "__main__":
    main() 