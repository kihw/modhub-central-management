#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Union, List

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

def is_tool_available(command: str) -> bool:
    if not command:
        return False
    try:
        subprocess.run(
            [command.split()[0], "--version"],
            capture_output=True,
            check=False,
            shell=False
        )
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def run_command(
    command: Union[str, List[str]],
    cwd: Optional[Path] = None,
    env: Optional[Dict] = None
) -> bool:
    try:
        cmd_list = command.split() if isinstance(command, str) else command
        result = subprocess.run(
            cmd_list,
            cwd=cwd,
            env=env or os.environ.copy(),
            check=True,
            text=True,
            capture_output=True,
            shell=False
        )
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\nError: {e.stderr}")
        return False

def setup_environment() -> Dict:
    env = os.environ.copy()
    if platform.system() == "Windows":
        env["npm_config_prefix"] = str(ROOT_DIR / "npm-global")
    return env

def install_backend_dependencies() -> bool:
    print("\n===== Installing Backend Dependencies =====")
    if not is_tool_available("pip"):
        print("pip not found in system PATH")
        return False
    
    venv_dir = BACKEND_DIR / "venv"
    if not venv_dir.exists():
        if not run_command([sys.executable, "-m", "venv", str(venv_dir)]):
            return False

    pip_path = venv_dir / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
    requirements_file = BACKEND_DIR / "requirements.txt"
    
    return run_command([
        str(pip_path),
        "install",
        "-r" if requirements_file.exists() else "fastapi",
        str(requirements_file) if requirements_file.exists() else "uvicorn"
    ])

def install_frontend_dependencies() -> bool:
    print("\n===== Installing Frontend Dependencies =====")
    if not is_tool_available("npm"):
        print("npm not found in system PATH")
        return False
    return run_command(["npm", "install"], cwd=FRONTEND_DIR, env=setup_environment())

def build_frontend() -> bool:
    print("\n===== Building Frontend =====")
    return run_command(["npm", "run", "build"], cwd=FRONTEND_DIR, env=setup_environment())

def prepare_distribution() -> bool:
    print("\n===== Preparing Distribution =====")
    try:
        DIST_DIR.mkdir(exist_ok=True)
        
        frontend_build_dir = FRONTEND_DIR / "build"
        if frontend_build_dir.exists():
            dist_frontend = DIST_DIR / "frontend"
            shutil.rmtree(dist_frontend, ignore_errors=True)
            shutil.copytree(frontend_build_dir, dist_frontend)
        
        backend_dist = DIST_DIR / "backend"
        backend_dist.mkdir(exist_ok=True)
        
        essential_files = ["main.py", "requirements.txt"]
        for file in essential_files:
            src_file = BACKEND_DIR / file
            if src_file.exists():
                shutil.copy2(src_file, backend_dist / file)
        
        for item in BACKEND_DIR.glob("*.py"):
            if item.name not in essential_files:
                shutil.copy2(item, backend_dist / item.name)
        
        api_dir = BACKEND_DIR / "api"
        if api_dir.exists():
            shutil.copytree(api_dir, backend_dist / "api", dirs_exist_ok=True)
        
        return True
    except Exception as e:
        print(f"Error during distribution preparation: {e}")
        return False

def package_electron_app() -> bool:
    print("\n===== Packaging Electron Application =====")
    if not is_tool_available("npm"):
        return False
        
    package_json_path = FRONTEND_DIR / "package.json"
    if not package_json_path.exists():
        print("package.json not found")
        return False
        
    if not run_command(["npm", "run", "electron:build"], cwd=FRONTEND_DIR, env=setup_environment()):
        return False
        
    electron_dist = FRONTEND_DIR / "dist"
    if electron_dist.exists():
        dist_electron = DIST_DIR / "electron-dist"
        shutil.rmtree(dist_electron, ignore_errors=True)
        shutil.copytree(electron_dist, dist_electron)
    return True

def main() -> int:
    if not all([
        install_backend_dependencies(),
        install_frontend_dependencies(),
        build_frontend(),
        prepare_distribution()
    ]):
        return 1
        
    if input("Package Electron application? (y/n): ").lower().strip() == 'y':
        if not package_electron_app():
            return 1
            
    print(f"\nBuild completed successfully. Distribution files available in: {DIST_DIR}")
    return 0

if __name__ == "__main__":
    sys.exit(main())