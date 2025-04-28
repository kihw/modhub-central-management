#!/usr/bin/env python3
"""
Run script for launching ModHub Central backend and frontend.
Supports concurrent execution of backend and frontend services.
"""

import os
import sys
import platform
import subprocess
import threading
import time
from pathlib import Path

# Define paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def is_tool_available(command):
    """Check if a command-line tool is available."""
    try:
        subprocess.run(
            [command, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            shell=True
        )
        return True
    except FileNotFoundError:
        return False

def run_command(command, cwd=None, env=None, capture_output=False, text=True):
    """Run a shell command and handle errors."""
    try:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"Running: {cmd_str}")
        
        # Determine appropriate shell parameter based on platform
        use_shell = platform.system() != "Windows"
        
        process = subprocess.Popen(
            cmd_str, 
            cwd=cwd, 
            env=env, 
            shell=True, 
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=text
        )
        return process
    except Exception as e:
        print(f"Error executing command: {cmd_str}")
        print(f"Error details: {e}")
        return None

def setup_backend_environment():
    """Prepare the backend virtual environment."""
    venv_dir = BACKEND_DIR / "venv"
    
    # Determine Python executable in the virtual environment
    if platform.system() == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
        uvicorn_path = venv_dir / "Scripts" / "uvicorn.exe"
    else:
        python_path = venv_dir / "bin" / "python"
        uvicorn_path = venv_dir / "bin" / "uvicorn"
    
    # Verify virtual environment exists
    if not venv_dir.exists():
        print("Creating virtual environment...")
        create_venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
        if run_command(create_venv_cmd) is None:
            print("Failed to create virtual environment")
            return None, None
    
    return python_path, uvicorn_path

def run_backend(uvicorn_path):
    """Run the backend FastAPI server."""
    backend_cmd = [
        str(uvicorn_path), 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8668", 
        "--reload"
    ]
    backend_process = run_command(backend_cmd, cwd=BACKEND_DIR)
    return backend_process

def run_frontend():
    """Run the frontend development server."""
    frontend_process = run_command("npm start", cwd=FRONTEND_DIR)
    return frontend_process

def tail_process_output(process, prefix=""):
    """Continuously read and print process output."""
    if process is None:
        return
    
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"{prefix}{output.strip()}")
    except Exception as e:
        print(f"Error reading process output: {e}")

def main():
    """Main run function to start backend and frontend."""
    print("Starting ModHub Central services...")
    
    # Check for required tools
    if not is_tool_available("npm"):
        print("Error: npm is not installed or not in PATH")
        return 1
    
    if not is_tool_available("pip"):
        print("Error: pip is not installed or not in PATH")
        return 1
    
    # Setup backend environment
    python_path, uvicorn_path = setup_backend_environment()
    if python_path is None or uvicorn_path is None:
        print("Failed to setup backend environment")
        return 1
    
    # Install dependencies
    print("\n===== Installing Backend Dependencies =====")
    install_cmd = [str(python_path), "-m", "pip", "install", "-r", str(BACKEND_DIR / "requirements.txt")]
    if run_command(install_cmd) is None:
        print("Failed to install backend dependencies")
        return 1
    
    print("\n===== Installing Frontend Dependencies =====")
    if run_command("npm install", cwd=FRONTEND_DIR) is None:
        print("Failed to install frontend dependencies")
        return 1
    
    # Run backend
    print("\n===== Starting Backend Service =====")
    backend_process = run_backend(uvicorn_path)
    
    # Give backend a moment to start
    time.sleep(2)
    
    # Run frontend
    print("\n===== Starting Frontend Service =====")
    frontend_process = run_frontend()
    
    # Create threads to read process outputs
    backend_thread = threading.Thread(
        target=tail_process_output, 
        args=(backend_process, "[BACKEND] ")
    )
    frontend_thread = threading.Thread(
        target=tail_process_output, 
        args=(frontend_process, "[FRONTEND] ")
    )
    
    backend_thread.start()
    frontend_thread.start()
    
    try:
        # Wait for processes to complete
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping ModHub Central services...")
        backend_process.terminate()
        frontend_process.terminate()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())