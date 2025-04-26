#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found in current directory"
  exit 1
fi

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
  echo "Error: fly CLI not found. Please install it first."
  echo "You can install it with: brew install flyctl"
  exit 1
fi

echo "Reading secrets from .env and setting them on fly.io..."

# Read each line from .env file
while IFS= read -r line || [ -n "$line" ]; do
  # Skip empty lines and comments
  if [[ -z "$line" || "$line" =~ ^# ]]; then
    continue
  fi
  
  # Remove any inline comments (everything after #)
  line=$(echo "$line" | sed 's/\s*#.*$//')
  
  # Trim whitespace
  line=$(echo "$line" | xargs)
  
  # Check if line contains an assignment
  if [[ "$line" =~ ^([A-Za-z0-9_]+)=(.*)$ ]]; then
    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    
    # Remove surrounding quotes if present
    value=$(echo "$value" | sed -E 's/^"(.*)"$/\1/' | sed -E "s/^'(.*)'$/\1/")
    
    echo "Setting $key..."
    fly secrets set "$key=$value"
  fi
done < .env

echo "All secrets from .env have been set on fly.io!"