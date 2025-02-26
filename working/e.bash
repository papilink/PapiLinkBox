#!/bin/bash

# Set the email address associated with your Git account
EMAIL="mgenialive@gmail.com

# Set the default SSH key file location
SSH_KEY_FILE="$HOME/.ssh/id_ed25519"

# Generate a new SSH key
echo "Generating a new SSH key..."
ssh-keygen -t ed25519 -C "$EMAIL" -f "$SSH_KEY_FILE"

# Start the SSH agent in the background
echo "Starting the SSH agent..."
eval "$(ssh-agent -s)"

# Add the SSH private key to the SSH agent
echo "Adding the SSH key to the SSH agent..."
ssh-add "$SSH_KEY_FILE"

# Copy the SSH public key to the clipboard
if command -v xclip &> /dev/null; then
    cat "${SSH_KEY_FILE}.pub" | xclip -selection clipboard
    echo "Your SSH public key has been copied to the clipboard."
elif command -v pbcopy &> /dev/null; then
    cat "${SSH_KEY_FILE}.pub" | pbcopy
    echo "Your SSH public key has been copied to the clipboard."
else
    echo "Could not copy the SSH public key to the clipboard. Please manually copy the following key:"
    cat "${SSH_KEY_FILE}.pub"
fi

# Instructions for adding the SSH key to your Git hosting service
echo "Please add the SSH public key to your Git hosting service (e.g., GitHub, GitLab)."
echo "For GitHub, you can do this by navigating to:"
echo "https://github.com/settings/ssh/new"

# Test the SSH connection to GitHub
echo "Testing SSH connection to GitHub..."
ssh -T git@github.com

echo "SSH setup for Git is complete!"