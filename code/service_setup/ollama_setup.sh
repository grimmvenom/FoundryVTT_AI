#!/bin/bash
# Summary:
# Ollama manual setup on linux
#

# --- CONFIGURATION ---
USER_NAME=${SUDO_USER:-$(whoami)}  # Gets the actual user if run with sudo
WEBUI_DIR="$(pwd)/open-webui"
PORT="9000"
MODEL="llama3.1:8b"


# --- PERMISSION CHECK ---

function check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        echo "Error: This script must be run with elevated permissions."
        echo "Please run: sudo $0"
        exit 1
    fi
}


# --- CORE FUNCTIONS ---

function install_dependencies() {
    echo "--- Installing Ollama and Python dependencies ---"
    pacman -Sy --needed ollama python-pip
    # install python version 3.12 for WebUI
    pamac build python312
}


function install_ollama() {
    pacman -Sy ollama
    systemctl enable --now ollama
}


 # Start without systemctl (no Jail / airgap)
function update_model_unlocked() {
    echo "--- Temporarily unlocking internet to pull $MODEL ---"
    systemctl stop ollama
    # Run serve in background as the actual user to avoid permission mess
    sudo -u "$USER_NAME" ollama serve > /dev/null 2>&1 &
    SERVE_PID=$!
    sleep 5
    sudo -u "$USER_NAME" ollama pull "$MODEL"
    kill $SERVE_PID
    echo "--- Relocking and starting system service ---"
    systemctl start ollama
}


function launch_ollama_interactive() {
    echo "--- Launching Interactive Terminal Chat ---"
    # Use sudo -u to run as YOU, not root
    sudo -u "$USER_NAME" ollama run $MODEL
}


function launch_ollama() {
    echo "--- Launching Chat In Background---"
    sudo -u "$USER_NAME" ollama run $MODEL &
}

function stop_ollama() {
    systemctl stop ollama
}


function restart_ollama() {
    systemctl daemon-reload
    systemctl restart ollama
}


function setup_open_webui() {
    echo "--- Setting up Open WebUI in $WEBUI_DIR ---"
    # We use sudo -u to ensure the folders and venv are owned by YOU, not root
    sudo -u "$USER_NAME" mkdir -p "$WEBUI_DIR"
    cd "$WEBUI_DIR" || exit
    
    sudo -u "$USER_NAME" python3.12 -m venv venv
    sudo -u "$USER_NAME" "$WEBUI_DIR/venv/bin/pip" install open-webui

    echo "--- Creating Systemd Service for WebUI (Port $PORT) ---"
    cat <<EOF > /etc/systemd/system/open-webui.service
[Unit]
Description=Open WebUI (Air-Gapped)
After=network.target ollama.service

[Service]
User=$USER_NAME
WorkingDirectory=$WEBUI_DIR
Environment="PATH=$WEBUI_DIR/venv/bin"
Environment="PORT=$PORT"
# AIR-GAP JAIL
IPAddressDeny=any
IPAddressAllow=127.0.0.1
IPAddressAllow=192.168.7.0/24
ExecStart=$WEBUI_DIR/venv/bin/open-webui serve
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    echo "Open WebUI should be setup now under $WEBUI_DIR"
    
}



function start_open_webui(){
    systemctl daemon-reload
    systemctl enable --now open-webui
    echo "--- Open WebUI started on http://localhost:$PORT ---"
    sleep 2
}


# -- EXECUTION FLOW (Uncomment these as needed) --
# --- Mandatory Permission Check---
check_permissions

# --- First time setup: ---
# install_dependencies
# install_ollama
setup_open_webui

# --- Maintenance Functions: ---
# update_model_unlocked
# restart_ollama
# stop_ollama

# --- Run Functions: ---
start_open_webui
launch_ollama_interactive
# launch_ollama

