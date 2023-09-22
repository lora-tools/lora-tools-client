
# lora-tools-client

## Setup Instructions

### Ngrok Setup

1. Sign up at [ngrok](https://dashboard.ngrok.com/signup)
2. Get your [free ngrok static domain](https://dashboard.ngrok.com/cloud-edge/domains)
3. [Install ngrok](https://ngrok.com/download) locally

### Server Setup

1. Create a server at [lora.tools](https://lora.tools/servers?s=createnew)
2. Copy/Paste your ngrok domain URL into the URL field

### lora-tools-client Installation

1. Open a terminal and clone this repository (lora-tools-client):
   ```bash
   git clone https://github.com/lora-tools/lora-tools-client.git
   ```

2. Install python and pip, then launch the installer GUI:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   cd lora-tools-client && python install.py
   ```

3. Copy ngrok authtoken, ngrok domain & server ID into the installer GUI.

4. Click the 'Install' button and wait for the installation to finish (takes about 10-15 minutes).

5. Click the 'Launch' button, or close the installer GUI and run:
   ```bash
   python launch.py
   ```

6. Click the 'Start' buttons next to the kohya_ss and sd_webui modules and wait for the launch to finish.
   - Note: The first launch takes about 5-10 minutes. Subsequent launches will only take a few seconds.

7. Click the Lora_._tools 'Start' button.

## Minimum Requirements

- Operating System: Linux or macOS
- Python
- CUDA
- NVIDIA GPU with at least 12+ GB VRAM
- At least 40+ GB free space on an SSD
