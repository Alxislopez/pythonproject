import os
import sys

if __name__ == "__main__":
    # Build the command
    cmd = "python nlp_text_processor.py --input sample_dataset.txt --output sorted_numbers.txt --feature numbers"
    
    # Run the command
    exit_code = os.system(cmd)
    
    # Check if it ran successfully
    if exit_code == 0:
        print("Program ran successfully!")
    else:
        print(f"Program failed with exit code {exit_code}") 