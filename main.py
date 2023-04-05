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
    buy_providers = db.Column(db.ARRAY(db.String(50)))
    buy_provider_logo = db.Column(db.ARRAY(db.String(50)))
    flatrate_providers = db.Column(db.ARRAY(db.String(50)))
    flatrate_provider_logo = db.Column(db.ARRAY(db.String(50)))
    rent_providers = db.Column(db.ARRAY(db.String(50)))
    rent_provider_logo = db.Column(db.ARRAY(db.String(50)))

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

        r = json.loads(providerResponse.read())["results"]

        purchaseOptions = r.get("US")
        if purchaseOptions is None:
            continue
        buy = []
        buy_logo =[]
        flatrate = []
        flatrate_logo = []
        rent = []
        rent_logo = []

        for option in purchaseOptions:
            if option == "buy":
                for provider in purchaseOptions[option]:
                    buy.append(provider["provider_name"])
                    buy_logo.append(provider["logo_path"])
            elif option == "flatrate":
                for provider in purchaseOptions[option]:
                    flatrate.append(provider["provider_name"])
                    flatrate_logo.append(provider["logo_path"])
            elif option == "rent":
                for provider in purchaseOptions[option]:
                    rent.append(provider["provider_name"])
                    rent_logo.append(provider["logo_path"])

        newResult = mediaResult(id=id, title=title, media_type=media_type,
                                buy_providers=buy, buy_provider_logo = buy_logo, flatrate_providers=flatrate,
                                flatrate_provider_logo = flatrate_logo, rent_providers=rent,
                                rent_provider_logo = rent_logo)
        db.session.add(newResult)
        db.session.commit()
    return
