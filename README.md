# CMSC447Project
This is the repository for CMSC447 Project.

## Usage
To install packages needed for Python and Flask, run these commands:

- `sudo apt install -y python3-pip`
- `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
- `sudo apt install -y python3-venv`

This test branch also uses postgresql, since it allows for arrays to be stored in columns.
To set that up run these commands:

- `sudo apt install postgresql postgresql-contrib`
- `sudo -iu postgres psql`

The prompt should change from the bash to `postgres=#`, then run these commands:

- `CREATE USER test WITH PASSWORD '447';`
- `CREATE DATABASE test_result`;
- `GRANT ALL PRIVILEGES ON DATABASE test_result TO test;`
- `\q` to exit postgresql

Make sure you're in the CMSC447Project directory and run:

- `python3 -m venv env`

To activate environment, make sure you're in the CMSC447Project directory and run:

- `source env/bin/activate`
	
Once you see (env) prior to your username in the terminal, run (Janky version for the branch):

- `pip install flask`
- `pip install flask_sqlalchemy`
- `pip install Flask psycopg2-binary`

To run Flask application
	
- `export FLASK_APP=main`
- `export FLASK_ENV=development`
- `flask run`

In the VM, open a web browser and go to http://127.0.0.1:5000/. You should be able to see the web page.
Currently this test branch only shows movies and TV shows in the US, and probably not all the possible search results. 

If this doesn't work, my apologies since I havent done any sort of readme/instructions on setting up a program so I may have missed something as I wrote this after coding not as I installed packages/programs -Emmett.
