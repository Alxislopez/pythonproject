"""
Patch for text_utils.py that works around the punkt_tab requirement
"""

def apply_patch():
    import os
    
    # Get the path to text_utils.py in the same directory as this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    text_utils_path = os.path.join(current_dir, "text_utils.py")
    
    # Read the content of text_utils.py
    with open(text_utils_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we need to patch
    if "punkt_tab" in content:
        # We need to patch - make backup first
        backup_path = os.path.join(current_dir, "text_utils.py.backup")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup at {backup_path}")
        
        # Replace punkt_tab references
        patched_content = content.replace("punkt_tab", "punkt")
        
        # Write patched content
        with open(text_utils_path, 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print("Applied patch to text_utils.py to fix punkt_tab requirement")
        return True
    
    print("No need to patch text_utils.py")
    return False

if __name__ == "__main__":
    apply_patch() 