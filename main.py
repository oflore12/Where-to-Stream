import tmdbsimple as tmdb
from flask import Flask, render_template, request, url_for, redirect
<<<<<<< HEAD
from sqlalchemy import text
from CMSC447Project.rescources.sharedDB.sharedDB import db
from CMSC447Project.rescources.models.models import *
=======
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSON as SQL_JSON
>>>>>>> e57eabe5ef42acf6cc63f0b7c6e819213db3ffdf

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wts:team3@localhost:5432/wts_db"
db.init_app(app)

tmdb.API_KEY = "523e00cfc7fcc6bed883c38162ea974d"
# As recommended by the tmdbsimple developers, this timeout ensures the code won't get stuck if TMDb is down
# TODO: add pretty error message when this happens...
tmdb.REQUESTS_TIMEOUT = 5

# Defines the expiration time for cached API results
CACHE_CLOCK = "1 minute"

@app.route('/')
def home():
    db.create_all()
    if not TVResult.query.filter_by(id=-1).first():
        db.session.add(TVResult(id=-1))
        db.session.commit()
    if not MovieResult.query.filter_by(id=-1).first():
        db.session.add(MovieResult(id=-1))
        db.session.commit()

    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        q = request.args.get('q')
        # If 'q' is empty or not provided, redirect to home page
        if not q:
            return redirect(url_for('home'))

        # Remove whitespace from 'q'
        q = q.strip()

        provider = request.args.get('provider')
        results = getResults(q, provider)

        return render_template("search.html", q=q, provider=provider, results=results, country="US")

    return redirect(url_for('home'))


# The function takes a search query (and provider to filter by) and returns a list of results
def getResults(q, providerFilter):
    search = tmdb.Search()
    # Check if the query is already cached in the 'Query' table
    cached_q = Query.query.filter_by(q=q).first()
    results = []

    # If query not cached
    if not cached_q:
        newQuery = Query(q=q)
        db.session.add(newQuery)
        db.session.commit()

        # Search using the 'tmdb' API (primarily for retrieving IDs)
        search.multi(query=q)

        for result in search.results:
            if result["media_type"] == "person":
                continue

            id = int(result["id"])
            media_type = result["media_type"]
            title = result["title"] if media_type == "movie" else result["name"]

            # If media type is TV
            if media_type == "tv":
                # Check if the TV result is already cached
                exists = TVResult.query.filter_by(id=id).first()
                # If not cached
                if not exists:
                    # Retrieve watch providers and create new 'TVResult' instance
                    providerSearch = tmdb.TV(id)
                    providerSearch.watch_providers()
                    newResult = TVResult(
                        id=id, title=title, providers=providerSearch.results)
                # If cached, perform TV caching procedure
                else:
                    newResult = TVCache(id)
            # If media type is movie
            else:
                # Check if the movie result is already cached
                exists = MovieResult.query.filter_by(id=id).first()
                # If not cached
                if not exists:
                    # Retrieve watch providers and create new 'MovieResult' instance
                    providerSearch = tmdb.Movies(id)
                    providerSearch.watch_providers()
                    newResult = MovieResult(
                        id=id, title=title, providers=providerSearch.results)
                # If cached, perform movie caching procedure
                else:
                    newResult = MovieCache(id)

            # If new result not cached, add to the database and commit change
            if not exists:
                db.session.add(newResult)
                db.session.commit()

            # Create a new 'QueryResultMapping' instance and add to the database and commit changes
            newQueryResultMapping = QueryResultMapping(
                tv_result=id if media_type == "tv" else -1,
                movie_result=id if media_type == "movie" else -1,
                q=newQuery.id)

            db.session.add(newQueryResultMapping)
            db.session.commit()
            
            if providerFilter != "All":
            	if providerCheck(newResult, providerFilter):
            		results.append(newResult)
            else:
            	results.append(newResult)
    # If query is cached
    else:
        # Retrieve cached result IDs from the 'QueryResultMapping' table
        cached_result_ids = QueryResultMapping.query.filter_by(
            q=cached_q.id).all()

        # Perform caching procedure for each result
        for cached_result_id in cached_result_ids:
            # If the cached result is a TV result
            if cached_result_id.tv_result != -1:
                currentResult = TVCache(cached_result_id.tv_result)
            # If the cached result is a movie result
            else:
                currentResult = MovieCache(cached_result_id.movie_result)

			# If there is no provider filter chosen, default will be "All"
            if providerFilter != "all":
            	# Check if the current movie or TV show is available on the specified streaming service
            	if providerCheck(currentResult, providerFilter):
            		# Add to results if it is
            		results.append(currentResult)
            # If no filter is chosen, always add current TV show or movie to results
            else:
            	results.append(currentResult)

    return results


def TVCache(id):
    # Check if there is a cached result in the database that is not "stale"
    currentResult = db.session.query(TVResult).from_statement(sqlalchemy.text("""
        SELECT
            "TVResults".id AS "TVResults_id", "TVResults".title AS "TVResults_title",
            "TVResults".providers AS "TVResults_providers", "TVResults".last_updated AS "TVResults_last_updated"
        FROM "TVResults"
        WHERE "TVResults".id = %(id_1)s
            AND "TVResults".last_updated > CURRENT_TIMESTAMP - interval '%(cacheClock_1)s'
        """ % {'id_1': id, 'cacheClock_1': CACHE_CLOCK})).first()

    # If the cached result is stale, retrieve the latest provider data and update the cache
    if (not currentResult):
        recacheSearch = tmdb.TV(id)
        recacheSearch.watch_providers()
        currentResult = TVResult.query.filter_by(id=id).first()
        currentResult.providers = recacheSearch.results
        currentResult.last_updated = db.func.current_timestamp()
        db.session.commit()

    return currentResult


def MovieCache(id):
    # Check if there is a cached result in the database that is not "stale"
    currentResult = db.session.query(MovieResult).from_statement(sqlalchemy.text("""
        SELECT
            "MovieResults".id AS "MovieResults_id", "MovieResults".title AS "MovieResults_title",
            "MovieResults".providers AS "MovieResults_providers", "MovieResults".last_updated AS "MovieResults_last_updated"
        FROM "MovieResults"
        WHERE "MovieResults".id = %(id_1)s
            AND "MovieResults".last_updated > CURRENT_TIMESTAMP - interval '%(cacheClock_1)s'
        """ % {'id_1': id, 'cacheClock_1': CACHE_CLOCK})).first()

    # If the cached result is stale, retrieve the latest provider data and update the cache
    if (not currentResult):
        recacheSearch = tmdb.Movies(id)
        recacheSearch.watch_providers()
        currentResult = MovieResult.query.filter_by(id=id).first()
        currentResult.providers = recacheSearch.results
        currentResult.last_updated = db.func.current_timestamp()
        db.session.commit()

    return currentResult

# Checks if a result (TV show or movie) is available on a service
def providerCheck(result, providerFilter):
	# First check if the media is available in the specified country (currently only US)
	if 'US' in result.providers:
		# Check each purchase option
		for purchaseOpt, providers in result.providers["US"].items():
			# Skip over the provided link
			if purchaseOpt == "link":
				continue
			else:
				# Return True if any of the providers match the filter
				for provider in providers:
					if provider["provider_name"].lower() == providerFilter:
						return True
	# Return False if the media is not available in chosen country or not on the specified provider
	return False
	
