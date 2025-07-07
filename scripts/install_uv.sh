#!/bin/bash

UV_INSTALL_PATH="$HOME/.local/bin"

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

# Check if uv is installed, if not, install it
if ! command -v uv > /dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    add_uv_to_path
else
    echo "uv is already installed."
fi
