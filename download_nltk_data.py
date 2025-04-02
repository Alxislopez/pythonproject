"""
Download required NLTK data for the ML Data Convertor application.
"""
import nltk
import sys

def download_nltk_resources():
    """Download all required NLTK resources."""
    print("Downloading NLTK resources...")
    try:
        # Download the punkt tokenizer (needed for sentence tokenization)
        nltk.download('punkt')
        print("✓ Successfully downloaded NLTK punkt tokenizer")
        
        # Specifically download punkt_tab resource
        try:
            nltk.download('punkt_tab')
            print("✓ Successfully downloaded NLTK punkt_tab resource")
        except:
            print("Note: punkt_tab couldn't be downloaded directly, but may be included in punkt")
        
        # Add any other resources you might need here
        
        return True
    except Exception as e:
        print(f"✗ Error downloading NLTK resources: {e}")
        return False

if __name__ == "__main__":
    success = download_nltk_resources()
    if success:
        print("All NLTK resources downloaded successfully!")
        sys.exit(0)
    else:
        print("Failed to download all required NLTK resources.")
        sys.exit(1) 