import psycopg2
from resources.database.database import db

# Before running this, make sure to create the 'wts' postgresql user

# New user and password, less of a placeholder
conn = psycopg2.connect(
   database="postgres",
   user='wts',
   password='team3',
   host='127.0.0.1',
   port= '5432'
)

# So each line does not need a commit and an execute
conn.autocommit = True

cursor = conn.cursor()

cursor.execute('DROP DATABASE IF EXISTS wts_db')
cursor.execute('CREATE DATABASE wts_db')

print("Where To Stream database sucessfully initialized.")

#Closing the connection
conn.close()
