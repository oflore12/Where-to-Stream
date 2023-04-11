from urllib.request import urlopen
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
    keyword = db.Column(db.ARRAY(db.String(200)))

    def __repr__(self):
        return f'<TVResult: {self.title}>'


class MovieResult(db.Model):
    __tablename__ = 'MovieResults'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    providers = db.Column(SQL_JSON)
    last_updated = db.Column(db.DateTime(timezone=True),
                             server_default=db.func.now())
    keyword = db.Column(db.ARRAY(db.String(200)))

    def __repr__(self):
        return f'<MovieResult: {self.title}>'


class Query(db.Model):
    __tablename__ = 'Queries'
    id = db.Column(db.Integer, primary_key=True)
    q = db.Column(db.String(100))

    def __repr__(self):
        return f'<Query: {self.q}>'


class QueryResultMapping(db.Model):
    __tablename__ = 'QueryResultMappings'
    id = db.Column(db.Integer, primary_key=True)
    tv_result = db.Column(db.Integer, db.ForeignKey(
        'TVResults.id'), nullable=True)
    movie_result = db.Column(db.Integer, db.ForeignKey(
        'MovieResults.id'), nullable=True)
    q = db.Column(db.Integer, db.ForeignKey('Queries.id'), nullable=False)

    def __repr__(self):
        return f'<QueryResultMapping: {self.tv_result}, {self.movie_result}, {self.q}>'


@app.route('/')
def home():
    # Put in init_db
    db.drop_all()
    db.create_all()
    db.session.add(TVResult(id=-1))
    db.session.add(MovieResult(id=-1))
    db.session.commit()
    # --------------

    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        q = request.args.get('q')
        if q is None or q == '':
            return redirect(url_for('home'))
        q = q.strip()
        provider = request.args.get('provider')
        results = getResults(q)
        return render_template("search.html", q=q, provider=provider, results=results, country="US")

    return redirect(url_for('home'))


def getResults(q):
    search = tmdb.Search()
    cached_q = Query.query.filter_by(q=q).first()
    results = []

    if cached_q is None:
        newQuery = Query(q=q)
        db.session.add(newQuery)
        db.session.commit()

        search.multi(query=q)

        for result in search.results:
            if result["media_type"] == "person":
                continue

            id = int(result["id"])
            media_type = result["media_type"]
            title = result["title"] if media_type == "movie" else result["name"]

            providerResponse = urlopen(
                providerRequest.format(media_type, id, apiKey))
            providers = json.loads(providerResponse.read())["results"]

            tv_id = -1
            movie_id = -1
            if media_type == "tv":  # TV
                tv_id = id
                newResult = TVResult(
                    id=tv_id, title=title, providers=providers)
            else:  # Movie
                movie_id = id
                newResult = MovieResult(
                    id=movie_id, title=title, providers=providers)

            results.append(newResult)

            db.session.add(newResult)
            db.session.commit()

            newQueryResultMapping = QueryResultMapping(
                tv_result=tv_id, movie_result=movie_id, q=newQuery.id)

            db.session.add(newQueryResultMapping)
            db.session.commit()
    else:
        cached_result_ids = QueryResultMapping.query.filter_by(
            q=cached_q.id).all()

        for cached_result_id in cached_result_ids:
            currentResult = None

            if cached_result_id.tv_result != -1:  # TV
                currentResult = TVResult.query.filter_by(
                    id=cached_result_id.tv_result).first()
            else:  # Movie
                currentResult = MovieResult.query.filter_by(
                    id=cached_result_id.movie_result).first()
            
            
            				
            
            	

            results.append(currentResult)

    return results
