"""
Radix Sort implementation for text data and numeric data

This module provides the optimized radix sort algorithm used exclusively 
for all sorting operations in the NLP text processing application.

The implementation includes:
1. radix_sort_numeric - For sorting numbers with customizable base
2. radix_sort_strings - For sorting text strings efficiently
3. Helper functions for counting sort and small array optimization
"""

import math
import multiprocessing

def insertion_sort(arr):
    """
    Insertion sort implementation for small arrays.
    
    Args:
        arr: List to sort
        
    Returns:
        Sorted list
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def get_optimal_base(arr):
    """
    Calculate the optimal base for radix sort based on the maximum value.
    
    Args:
        arr: List of numbers
        
    Returns:
        Optimal base for radix sort
    """
    if not arr:
        return 10
    
    max_val = max(abs(x) for x in arr)
    if max_val == 0:
        return 10
        
    log_val = math.log2(max_val)
    optimal_base = int(2 ** min(8, max(4, math.floor(log_val / 2))))
    return min(optimal_base, 256)

def parallel_counting_sort(arr, exp, base):
    """
    Parallel counting sort implementation for a specific digit position.
    
    Args:
        arr: List to sort
        exp: Current digit position (as a power of base)
        base: Number base to use
        
    Returns:
        None (sorts in-place)
    """
    if not arr:
        return
        
    n = len(arr)
    output = [0] * n
    count = [0] * base

    try:
        num_threads = min(multiprocessing.cpu_count(), len(arr))
        chunk_size = (len(arr) + num_threads - 1) // num_threads
        chunks = [arr[i * chunk_size:(i + 1) * chunk_size] for i in range(num_threads)]

        def count_chunk(chunk, result_queue):
            local_count = [0] * base
            for num in chunk:
                index = (num // exp) % base
                local_count[index] += 1
            result_queue.put(local_count)

        result_queue = multiprocessing.Queue()
        processes = [multiprocessing.Process(target=count_chunk, args=(chunk, result_queue)) for chunk in chunks]
        for p in processes: p.start()
        for p in processes: p.join()

        while not result_queue.empty():
            local_count = result_queue.get()
            for i in range(base):
                count[i] += local_count[i]

        for i in range(1, base):
            count[i] += count[i - 1]

        for i in reversed(range(n)):
            index = (arr[i] // exp) % base
            count[index] -= 1
            output[count[index]] = arr[i]

        for i in range(n):
            arr[i] = output[i]
            
    except Exception as e:
        # Fallback to sequential counting sort if parallel processing fails
        for num in arr:
            index = (num // exp) % base
            count[index] += 1

        for i in range(1, base):
            count[i] += count[i - 1]

        for i in reversed(range(n)):
            index = (arr[i] // exp) % base
            count[index] -= 1
            output[count[index]] = arr[i]

        for i in range(n):
            arr[i] = output[i]

def radix_sort_numeric(arr):
    """
    Optimized radix sort implementation for numeric data.
    
    Args:
        arr: List of numbers to sort
        
    Returns:
        Sorted list
    """
    if not arr:
        return arr

    if len(arr) < 1000:
        return insertion_sort(arr.copy())

    base = get_optimal_base(arr)
    min_val = min(arr)
    if min_val < 0:
        arr = [num - min_val for num in arr]

    max_val = max(arr)
    exp = 1

    while max_val // exp > 0:
        parallel_counting_sort(arr, exp, base)
        exp *= base

    if min_val < 0:
        arr = [num + min_val for num in arr]

    return arr

def counting_sort_by_position(arr, position):
    """
    Counting sort implementation for a specific character position.
    
    Args:
        arr: List of (padded_string, original_string) tuples
        position: The character position to sort by
        
    Returns:
        Sorted list of (padded_string, original_string) tuples
    """
    count = [0] * 256
    for padded, _ in arr:
        char = padded[position]
        count[ord(char)] += 1

    for i in range(1, 256):
        count[i] += count[i - 1]

    output = [None] * len(arr)
    for i in range(len(arr) - 1, -1, -1):
        padded, original = arr[i]
        char = padded[position]
        output[count[ord(char)] - 1] = (padded, original)
        count[ord(char)] -= 1

    return output

def radix_sort_strings(arr):
    """
    Radix sort implementation for strings.
    
    Args:
        arr: List of strings to sort
        
    Returns:
        Sorted list of strings
    """
    if not arr:
        return arr

    if len(arr) < 32:
        return insertion_sort(arr.copy())

    max_length = max(len(s) for s in arr)
    padded_arr = [(s.ljust(max_length), s) for s in arr]

    for i in range(max_length - 1, -1, -1):
        padded_arr = counting_sort_by_position(padded_arr, i)

    return [original for _, original in padded_arr]
