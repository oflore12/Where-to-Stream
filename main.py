import sqlalchemy
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        q = request.args.get('q')
        service = request.args.get('service')
        print([q, service])

    return render_template('home.html')
