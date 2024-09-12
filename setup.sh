# Install Nginx from the official Nginx repository
install_nginx() {
    if ! command -v nginx &> /dev/null
    then
        echo "Nginx not found. Installing from the official Nginx repository..."

        # Add Nginx's official signing key
        curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo tee /etc/apt/trusted.gpg.d/nginx_signing.asc > /dev/null

        # Add the Nginx repository
        echo "deb [arch=$(dpkg --print-architecture)] http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list

        # Update the package lists and install Nginx
        sudo apt update
        sudo apt install -y nginx

        echo "Nginx installed successfully."
    else
        echo "Nginx is already installed."
    fi
}

# Install Git
install_git() {
    if ! command -v git &> /dev/null
    then
        echo "Git not found. Installing Git..."
        sudo apt update
        sudo apt install -y git
        echo "Git installed successfully."
    else
        echo "Git is already installed."
    fi
}

# Install Ngrok
install_ngrok() {
    if ! command -v ngrok &> /dev/null
    then
        echo "Ngrok not found. Installing Ngrok..."

        # Download Ngrok and install it
        wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
        unzip ngrok-stable-linux-amd64.zip
        sudo mv ngrok /usr/local/bin/ngrok
        rm ngrok-stable-linux-amd64.zip

        echo "Ngrok installed successfully."
    else
        echo "Ngrok is already installed."
    fi
}

# Install Node.js and npm from the official NodeSource repository
install_nodejs() {
    if ! command -v node &> /dev/null
    then
        echo "Node.js not found. Installing Node.js from NodeSource..."

        # Add Node.js PPA (for latest version of Node.js)
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

        # Install Node.js and npm
        sudo apt update
        sudo apt install -y nodejs

        echo "Node.js installed successfully."
    else
        echo "Node.js is already installed."
    fi
}

install_jq(){
  if ! command -v jq &> /dev/null
  then
    echo "jq not found. Installing jq from apt"
    sudo apt install -y jq
    sudo apt update
    echo "jq installed successfully."
  else
    echo "jq is already installed."
  fi
}

# Usage example
install_nginx
install_git
install_ngrok
install_nodejs
install_jq

# 2. Create ngrok multi-tunneling configuration
echo "Creating ngrok multi-tunneling configuration..."

mkdir -p ~/.ngrok
cat > ~/.ngrok/ngrok.yml <<EOL
tunnels:
  flask:
    addr: 5000
    proto: http
    bind_tls: false
  nodejs:
    addr: 3000
    proto: http
    bind_tls: false
EOL

# 3. ngrok API key generation doc
echo "For ngrok API key generation, follow these steps:"
echo "1. Sign up or log in to ngrok at https://dashboard.ngrok.com"
echo "2. Go to the Auth section to get your API key."
echo "3. Replace <YOUR_NGROK_API_KEY> below with your actual API key."

# 4. Add ngrok API key
echo "Adding ngrok API key..."
# shellcheck disable=SC2162
read -p "Enter your ngrok API key: " NGROK_API_KEY
./ngrok authtoken "$NGROK_API_KEY"

#!/bin/bash

# Function to create or update the .env file with key-value pairs
create_or_update_env_file() {
    ENV_FILE=".env"
    # Check if the .env file exists, if not create it
    if [ ! -f "$ENV_FILE" ]; then
        touch "$ENV_FILE"
        echo ".env file created."
    else
        echo ".env file already exists."
    fi
    # Function to add or update a key-value pair in .env
    add_or_update_env_var() {
        local key=$1
        local value=$2

        # Check if the key already exists in the file
        if grep -q "^${key}=" "$ENV_FILE"; then
            # If the key exists, replace the value
            sed -i "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
            echo "Updated ${key}=${value} in the .env file."
        else
            # If the key does not exist, append it
            echo "${key}=${value}" >> "$ENV_FILE"
            echo "Added ${key}=${value} to the .env file."
        fi
    }
    # Call the function to add or update the key-value pair in .env
    add_or_update_env_var "NGROK_API_KEY" "$NGROK_API_KEY"

echo "Finished updating the .env file."
}
# Call the function to start the process
create_or_update_env_file

# Installing envtool
echo "Installing envtool..."

git clone https://github.com/psypherion/envtool.git

cd envtool || exit

chmod +x run.sh

./run.sh

cd ../

# setting up python environment

echo "Setting up python environment..."
envtool -n venv

echo "Done!"

mkdir assets/
echo "Setup is complete now activate the virtual environment"

echo "Type this command : source venv/bin/activate"

# setting up nodejs environment
npm init
npm install express socket.io