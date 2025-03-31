import os
import sys

required_files = [
    "nlp_text_processor.py",
    "radix_sort.py",
    "text_utils.py",
    "dataset_handler.py",
    "sample_dataset.txt"
]

current_dir = os.path.dirname(os.path.abspath(__file__))

missing_files = []

for file in required_files:
    file_path = os.path.join(current_dir, file)
    if os.path.exists(file_path):
        print(f"✓ {file} exists")
    else:
        missing_files.append(file)
        print(f"✗ {file} does NOT exist")

if missing_files:
    print("\nMissing files. Please create them.")
    sys.exit(1)
else:
    print("\nAll required files exist!") 