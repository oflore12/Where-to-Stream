# CMSC447Project
This is the repository for CMSC447 Project.

## Usage
To instal packages needed for Python and Flask, run these commands:

- `sudo apt install -y python3-pip`
- `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
- `sudo apt install -y python3-venv`

Make sure you're in the CMSC447Project directory and run:

- `python3 -m venv env`

To activate environment, make sure you're in the CMSC447Project directory and run:

- `source env/bin/activate`
	
Once you see (env) prior to your username in the terminal, run:

- `pip install -r requirements.txt`

To run Flask application
	
- `export FLASK_APP=main`
- `export FLASK_ENV=development`
- `flask run`

In the VM, open a web browser and go to http://127.0.0.1:5000/. You should be able to see the web page.
