#!/usr/bin/env python3
"""
Run script for Microgrid Optimization Streamlit App
Usage: python run_streamlit.py
"""

import subprocess
import sys
import os

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the app.py file
    app_path = os.path.join(script_dir, "src", "app", "app.py")
    
    # Check if app.py exists
    if not os.path.exists(app_path):
        print(f"Error: Could not find app.py at {app_path}")
        print("Please make sure the file structure is correct.")
        sys.exit(1)
    
    # Run streamlit
    print("Starting Microgrid Optimization Simulator...")
    print(f"Running: streamlit run {app_path}")
    print("\nThe app will open in your browser automatically.")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()