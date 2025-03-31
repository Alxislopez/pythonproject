import subprocess
import os
import sys
import webbrowser
import time
import threading

def run_backend():
    """Run the FastAPI backend server"""
    print("Starting backend server...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "api.py"])

def run_frontend():
    """Run the React frontend dev server"""
    print("Starting frontend development server...")
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"))
    if os.name == 'nt':  # Windows
        subprocess.run(["npm.cmd", "start"])
    else:  # Linux/Mac
        subprocess.run(["npm", "start"])

def open_browser():
    """Open the browser after a delay to let servers start"""
    time.sleep(5)  # Wait for servers to start
    webbrowser.open("http://localhost:3000")

if __name__ == "__main__":
    # Check if frontend dependencies are installed
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("Installing frontend dependencies...")
        os.chdir(frontend_dir)
        if os.name == 'nt':  # Windows
            subprocess.run(["npm.cmd", "install"])
        else:  # Linux/Mac
            subprocess.run(["npm", "install"])
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start browser after a delay
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run frontend (this will block until frontend is closed)
    run_frontend() 