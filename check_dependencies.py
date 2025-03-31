import importlib
import sys

required_modules = [
    "matplotlib",
    "argparse",
    "time",
    "random",
    "re",
    "statistics"
]

missing_modules = []

for module in required_modules:
    try:
        importlib.import_module(module)
        print(f"✓ {module} is installed")
    except ImportError:
        missing_modules.append(module)
        print(f"✗ {module} is NOT installed")

if missing_modules:
    print("\nMissing modules. Install them with:")
    print(f"pip install {' '.join(missing_modules)}")
    sys.exit(1)
else:
    print("\nAll required modules are installed!") 