"""
Radix Sort implementation for text data and numeric data
"""

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

def counting_sort(arr, exp, base=10):
    """
    Counting sort implementation for a specific digit position.
    
    Args:
        arr: List to sort
        exp: Current digit position (as a power of base)
        base: Number base to use
        
    Returns:
        None (sorts in-place)
    """
    n = len(arr)
    count = [0] * base
    output = [0] * n

    for i in range(n):
        index = (arr[i] // exp) % base
        count[index] += 1

    for i in range(1, base):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = (arr[i] // exp) % base
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort_numeric(arr, base=10):
    """
    Optimized radix sort implementation for numeric data.
    
    Args:
        arr: List of numbers to sort
        base: Number base to use for sorting
        
    Returns:
        Sorted list
    """
    if len(arr) == 0:
        return arr

    if len(arr) < 32:
        return insertion_sort(arr.copy())

    # Handle negative numbers
    min_val = min(arr)
    offset = 0
    if min_val < 0:
        offset = abs(min_val)
        arr = [num + offset for num in arr]

    # Perform radix sort
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort(arr, exp, base)
        exp *= base

    # Restore original values if there was an offset
    if offset > 0:
        arr = [num - offset for num in arr]

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
    # Initialize count array for all possible characters (ASCII)
    count = [0] * 256
    
    # Count occurrences of each character at the given position
    for padded, _ in arr:
        char = padded[position]
        count[ord(char)] += 1
    
    # Calculate cumulative count
    for i in range(1, 256):
        count[i] += count[i - 1]
    
    # Build the output array
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
    if len(arr) == 0:
        return arr
        
    if len(arr) < 32:
        return insertion_sort(arr.copy())
    
    # Find the maximum length string
    max_length = 0
    for item in arr:
        max_length = max(max_length, len(item))
    
    # Pad strings to make them equal length
    # This simplifies the sorting process
    padded_arr = [(s.ljust(max_length), s) for s in arr]
    
    # Perform radix sort from the rightmost character to the leftmost
    for i in range(max_length - 1, -1, -1):
        # Use counting sort for each position
        padded_arr = counting_sort_by_position(padded_arr, i)
    
    # Return the original strings in sorted order
    return [original for _, original in padded_arr] 