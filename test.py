from flask import Flask

app = Flask(__name__)

@app.route('/')
def testing():
    return '<h1>testing, testing, CMSC447Project</h1>'
