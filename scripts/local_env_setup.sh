#!/bin/bash

export UV_PROJECT_ENVIRONMENT="cra_env"

VENV_PATH="./cra_env"
UV_INSTALL_PATH="$HOME/.local/bin"
# Dynamically find Python 3.10
PYTHON_PATH=$(command -v python3.10)

if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python 3.10 is not found in PATH. Please install it or add it to PATH."
    exit 1
else
    echo "Python 3.10 found at $PYTHON_PATH."
fi

# Function to add uv to PATH
add_uv_to_path() {
    SHELL_CONFIG=""

    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    else
        echo "Unsupported shell. Please add $UV_INSTALL_PATH to your PATH manually."
        return
    fi

    if ! grep -q "$UV_INSTALL_PATH" "$SHELL_CONFIG"; then
        echo "Adding $UV_INSTALL_PATH to PATH in $SHELL_CONFIG"
        echo "export PATH=\"$UV_INSTALL_PATH:\$PATH\"" >> "$SHELL_CONFIG"
        echo "Please run 'source $SHELL_CONFIG' or open a new terminal to apply changes."
    else
        echo "$UV_INSTALL_PATH is already in PATH."
    fi
}

# Check if uv is installed, if not, print error message
if ! command -v uv > /dev/null 2>&1; then
    echo "Error: 'uv' is not installed. Please use 'install_uv.sh' script to install it first!"
    exit 1
else
    echo "uv is already installed."
fi

# Check if the specified Python version is installed
if ! command -v "$PYTHON_PATH" > /dev/null 2>&1; then
    echo "Error: Python 3.10 is not installed at $PYTHON_PATH. Please install it first."
    exit 1
else
    echo "Python 3.10 found at $PYTHON_PATH."
fi

# Check if virtual environment is set up, if not, set it up
if [ ! -d "$VENV_PATH" ]; then
    echo "Setting up virtual environment with uv using $PYTHON_PATH..."
    if uv venv "$UV_PROJECT_ENVIRONMENT" -p "$PYTHON_PATH"; then
        echo "Virtual environment '$UV_PROJECT_ENVIRONMENT' created successfully."
    else
        echo "Failed to create the virtual environment. Please check for errors above."
        exit 1
    fi
    # Ensure pip is installed in the virtual environment
    echo "Ensuring pip is available..."
    # shellcheck source=/dev/null
    source "$VENV_PATH"/bin/activate
    python -m ensurepip --upgrade
    deactivate
else
    echo "Virtual environment '$UV_PROJECT_ENVIRONMENT' already exists."
fi

# Install dependencies in the virtual environment
echo "Installing dependencies with uv sync..."
if uv sync; then
    echo "Dependencies installed successfully."
else
    echo "Failed to install dependencies. Please check for errors above."
    exit 1
fi

# Ensure pip is installed and upgraded in the virtual environment
echo "Ensuring pip is available and up-to-date..."
source "$VENV_PATH"/bin/activate
if python -m ensurepip --upgrade; then
    echo "pip is available and up-to-date."
else
    echo "Failed to ensure pip. Please check for errors above."
    deactivate
    exit 1
fi
deactivate

echo "All steps completed successfully!"
