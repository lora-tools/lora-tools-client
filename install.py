import tkinter as tk
from tkinter import ttk
import os
import subprocess
import shutil
import sys
import platform
import pkg_resources
import threading
import secrets
import webbrowser
import requests
import sys
import time

SCRIPTS_DIR = "scripts"

git_command = "git"

def get_os():
    """Returns the current OS: 'linux', 'windows', or 'mac'."""
    os_name = platform.system().lower()
    if "linux" in os_name:
        return "linux"
    elif "windows" in os_name:
        return "windows"
    elif "darwin" in os_name:  # MacOS
        return "mac"
    else:
        raise ValueError("Unsupported OS detected.")

def generate_random_string(length=32):
    """Generate a cryptographically secure random string of the given length."""
    return secrets.token_hex(length)

def ensure_scripts_dir():
    """Ensure the scripts directory exists."""
    os.makedirs(SCRIPTS_DIR, exist_ok=True)

def clone_repositories():
    
    subprocess.run([git_command, "clone", "https://github.com/AUTOMATIC1111/stable-diffusion-webui", "stable-diffusion-webui"])
    subprocess.run([git_command, "clone", "https://github.com/bmaltais/kohya_ss.git", "kohya_ss"])
    subprocess.run([git_command, "-C", "kohya_ss", "checkout", "397bf51a8cd36104e52055358e4ffd066c5858df"])
    subprocess.run([git_command, "clone", "https://github.com/lora-tools/lora-tools.git", "api"])

def create_env_file(SDAPIUSERNAME, SDAPIPASSWORD, NGROK_AUTH_TOKEN, NGROK_DOMAIN, SERVERID):
    env_path = os.path.join("api", ".env")
    with open(env_path, "w") as f:
        f.write(f"SDAPIUSERNAME={SDAPIUSERNAME}\n")
        f.write(f"SDAPIPASSWORD={SDAPIPASSWORD}\n")
        f.write(f"NGROK_AUTH_TOKEN={NGROK_AUTH_TOKEN}\n")
        f.write(f"NGROK_DOMAIN={NGROK_DOMAIN}\n")
        f.write(f"SERVERID={SERVERID}\n")

def download_file(url, destination):
    """Download a file from a given URL to a specified destination."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def download_models():
    # Ensure the directory exists
    os.makedirs("stable-diffusion-webui/models/Stable-diffusion/XL", exist_ok=True)
    os.makedirs("stable-diffusion-webui/models/VAE", exist_ok=True)

    download_file("https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors", "stable-diffusion-webui/models/Stable-diffusion/XL/sd_xl_base_1.0.safetensors")
    download_file("https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors", "stable-diffusion-webui/models/Stable-diffusion/XL/sd_xl_refiner_1.0.safetensors")
    download_file("https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors", "stable-diffusion-webui/models/VAE/sdxl_vae.safetensors")

    # Clone adetailer repository to a temporary location
    subprocess.run([git_command, "clone", "https://github.com/Bing-su/adetailer.git", "adetailer_tmp"])
    
    # Move the contents of adetailer_tmp to stable-diffusion-webui/extensions/adetailer
    adetailer_dest_path = "stable-diffusion-webui/extensions/adetailer"
    os.makedirs(adetailer_dest_path, exist_ok=True)
    for item in os.listdir("adetailer_tmp"):
        src_path = os.path.join("adetailer_tmp", item)
        dest_path = os.path.join(adetailer_dest_path, item)
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)
        shutil.move(src_path, dest_path)
    
    # Remove the temporary directory
    shutil.rmtree("adetailer_tmp")

def create_sd_webui_start_script(SDAPIUSERNAME, SDAPIPASSWORD):
    ensure_scripts_dir()
    os_type = get_os()
    if os_type == "windows":
        shebang_line = ""
        script_ext = ".bat"
        activate_command = "call venv\\Scripts\\activate.bat"
        command_suffix = "call"
    else:  # Linux and MacOS
        shebang_line = "#!/bin/bash"
        script_ext = ".sh"
        activate_command = "source venv/bin/activate"
        command_suffix = "bash"

    content = f"""{shebang_line}
cd stable-diffusion-webui
{activate_command}
{command_suffix} webui{script_ext} --port 7869 --xformers --api --cors-allow-origins=http://0.0.0.0:7869 --listen --no-half-vae --hide-ui-dir-config --gradio-auth {SDAPIUSERNAME}:{SDAPIPASSWORD} --api-auth {SDAPIUSERNAME}:{SDAPIPASSWORD}
"""
    script_path = os.path.join(SCRIPTS_DIR, f"sd_webui{script_ext}")
    with open(script_path, "w") as f:
        f.write(content)
    if os_type != "windows":
        os.chmod(script_path, 0o755)

def create_kohya_ss_start_script():
    ensure_scripts_dir()
    os_type = get_os()
    if os_type == "windows":
        shebang_line = ""
        script_ext = ".bat"
        activate_command = "call venv\\Scripts\\activate.bat"
        command_suffix = "call"
    else:  # Linux and MacOS
        shebang_line = "#!/bin/bash"
        script_ext = ".sh"
        activate_command = "source venv/bin/activate"
        command_suffix = ""

    content = f"""{shebang_line}
cd kohya_ss
{activate_command}
{command_suffix} gui{script_ext} --listen 0.0.0.0 --server_port 4204 --headless
"""
    script_path = os.path.join(SCRIPTS_DIR, f"kohya_ss{script_ext}")
    with open(script_path, "w") as f:
        f.write(content)
    if os_type != "windows":
        os.chmod(script_path, 0o755)

def setup_kohya_ss():
    os_type = get_os()
    if os_type == "windows":
        process = subprocess.Popen(["setup.bat"], cwd="kohya_ss", stdin=subprocess.PIPE, text=True, shell=True)
        process.communicate(input="1\n2\n6\n")
    else:  # Linux and MacOS
        subprocess.run(["./setup.sh"], cwd="kohya_ss")

def get_pip_path():
    base_dir = os.path.abspath("api")
    os_type = get_os()
    if os_type == "windows":
        return os.path.join(base_dir, "venv", "Scripts", "pip.exe")
    else:  # Linux and MacOS
        return os.path.join(base_dir, "venv", "bin", "pip")

def setup_api_venv():
    os_type = get_os()
    if os_type == "windows":
        python_executable = "python.exe"
    else:  # Linux and MacOS
        python_executable = "python"

    # Create the virtual environment
    subprocess.run([python_executable, "-m", "venv", "venv"], cwd="api")
    
    # Install the requirements
    subprocess.run([get_pip_path(), "install", "-r", "requirements.txt"], cwd="api")
    
    # Debug helper
    result = subprocess.run([get_pip_path(), "install", "-r", "requirements.txt"], cwd="api", capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

# Modify the .env file
def modify_env_file():
    base_dir = os.getcwd()
    env_path = os.path.join(base_dir, "api", ".env")
    with open(env_path, "a") as f:
        f.write(f"BASE_TRAINING_DIR={base_dir}/api/trainingSessions\n")
        f.write(f"LORA_PATH={base_dir}/stable-diffusion-webui/models/Lora\n")
        f.write(f"BASE_PATH={base_dir}\n")
        f.write("KOHYA_URL=http://0.0.0.0:4204/\n")
        f.write("SDAPIURL=http://0.0.0.0:7869\n")
        f.write("PROXY_FETCH_URL=https://lora.tools/api/1.1/wf/proxy_url\n")
        f.write("TRAINING_COMPLETE_URL=https://lora.tools/api/1.1/wf/training_complete\n")
        f.write("SERVER_PING_URL=https://lora.tools/api/1.1/wf/ping-sdwebui\n")

# Create the lora_tools.sh script
def create_lora_tools_script():
    ensure_scripts_dir()
    os_type = get_os()
    if os_type == "windows":
        shebang_line = ""  # Windows doesn't need a shebang line
        script_ext = ".bat"
        activate_command = "call venv\\Scripts\\activate.bat"
        ngrok_command = "start ngrok http %RANDOM_PORT% --authtoken %NGROK_AUTH_TOKEN% --domain %NGROK_DOMAIN%"
        uvicorn_command = "uvicorn main:app --host 0.0.0.0 --port %RANDOM_PORT% --reload"
        random_port_generation = "set /a RANDOM_PORT=8301 + %RANDOM% %% 201"
    else:  # Linux and MacOS
        shebang_line = "#!/bin/bash"
        script_ext = ".sh"
        activate_command = "source venv/bin/activate"
        ngrok_command = "ngrok http $RANDOM_PORT --authtoken $NGROK_AUTH_TOKEN --domain $NGROK_DOMAIN &"
        uvicorn_command = "uvicorn main:app --host 0.0.0.0 --port $RANDOM_PORT --reload"
        random_port_generation = "RANDOM_PORT=$((8301 + RANDOM % 201))"

    content = f"""{shebang_line}
cd api
{activate_command}
{random_port_generation}
{ngrok_command}
{uvicorn_command}
"""
    script_path = os.path.join(SCRIPTS_DIR, f"lora_tools{script_ext}")
    with open(script_path, "w") as f:
        f.write(content)
    if os_type != "windows":
        os.chmod(script_path, 0o755)

# Generate the launch.py file
def create_startup_script():
    content = """import subprocess
import tkinter as tk
import time
import psutil
import platform
import os

def get_os():
    os_name = platform.system().lower()
    if "windows" in os_name:
        return "windows"
    elif "linux" in os_name:
        return "linux"
    elif "darwin" in os_name:
        return "mac"
    else:
        return None

def start_scripts():
    root = tk.Tk()
    root.title("Lora.tools Launcher")

    processes = {
        "kohya_ss": None,
        "sd_webui": None,
        "lora_tools": None
    }

    os_type = get_os()

    if os_type == "windows":
        commands = {
            "kohya_ss": [r"scripts\kohya_ss.bat"],
            "sd_webui": [r"scripts\sd_webui.bat"],
            "lora_tools": [r"scripts\lora_tools.bat"]
        }
    else:
        commands = {
            "kohya_ss": ["./scripts/kohya_ss.sh"],
            "sd_webui": ["./scripts/sd_webui.sh"],
            "lora_tools": ["./scripts/lora_tools.sh"]
        }

    def start_process(script):
        if processes[script] is None or processes[script].poll() is not None:
            processes[script] = subprocess.Popen(commands[script], shell=True if os_type == "windows" else False)

    def stop_process(script):
        process = processes[script]
        if process:
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except psutil.NoSuchProcess:
                pass

        # Clear terminal screen
        if os_type == "windows":
            os.system('cls')
        else:  # UNIX-like systems (Linux, MacOS)
            os.system('clear')

        # Print the custom message to the terminal
        print(f"{script} stopped")
        
        # Give the process a little time to terminate
        time.sleep(1)

        # If it's still running after attempting to kill, force terminate
        process = processes[script]
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
            if process.poll() is None:
                process.kill()

    def update_status():
        for script, process in processes.items():
            label = labels[script]
            start_btn = start_buttons[script]
            stop_btn = stop_buttons[script]

            if process and process.poll() is None:  # Still running
                label.config(text=f"{script} status: Running")
                start_btn.config(state=tk.DISABLED)
                stop_btn.config(state=tk.NORMAL)
            else:
                label.config(text=f"{script} status: Not running")
                start_btn.config(state=tk.NORMAL)
                stop_btn.config(state=tk.DISABLED)

        root.after(1000, update_status)

    labels = {}
    start_buttons = {}
    stop_buttons = {}

    for script in processes.keys():
        frame = tk.Frame(root)
        frame.pack(pady=24, padx=32, fill=tk.X)

        label = tk.Label(frame, text=f"{script} status: Not started", font="Arial", width=30, anchor="w")
        label.pack(side=tk.LEFT)
        labels[script] = label

        start_btn = tk.Button(frame, text="Start", font="Arial", command=lambda s=script: start_process(s))
        start_btn.pack(side=tk.LEFT, padx=12)
        start_buttons[script] = start_btn

        stop_btn = tk.Button(frame, text="Stop", font="Arial", command=lambda s=script: stop_process(s))
        stop_btn.pack(side=tk.LEFT)
        stop_buttons[script] = stop_btn

    update_status()

    def on_exit():
        for process in processes.values():
            if process and process.poll() is None:
                process.terminate()
                process.wait()
                if process.poll() is None:
                    process.kill()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_exit)
    root.mainloop()

if __name__ == "__main__":
    start_scripts()
"""
    # Modify the paths in the content to be relative to the scripts directory
    content = content.replace("./kohya_ss.sh", f"./{SCRIPTS_DIR}/kohya_ss.sh")
    content = content.replace("./sd_webui.sh", f"./{SCRIPTS_DIR}/sd_webui.sh")
    content = content.replace("./lora_tools.sh", f"./{SCRIPTS_DIR}/lora_tools.sh")

    with open("launch.py", "w") as f:
        f.write(content)

# tkinter GUI Class
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Lora.tools Installer")

        # Set the GUI dimensions
        self.root.geometry('800x600')
        self.root.minsize(800, 600)

        # Vertically and horizontally center all widgets
        # self.root.grid_rowconfigure(0, weight=1)
        # self.root.grid_columnconfigure(0, weight=1)

        # Create a main frame for padding
        self.main_frame = ttk.Frame(self.root, padding=32)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        self.labels = ["NGROK_AUTH_TOKEN", "NGROK_DOMAIN", "SERVERID"]
        
        if self.all_prerequisites_met():
            # self.display_image()
            self.show_completion_message()
        else:
            # self.display_image()
            self.display_instructions()
            self.show_input_fields()

    # @TODO - Add branding
    # def display_image(self):
    #     # Load and display the image
    #     self.img = tk.PhotoImage(file="icon128x128.png")
    #     img_label = ttk.Label(self.main_frame, image=self.img)
    #     img_label.pack(pady=20)

    def display_instructions(self):
        # Display the instructions using a Text widget for the clickable link
        self.instruction_text = tk.Text(self.main_frame, height=3, wrap=tk.WORD, bg=self.root.cget("background"), relief=tk.FLAT)
        self.instruction_text.insert(tk.END, "Create your Lora.tools server and get installation instructions at ")
        self.instruction_text.insert(tk.END, "lora.tools", "link")
        self.instruction_text.tag_configure("link", foreground="blue", underline=True)
        self.instruction_text.tag_bind("link", "<Button-1>", lambda e: webbrowser.open("https://lora.tools/servers?s=createnew"))
        self.instruction_text.configure(state=tk.DISABLED)  # Make it read-only
        self.instruction_text.pack(pady=20)

    def all_prerequisites_met(self):
        # Check for the repositories
        repos_exist = all(os.path.isdir(repo) for repo in ["stable-diffusion-webui", "kohya_ss", "api"])
        # if not repos_exist:
        #     print("Repositories missing.")

        # Check for the scripts
        scripts_exist = all(os.path.isfile(os.path.join(SCRIPTS_DIR, script)) for script in ["sd_webui.sh", "kohya_ss.sh", "lora_tools.sh"])
        # if not scripts_exist:
        #     print("Scripts missing.")
        
        # Check for the venv directories
        venvs_exist = all(os.path.isdir(os.path.join(repo, "venv")) for repo in ["kohya_ss", "api"])
        # if not venvs_exist:
        #     print("Venvs missing.")

        # Check for the HuggingFace downloads
        huggingface_downloads = [
            "stable-diffusion-webui/models/Stable-diffusion/XL/sd_xl_base_1.0.safetensors",
            "stable-diffusion-webui/models/Stable-diffusion/XL/sd_xl_refiner_1.0.safetensors",
            "stable-diffusion-webui/models/VAE/sdxl_vae.safetensors",
            "stable-diffusion-webui/extensions/adetailer/install.py"
        ]
        downloads_exist = all(os.path.isfile(download) for download in huggingface_downloads)
        # if not downloads_exist:
        #     print("HuggingFace downloads missing.")

        kohya_requirements = []
        if os.path.exists("kohya_ss/venv/bin/pip"):
            kohya_requirements = self.get_installed_packages("kohya_ss/venv/bin/pip")
        api_requirements = []
        if os.path.exists("api/venv/bin/pip"):
            api_requirements = self.get_installed_packages("api/venv/bin/pip")
        
        kohya_required = self.read_requirements("kohya_ss/requirements_linux.txt")
        api_required = self.read_requirements("api/requirements.txt")
        
        # Debugging: Print the required and installed packages
        # print("Kohya required:", kohya_required)
        # print("Kohya installed:", kohya_requirements)

        # Check if required packages are installed in the virtual environments
        kohya_missing = kohya_required - set(kohya_requirements)
        if kohya_missing:
            print("Kohya missing requirements:", kohya_missing)
        
        api_missing = api_required - set(api_requirements)
        if api_missing:
            print("API missing requirements:", api_missing)
        
        return repos_exist and scripts_exist and venvs_exist and downloads_exist and not kohya_missing and not api_missing

    def standardize_name(self, name):
        return name.replace("-", "_").lower()

    def get_installed_packages(self, pip_path):
        output = subprocess.check_output([pip_path, "list"], text=True)
        lines = output.split("\n")[2:]  # Skip the header lines
        installed = set(line.split()[0] for line in lines if line)  # Just get the package name
        return installed

    def read_requirements(self, filepath):
        """Read the requirements file and return a set of required packages."""
        requirements = set()
        if not os.path.exists(filepath):
            return requirements
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Check for references to other requirements files
                if line.startswith("-r"):
                    ref_filepath = line.split(" ", 1)[-1].strip()
                    requirements.update(self.read_requirements(ref_filepath))
                else:
                    # Extract package name without version specifier
                    requirements.add(line.split('==')[0].split('>')[0].split('<')[0].split('@')[0].strip())
        return requirements

    def show_input_fields(self):
        for label in self.labels:
            frame = ttk.Frame(self.main_frame)
            frame.pack(padx=10, pady=5, fill=tk.X)
            
            lbl = ttk.Label(frame, text=label, width=20)
            lbl.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.entries[label] = entry
        
        self.submit_button = ttk.Button(self.main_frame, text="Install", command=self.on_submit)
        self.submit_button.pack(pady=20)

    def show_completion_message(self):
        ttk.Label(self.main_frame, text="✅ Lora.tools installation is complete").pack(pady=20)
        
        start_server_btn = ttk.Button(self.main_frame, text="Launch", command=self.start_server)
        start_server_btn.pack(pady=20)
        
    def start_server(self):
        self.root.destroy()  # Close the tkinter window
        subprocess.run(["python", "launch.py"])  # Run the launch.py script
        
    def hide_inputs_and_submit(self):
        """Hide the input fields, the submit button, and the instructions."""
        for entry in self.entries.values():
            entry.master.pack_forget()
        self.submit_button.pack_forget()
        self.instruction_text.pack_forget()  # Hide the instructions

    def show_installing_message(self):
        """Display the 'Installing...' message."""
        self.installing_label = ttk.Label(self.root, text="Installing... Please wait")
        self.installing_label.pack(pady=20)

    def installation_process(self, SDAPIUSERNAME, SDAPIPASSWORD, NGROK_AUTH_TOKEN, NGROK_DOMAIN, SERVERID):
       # Step 2a: Clone the repositories
        clone_repositories()

        # Step 2b: Setup api venv
        setup_api_venv()

        # Step 3: Create the .env file
        create_env_file(SDAPIUSERNAME, SDAPIPASSWORD, NGROK_AUTH_TOKEN, NGROK_DOMAIN, SERVERID)

        # Step 4: Download the models
        download_models()

        # Step 5: Generate the shell scripts
        create_sd_webui_start_script(SDAPIUSERNAME, SDAPIPASSWORD)
        create_kohya_ss_start_script()

        # Step 6: Setup kohya_ss
        setup_kohya_ss()

        # Step 7: Modify the .env file
        modify_env_file()

        # Step 8: Create the lora_tools.sh script
        create_lora_tools_script()

        # Step 9: Generate the launch.py file
        create_startup_script()

        # Once installation is done, update the GUI in the main thread
        self.root.after(0, self.post_installation_updates)

    def post_installation_updates(self):
        """Updates to be done after installation."""
        self.installing_label.pack_forget()
        self.show_completion_message()

    def on_submit(self):
        self.hide_inputs_and_submit()
        self.show_installing_message()

        SDAPIUSERNAME = generate_random_string()
        SDAPIPASSWORD = generate_random_string()
        NGROK_AUTH_TOKEN = self.entries["NGROK_AUTH_TOKEN"].get()
        NGROK_DOMAIN = self.entries["NGROK_DOMAIN"].get()
        SERVERID = self.entries["SERVERID"].get()

        # Start the installation process in a separate thread
        install_thread = threading.Thread(target=self.installation_process, args=(SDAPIUSERNAME, SDAPIPASSWORD, NGROK_AUTH_TOKEN, NGROK_DOMAIN, SERVERID))
        install_thread.start()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()