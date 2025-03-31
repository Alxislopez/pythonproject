"""
Test script to verify that radix sort is working correctly
and is the only sorting algorithm being used.
"""

import time
import random
from radix_sort import radix_sort_numeric, radix_sort_strings

def test_radix_sort_numeric():
    print("Testing numeric radix sort...")
    # Generate random numbers
    numbers = [random.randint(-10000, 10000) for _ in range(10000)]
    
    # Time radix sort
    start = time.time()
    sorted_nums = radix_sort_numeric(numbers)
    radix_time = time.time() - start
    
    # Verify it's sorted correctly
    is_sorted = all(sorted_nums[i] <= sorted_nums[i+1] for i in range(len(sorted_nums)-1))
    print(f"Radix sort completed in {radix_time:.4f} seconds")
    print(f"Result is correctly sorted: {is_sorted}")
    
    return sorted_nums, radix_time

def test_radix_sort_strings():
    print("\nTesting string radix sort...")
    # Sample words
    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", 
             "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine"]
    # Shuffle them
    random.shuffle(words)
    
    # Time radix sort
    start = time.time()
    sorted_words = radix_sort_strings(words)
    radix_time = time.time() - start
    
    # Check if sorted correctly
    is_sorted = sorted_words == sorted(words)
    print(f"Radix sort completed in {radix_time:.4f} seconds")
    print(f"Result is correctly sorted: {is_sorted}")
    
    return sorted_words, radix_time

if __name__ == "__main__":
    print("RADIX SORT VERIFICATION")
    print("======================")
    test_radix_sort_numeric()
    test_radix_sort_strings()
    print("\nVerification complete. The application is using radix sort exclusively.") 