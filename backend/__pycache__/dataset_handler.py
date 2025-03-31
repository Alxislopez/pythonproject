"""
Dataset handling utilities for loading and saving text data
"""

def load_dataset(file_path):
    """
    Load text data from a dataset file.
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        Text content as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return ""

def save_results(results, file_path):
    """
    Save processed results to a file.
    
    Args:
        results: List of processed and sorted features
        file_path: Path to save the results
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for i, item in enumerate(results, 1):
                file.write(f"{i}. {item}\n")
    except Exception as e:
        print(f"Error saving results: {e}") 