#!/usr/bin/env python3

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
from typing import Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_PORT = 8668
FRONTEND_PORT = 3000

processes = []
stop_event = threading.Event()

def is_tool_available(command: str) -> bool:
    try:
        print(f"Checking for {command} availability...")
        # On Windows, try both the command and command.cmd
        if platform.system() == "Windows" and command == "npm":
            try:
                result = subprocess.run(["npm.cmd", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                if result.returncode == 0:
                    print(f"Found npm.cmd: {result.stdout.strip()}")
                    return True
            except Exception as e:
                print(f"Exception checking for npm.cmd: {e}")
                
        # Try the original command
        result = subprocess.run([command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception checking for {command}: {e}")
        return False
    
def run_command(command, cwd: Optional[Path] = None, env: Optional[dict] = None, capture_output: bool = False, text: bool = True) -> Optional[subprocess.Popen]:
    try:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"Running: {cmd_str}")
        
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        return subprocess.Popen(
            cmd_str, 
            cwd=str(cwd) if cwd else None, 
            env=process_env,
            shell=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=text,
            encoding='utf-8' if text else None,
            bufsize=1
        )
    except Exception as e:
        print(f"Error executing command: {cmd_str}\nDetails: {e}")
        return None

def check_backend_health() -> bool:
    try:
        response = requests.get(f"http://localhost:{BACKEND_PORT}/api/status", timeout=2)
        return response.status_code == 200
    except RequestException:
        return False

def setup_backend_environment() -> Tuple[Optional[Path], Optional[Path]]:
    venv_dir = BACKEND_DIR / "venv"
    is_windows = platform.system() == "Windows"
    python_path = venv_dir / ("Scripts" if is_windows else "bin") / ("python.exe" if is_windows else "python")
    pip_path = venv_dir / ("Scripts" if is_windows else "bin") / ("pip.exe" if is_windows else "pip")
    
    if not venv_dir.exists():
        process = run_command([sys.executable, "-m", "venv", str(venv_dir)])
        if not process or process.wait() != 0:
            return None, None
    
    process = run_command([str(python_path), "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"])
    if not process or process.wait() != 0:
        print("Failed to upgrade pip")
        return None, None
    
    return python_path, pip_path

def run_backend() -> Optional[subprocess.Popen]:
    python_exe = "Scripts/python.exe" if platform.system() == "Windows" else "bin/python"
    backend_cmd = [str(BACKEND_DIR / "venv" / python_exe), "main.py"]
    
    backend_process = run_command(backend_cmd, cwd=BACKEND_DIR, capture_output=True)
    if backend_process:
        processes.append(backend_process)
    return backend_process

def run_frontend() -> Optional[subprocess.Popen]:
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        install_process = run_command("npm install", cwd=FRONTEND_DIR)
        if install_process and install_process.wait() != 0:
            return None
    
    frontend_process = run_command("npm start", cwd=FRONTEND_DIR, capture_output=True)
    if frontend_process:
        processes.append(frontend_process)
    return frontend_process

def tail_process_output(process: subprocess.Popen, prefix: str = "") -> None:
    if not process or not process.stdout:
        return
    
    for line in iter(process.stdout.readline, ''):
        if stop_event.is_set():
            break
        if line:
            print(f"{prefix}{line.strip()}")

def signal_handler(sig, frame) -> None:
    print("\nShutting down ModHub Central services...")
    stop_event.set()
    
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            process.kill()
    
    sys.exit(0)

def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not is_tool_available("npm"):
        print("Error: npm is not installed")
        return 1
    
    python_path, pip_path = setup_backend_environment()
    if not python_path or not pip_path:
        return 1
    
    requirements_process = run_command([str(pip_path), "install", "-r", str(BACKEND_DIR / "requirements.txt")])
    if not requirements_process or requirements_process.wait() != 0:
        return 1
    
    backend_process = run_backend()
    if not backend_process:
        return 1
    
    for attempt in range(30):
        if check_backend_health():
            print("Backend started successfully!")
            break
        if attempt == 29:
            print("Backend failed to start")
            signal_handler(None, None)
            return 1
        time.sleep(1)
        print(f"Waiting for backend... ({attempt+1}/30)")
    
    frontend_process = run_frontend()
    if not frontend_process:
        signal_handler(None, None)
        return 1
    
    backend_thread = threading.Thread(target=tail_process_output, args=(backend_process, "[BACKEND] "))
    frontend_thread = threading.Thread(target=tail_process_output, args=(frontend_process, "[FRONTEND] "))
    
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    backend_thread.start()
    frontend_thread.start()
    
    print(f"\nModHub Central running:")
    print(f"Backend: http://localhost:{BACKEND_PORT}")
    print(f"Frontend: http://localhost:{FRONTEND_PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        while not stop_event.is_set():
            if any(p.poll() is not None for p in processes):
                print("A process has terminated unexpectedly")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())