# CMSC447Project
This is the repository for CMSC447 Project.

## Usage
To install packages needed for Python and Flask, run these commands:

- `sudo apt install -y python3-pip`
- `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
- `sudo apt install -y python3-venv`
- `sudo apt install -y postgresql postgresql-contrib`

Start the PostgreSQL database:

- `sudo passwd postgres` (1st time after install)
- `sudo service postgresql start`

New way to create the PostgreSQL user and database:

- `sudo -iu postgres createuser -P -e -s wts`
- Enter password `team3` and confirm password
- `python3 init_db.py`

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

## Run Application After the initial installation and creatation of database
- `sudo service postgresql start`
- `python3 init_db.py`
- `export FLASK_APP=main`
- `export FLASK_ENV=development`
- `flask run`

## Testing
In the Python environment, simply run `pytest` to run a test session on all testing files. All testing files are located in the *tests/* directory.

To run a specific testing file, run `pytest test/<name_of_test>.py`.
