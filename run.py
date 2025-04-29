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
import signal
from pathlib import Path
import requests
from requests.exceptions import RequestException

# Define paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Global processes
processes = []
stop_event = threading.Event()

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
        
        # Create new env with PATH if not provided
        if env is None:
            env = os.environ.copy()
        
        # Determine appropriate shell parameter based on platform
        use_shell = True
        
        process = subprocess.Popen(
            cmd_str, 
            cwd=cwd, 
            env=env, 
            shell=use_shell, 
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=text
        )
        return process
    except Exception as e:
        print(f"Error executing command: {cmd_str}")
        print(f"Error details: {e}")
        return None

def check_backend_health():
    """Check if backend is up and running."""
    try:
        response = requests.get("http://localhost:8668/api/status", timeout=2)
        return response.status_code == 200
    except RequestException:
        return False

def setup_backend_environment():
    """Prepare the backend virtual environment."""
    venv_dir = BACKEND_DIR / "venv"
    
    # Determine Python executable in the virtual environment
    if platform.system() == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        python_path = venv_dir / "bin" / "python"
        pip_path = venv_dir / "bin" / "pip"
    
    # Verify virtual environment exists
    if not venv_dir.exists():
        print("Creating virtual environment...")
        create_venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
        process = run_command(create_venv_cmd)
        if process is None or process.wait() != 0:
            print("Failed to create virtual environment")
            return None, None
    
    # Install package to verify environment
    print("Installing required packages...")
    install_cmd = [str(pip_path), "install", "-U", "pip", "setuptools", "wheel"]
    process = run_command(install_cmd)
    if process is None or process.wait() != 0:
        print("Failed to upgrade pip in virtual environment")
    
    return python_path, pip_path

def run_backend():
    """Run the backend FastAPI server."""
    global processes
    
    if platform.system() == "Windows":
        backend_cmd = [str(BACKEND_DIR / "venv" / "Scripts" / "python.exe"), "main.py"]
    else:
        backend_cmd = [str(BACKEND_DIR / "venv" / "bin" / "python"), "main.py"]
    
    print("Starting backend server...")
    backend_process = run_command(backend_cmd, cwd=BACKEND_DIR)
    
    if backend_process is None:
        print("Failed to start backend server")
        return None
    
    processes.append(backend_process)
    return backend_process

def run_frontend():
    """Run the frontend development server."""
    global processes
    
    # Check if node_modules exist, if not install
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies first...")
        install_process = run_command("npm install", cwd=FRONTEND_DIR)
        if install_process:
            install_process.wait()
    
    print("Starting frontend development server...")
    if platform.system() == "Windows":
        frontend_cmd = "npm start"
    else:
        frontend_cmd = "npm start"
    
    frontend_process = run_command(frontend_cmd, cwd=FRONTEND_DIR)
    
    if frontend_process is None:
        print("Failed to start frontend server")
        return None
    
    processes.append(frontend_process)
    return frontend_process

def tail_process_output(process, prefix=""):
    """Continuously read and print process output."""
    if process is None:
        return
    
    try:
        while not stop_event.is_set():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"{prefix}{output.strip()}")
            if stop_event.is_set():
                break
    except Exception as e:
        print(f"Error reading process output: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals."""
    print("\nShutting down ModHub Central services...")
    stop_event.set()
    
    for process in processes:
        try:
            if platform.system() == "Windows":
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            print(f"Terminated process PID: {process.pid}")
        except:
            pass
    
    # Give processes a moment to shut down
    time.sleep(1)
    
    # Force kill any remaining processes
    for process in processes:
        if process.poll() is None:  # Process still running
            if platform.system() == "Windows":
                process.kill()
            else:
                process.send_signal(signal.SIGKILL)
    
    sys.exit(0)

def main():
    """Main run function to start backend and frontend."""
    global processes
    
    # Setup signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting ModHub Central services...")
    
    # Check for required tools
    if not is_tool_available("npm"):
        print("Error: npm is not installed or not in PATH")
        print("Please install Node.js and npm: https://nodejs.org/")
        return 1
    
    # Setup backend environment
    python_path, pip_path = setup_backend_environment()
    if python_path is None or pip_path is None:
        print("Failed to setup backend environment")
        return 1
    
    # Install dependencies
    print("\n===== Installing Backend Dependencies =====")
    install_cmd = [str(pip_path), "install", "-r", str(BACKEND_DIR / "requirements.txt")]
    install_process = run_command(install_cmd)
    if install_process is None or install_process.wait() != 0:
        print("Failed to install backend dependencies")
        return 1
    
    # Run backend
    print("\n===== Starting Backend Service =====")
    backend_process = run_backend()
    if backend_process is None:
        return 1
    
    # Wait for backend to be ready
    print("Waiting for backend to start...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_backend_health():
            print("Backend started successfully!")
            break
        if attempt == max_attempts - 1:
            print("Backend failed to start within the expected time.")
            signal_handler(None, None)
            return 1
        time.sleep(1)
        print(f"Waiting for backend to start... ({attempt+1}/{max_attempts})")
    
    # Run frontend
    print("\n===== Starting Frontend Service =====")
    frontend_process = run_frontend()
    if frontend_process is None:
        signal_handler(None, None)
        return 1
    
    # Create threads to read process outputs
    backend_thread = threading.Thread(
        target=tail_process_output, 
        args=(backend_process, "[BACKEND] ")
    )
    frontend_thread = threading.Thread(
        target=tail_process_output, 
        args=(frontend_process, "[FRONTEND] ")
    )
    
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    backend_thread.start()
    frontend_thread.start()
    
    print("\n===== ModHub Central is now running =====")
    print("Backend: http://localhost:8668")
    print("Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep the main thread running
        while True:
            if backend_process.poll() is not None:
                print("Backend process has terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend process has terminated unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())