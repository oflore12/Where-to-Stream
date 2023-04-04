from urllib.request import urlopen
import urllib.parse
import json
import tmdbsimple as tmdb
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

apiKey = "523e00cfc7fcc6bed883c38162ea974d"
searchRequest = "https://api.themoviedb.org/3/search/multi?api_key={}&language={}&query={}&include_adult=false"
providerRequest = "https://api.themoviedb.org/3/{}/{}/watch/providers?api_key={}"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wts:team3@localhost:5432/wts_db"
db = SQLAlchemy(app)

tmdb.API_KEY = apiKey
# Recommended by the tmdbsimple devs, so if the site is down the code won't get stuck there
tmdb.REQUESTS_TIMEOUT = 5

class mediaResult(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    media_type = db.Column(db.String(5))
    buy_providers = db.Column(db.ARRAY(db.String(30)))
    flatrate_providers = db.Column(db.ARRAY(db.String(30)))
    rent_providers = db.Column(db.ARRAY(db.String(30)))

    def __repr__(self):
        return f'<Result: {self.title}>'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        db.drop_all()
        db.create_all()
        q = request.args.get('q')
        if q is None or q == '':
            return redirect(url_for('home'))
        q = q.strip()
        provider = request.args.get('provider')
        getResults(q)

    results = mediaResult.query.all()
    return render_template("search.html", q=q, provider=provider, results=results)


def getResults(q):

    search = tmdb.Search()
    response = search.multi(query=q)

    for result in search.results:
        if result["media_type"] == "person":
            continue

        id = int(result["id"])
        media_type = result["media_type"]
        title = result["title"] if media_type == "movie" else result["name"]

        providerResponse = urlopen(providerRequest.format(media_type, id, apiKey))

        #need to work on implementing tmdb simple below once we can figure
        #out how to see providers and add to list with tmdbsimple

        #providerSearch = None
        #if media_type == "movie":
            #providerSearch = tmdb.Movies(id)

            

        #else:
       #     providerSearch = tmdb.TV(id)
        
        r = json.loads(providerResponse.read())["results"]

        #r = providerSearch
        #purchaseOptions = providerSearch.get("US")
        purchaseOptions = r.get("US")
        if purchaseOptions is None:
            continue
        buy = []
        flatrate = []
        rent = []

        for option in purchaseOptions:
            if option == "buy":
                for provider in purchaseOptions[option]:
                    buy.append(provider["provider_name"])
            elif option == "flatrate":
                for provider in purchaseOptions[option]:
                    flatrate.append(provider["provider_name"])
            elif option == "rent":
                for provider in purchaseOptions[option]:
                    rent.append(provider["provider_name"])

        newResult = mediaResult(id=id, title=title, media_type=media_type,
                                buy_providers=buy, flatrate_providers=flatrate, rent_providers=rent)
        db.session.add(newResult)
        db.session.commit()
    return
