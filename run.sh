#!/bin/bash

# Install necessary packages
sudo apt install -y python3-pip build-essential libssl-dev libffi-dev python3-dev python3-venv postgresql postgresql-contrib expect

# Create and activate virtual environment
python3 -m venv env
source ./env/bin/activate

# Install requirements
pip install -r requirements.txt

if ! sudo grep "^postgres:" /etc/shadow > /dev/null; then
    echo -e "\nsetting up the postgres database..."

    echo "prompt for a password for the postgres database..."
    sudo passwd postgres  # First time after install
fi

# Start PostgreSQL database
sudo service postgresql start

# Create the 'wts' user with 'team3' password, ignore error if already exists
expect <<EOF
    spawn sudo -iu postgres createuser -P -e -s wts
    expect "Enter password for new role:"
    send "team3\r"
    expect "Enter it again:"
    send "team3\r"
    expect eof
EOF

# Initialize the database
python3 init_db.py

# Run the flask app
export FLASK_DEBUG=1
flask run

deactivate
