from urllib.request import urlopen
import urllib.parse
import json
import tmdbsimple as tmdb
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON as SQL_JSON

app = Flask(__name__)

apiKey = "523e00cfc7fcc6bed883c38162ea974d"
searchRequest = "https://api.themoviedb.org/3/search/multi?api_key={}&language={}&query={}&include_adult=false"
providerRequest = "https://api.themoviedb.org/3/{}/{}/watch/providers?api_key={}"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wts:team3@localhost:5432/wts_db"
db = SQLAlchemy(app)

tmdb.API_KEY = apiKey
# Recommended by the tmdbsimple devs, so if the site is down the code won't get stuck there
tmdb.REQUESTS_TIMEOUT = 5


class TVResult(db.Model):
    __tablename__ = 'TVResults'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    providers = db.Column(SQL_JSON)
    last_updated = db.Column(db.DateTime(timezone=True),
                             server_default=db.func.now())

    def __repr__(self):
        return f'<TVResult: {self.title}>'


class MovieResult(db.Model):
    __tablename__ = 'MovieResults'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    providers = db.Column(SQL_JSON)
    last_updated = db.Column(db.DateTime(timezone=True),
                             server_default=db.func.now())

    def __repr__(self):
        return f'<MovieResult: {self.title}>'


@app.route('/')
def home():
    db.drop_all()  # dev trigger to dump database
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        db.create_all()
        """ results = TVResult.query.all()
        for r in results:
            print(r) """

        q = request.args.get('q')
        if q is None or q == '':
            return redirect(url_for('home'))
        q = q.strip()
        provider = request.args.get('provider')
        results = getResults(q)
        return render_template("search.html", q=q, provider=provider, results=results)

    return redirect(url_for('home'))


def getResults(q):
    search = tmdb.Search()
    search.multi(query=q)
    results = []

    for result in search.results:
        if result["media_type"] == "person":
            continue

        id = int(result["id"])
        media_type = result["media_type"]
        title = result["title"] if media_type == "movie" else result["name"]

        providerResponse = urlopen(
            providerRequest.format(media_type, id, apiKey))
        providers = json.loads(providerResponse.read())["results"]

        # Replace with filtering
        providers = providers.get("US")

        if media_type == "tv":
            newResult = TVResult(id=id, title=title, providers=providers)
        else:  # Movie
            newResult = MovieResult(id=id, title=title, providers=providers)

        results.append(newResult)
        if providers:
            print(result["id"], newResult.title, media_type, type(providers), providers.keys())

        #db.session.add(newResult)
        #db.session.commit()

    return results
