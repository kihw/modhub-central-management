#!/usr/bin/env python3
"""
Build script for automated building of both backend and frontend components.
This script handles dependency installation, compilation, and preparation for distribution.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Define paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"


def is_tool_available(command):
    """Check if a command-line tool is available."""
    try:
        subprocess.run(
            [command, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def run_command(command, cwd=None, env=None):
    """Run a shell command and handle errors."""
    try:
        print(f"Running: {' '.join(command)}")
        process = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.stdout:
            print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Error details: {e.stderr}")
        return False


def setup_environment():
    """Prepare the environment variables for the build process."""
    env = os.environ.copy()
    
    # Ensure npm uses appropriate config for the platform
    if platform.system() == "Windows":
        env["npm_config_prefix"] = str(ROOT_DIR / "npm-global")
    
    return env


def install_backend_dependencies():
    """Install Python dependencies for the backend."""
    print("\n===== Installing Backend Dependencies =====")
    
    if not is_tool_available("pip"):
        print("Error: pip is not installed or not in PATH")
        return False
    
    # Create virtual environment if it doesn't exist
    venv_dir = BACKEND_DIR / "venv"
    
    if not venv_dir.exists():
        print("Creating virtual environment...")
        if platform.system() == "Windows":
            venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
        else:
            venv_cmd = ["python3", "-m", "venv", str(venv_dir)]
        
        if not run_command(venv_cmd):
            return False
    
    # Determine pip path based on the platform
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    # Install dependencies from requirements.txt if it exists
    requirements_file = BACKEND_DIR / "requirements.txt"
    if requirements_file.exists():
        if not run_command([str(pip_path), "install", "-r", str(requirements_file)]):
            return False
    else:
        # If requirements.txt doesn't exist, install FastAPI and uvicorn directly
        if not run_command([str(pip_path), "install", "fastapi", "uvicorn"]):
            return False
    
    return True


def install_frontend_dependencies():
    """Install npm dependencies for the frontend."""
    print("\n===== Installing Frontend Dependencies =====")
    
    if not is_tool_available("npm"):
        print("Error: npm is not installed or not in PATH")
        return False
    
    env = setup_environment()
    
    return run_command(["npm", "install"], cwd=FRONTEND_DIR, env=env)


def build_frontend():
    """Build the frontend application."""
    print("\n===== Building Frontend =====")
    env = setup_environment()
    
    # Run npm build script
    if not run_command(["npm", "run", "build"], cwd=FRONTEND_DIR, env=env):
        return False
    
    return True


def prepare_distribution():
    """Prepare the project for distribution."""
    print("\n===== Preparing Distribution =====")
    
    # Create dist directory if it doesn't exist
    DIST_DIR.mkdir(exist_ok=True)
    
    # Copy frontend build to dist
    frontend_build_dir = FRONTEND_DIR / "build"
    if frontend_build_dir.exists():
        print(f"Copying frontend build from {frontend_build_dir} to {DIST_DIR / 'frontend'}")
        if (DIST_DIR / "frontend").exists():
            shutil.rmtree(DIST_DIR / "frontend")
        shutil.copytree(frontend_build_dir, DIST_DIR / "frontend")
    else:
        print(f"Warning: Frontend build directory {frontend_build_dir} does not exist")
    
    # Copy necessary backend files
    backend_dist = DIST_DIR / "backend"
    backend_dist.mkdir(exist_ok=True)
    
    # Copy main backend files (adjust as needed)
    for file in ["main.py", "requirements.txt"]:
        src_file = BACKEND_DIR / file
        if src_file.exists():
            shutil.copy(src_file, backend_dist / file)
    
    # Copy backend modules
    for item in BACKEND_DIR.glob("*.py"):
        if item.name != "main.py":  # Already copied above
            shutil.copy(item, backend_dist / item.name)
    
    # Copy any API modules
    api_dir = BACKEND_DIR / "api"
    if api_dir.exists():
        shutil.copytree(api_dir, backend_dist / "api", dirs_exist_ok=True)
    
    print(f"Distribution prepared in {DIST_DIR}")
    return True


def package_electron_app():
    """Package the Electron application (optional)."""
    print("\n===== Packaging Electron Application =====")
    
    if not is_tool_available("npm"):
        print("Error: npm is not installed or not in PATH")
        return False
    
    env = setup_environment()
    
    # Check if electron-builder is installed
    package_json_path = FRONTEND_DIR / "package.json"
    if not package_json_path.exists():
        print(f"Error: package.json not found at {package_json_path}")
        return False
    
    # Run electron-builder
    if not run_command(["npm", "run", "electron:build"], cwd=FRONTEND_DIR, env=env):
        print("Warning: Electron packaging failed. Make sure you have a proper electron:build script in package.json")
        return False
    
    # Copy packaged app to dist directory if it exists
    electron_dist = FRONTEND_DIR / "dist"
    if electron_dist.exists():
        print(f"Copying Electron packages from {electron_dist} to {DIST_DIR / 'electron-dist'}")
        if (DIST_DIR / "electron-dist").exists():
            shutil.rmtree(DIST_DIR / "electron-dist")
        shutil.copytree(electron_dist, DIST_DIR / "electron-dist")
    
    return True


def main():
    """Main build function."""
    print("Starting build process...")
    
    if not install_backend_dependencies():
        print("Failed to install backend dependencies.")
        return 1
    
    if not install_frontend_dependencies():
        print("Failed to install frontend dependencies.")
        return 1
    
    if not build_frontend():
        print("Failed to build frontend.")
        return 1
    
    if not prepare_distribution():
        print("Failed to prepare distribution.")
        return 1
    
    # Optional: Package Electron app
    package_electron = input("Do you want to package the Electron application? (y/n): ").lower() == 'y'
    if package_electron and not package_electron_app():
        print("Failed to package Electron application.")
        return 1
    
    print("\n===== Build Completed Successfully =====")
    print(f"Distribution files are available in: {DIST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())