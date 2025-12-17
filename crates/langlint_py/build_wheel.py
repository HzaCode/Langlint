#!/usr/bin/env python
"""Build wheel with maturin and fix the structure"""
import subprocess
import zipfile
import os
import tempfile
import shutil

def build_wheel():
    # 1. Build with maturin
    subprocess.run(["maturin", "build", "--release", "--interpreter", "py"], check=True)
    
    # 2. Find the wheel file
    wheel_dir = "../../target/wheels"
    wheel_files = [f for f in os.listdir(wheel_dir) if f.startswith("langlint-") and f.endswith(".whl")]
    if not wheel_files:
        raise Exception("No wheel file found")
    
    wheel_path = os.path.join(wheel_dir, wheel_files[0])
    
    # 3. Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract wheel
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Remove the langlint_py directory if it exists
        langlint_py_dir = os.path.join(temp_dir, "langlint_py")
        if os.path.exists(langlint_py_dir) and os.path.isdir(langlint_py_dir):
            # Move the .pyd file to root
            for file in os.listdir(langlint_py_dir):
                if file.endswith('.pyd'):
                    shutil.move(os.path.join(langlint_py_dir, file), temp_dir)
            # Remove the directory
            shutil.rmtree(langlint_py_dir)
        
        # Copy langlint package
        langlint_src = "python/langlint"
        langlint_dst = os.path.join(temp_dir, "langlint")
        if os.path.exists(langlint_src):
            shutil.copytree(langlint_src, langlint_dst)
        
        # Copy Rust CLI binary
        rust_cli_src = "../../target/release/langlint.exe"
        if os.path.exists(rust_cli_src):
            # Put it in langlint package directory
            rust_cli_dst = os.path.join(langlint_dst, "langlint.exe")
            shutil.copy2(rust_cli_src, rust_cli_dst)
        
        # Update RECORD file
        record_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "RECORD":
                    record_path = os.path.join(root, file)
                    break
        
        if record_path:
            # Read existing records
            with open(record_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out langlint_py directory entries and add new ones
            new_lines = []
            for line in lines:
                if not line.startswith("langlint_py/"):
                    new_lines.append(line)
            
            # Add langlint_py.pyd entry
            new_lines.insert(0, "langlint_py.cp311-win_amd64.pyd,,\n")
            
            # Add langlint package entries
            for root, dirs, files in os.walk(langlint_dst):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
                    rel_path = rel_path.replace("\\", "/")
                    new_lines.append(f"{rel_path},,\n")
            
            with open(record_path, 'w') as f:
                f.writelines(new_lines)
        
        # Recreate wheel
        new_wheel_path = wheel_path.replace(".whl", "_fixed.whl")
        with zipfile.ZipFile(new_wheel_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)
        
        # Replace original wheel
        os.remove(wheel_path)
        os.rename(new_wheel_path, wheel_path)
        
        print(f"Fixed wheel: {wheel_path}")

if __name__ == "__main__":
    build_wheel()
