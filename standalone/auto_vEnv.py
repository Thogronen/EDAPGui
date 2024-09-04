import os
import subprocess
import sys

def create_venv(venv_name):
    # Create the virtual environment
    subprocess.check_call([sys.executable, "-m", "venv", venv_name])
    print(f"Virtual environment '{venv_name}' created successfully.")

def activate_venv(venv_name):
    activate_script = os.path.join(venv_name, 'Scripts', 'activate.bat')
    if os.name == 'nt':  # For Windows
        os.system(f'start cmd /k "{activate_script}"')
    else:  # For macOS/Linux
        os.system(f'source {venv_name}/bin/activate')

def install_packages(venv_name, requirements_file):
    # Install the packages listed in requirements.txt
    subprocess.check_call([os.path.join(venv_name, 'Scripts', 'pip'), "install", "-r", requirements_file])
    print(f"Packages from {requirements_file} installed successfully.")

def open_folder(venv_name):
    if os.name == 'nt':  # For Windows
        os.startfile(os.path.abspath(venv_name))
    elif os.name == 'posix':  # For macOS/Linux
        subprocess.call(['open', os.path.abspath(venv_name)])

if __name__ == "__main__":
    venv_name = "myenv"  # Change this to your desired venv name
    requirements_file = "requirements.txt"  # Ensure you have a requirements.txt in the same directory

    # Create virtual environment
    create_venv(venv_name)
    
    # Install packages from requirements.txt
    if os.path.exists(requirements_file):
        install_packages(venv_name, requirements_file)
    else:
        print(f"{requirements_file} not found. Skipping package installation.")
    
    # Open the virtual environment folder
    open_folder(venv_name)
    
    # Activate the virtual environment
    activate_venv(venv_name)
