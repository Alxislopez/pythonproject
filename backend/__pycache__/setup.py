import os
import sys
import subprocess

def check_python_version():
    print("Checking Python version...")
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher is required")
        sys.exit(1)
    print(f"Using Python {sys.version}")

def install_dependencies():
    print("Installing dependencies...")
    dependencies = ["matplotlib", "argparse"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        sys.exit(1)

def check_project_structure():
    print("Checking project structure...")
    project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pythonproject")
    
    required_files = [
        "nlp_text_processor.py",
        "radix_sort.py",
        "text_utils.py",
        "dataset_handler.py",
        "sample_dataset.txt"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(project_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
        sys.exit(1)
    
    print("Project structure looks good")

def main():
    print("Setting up NLP Project...")
    check_python_version()
    install_dependencies()
    check_project_structure()
    print("Setup complete! You can now run the project.")

if __name__ == "__main__":
    main() 