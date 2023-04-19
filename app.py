import tmdbsimple as tmdb
from flask import Flask, render_template, request, url_for, redirect
import sqlalchemy
from sqlalchemy.orm.session import make_transient
from .resources.sharedDB.sharedDB import db
from .resources.models.models import *

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wts:team3@localhost:5432/wts_db"

db.init_app(app)

tmdb.API_KEY = "523e00cfc7fcc6bed883c38162ea974d"
# As recommended by the tmdbsimple developers, this timeout ensures the code won't get stuck if TMDb is down
tmdb.REQUESTS_TIMEOUT = 5

# Defines the expiration time for cached API results
CACHE_CLOCK = "1 minute"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    useDBModels()

    if request.method == 'GET':
        q = request.args.get('q')
        # If 'q' is empty or not provided, redirect to home page
        if not q:
            return redirect(url_for('home'))
        # Remove whitespace from 'q'
        q = q.strip()

        provider = request.args.get('provider')

        try:
            results = getResults(q, provider)
        except Exception as e:
            print(e)
            results = []

        return render_template("search.html", q=q, provider=provider, results=results, country="US")

    return redirect(url_for('home'))


@app.route('/filter')
def filter():
    return render_template('filter.html')


@app.route('/suggestions')
def suggestions():
    # Custom API for suggested search keywords
    search = tmdb.Search()
    q = request.args.get('q')
    search.multi(query=q)
    suggestions = []
    counter = 0
    for result in search.results:
        if result["media_type"] == "tv" and counter < 10 and result['name'].lower() not in suggestions:
            suggestions.append(result['name'].lower())
            counter += 1
        elif result["media_type"] == "movie" and counter < 10 and result['title'].lower() not in suggestions:
            suggestions.append(result['title'].lower())
            counter += 1
    return suggestions


def getResults(q, providerFilter):
    # The function takes a search query (and provider to filter by) and returns a list of results
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
                    try:
                        year = result["first_air_date"].split('-')[0]
                    except:
                        year = ''

                    # Retrieve watch providers and create new 'TVResult' instance
                    providerSearch = tmdb.TV(id)
                    providerSearch.watch_providers()
                    newResult = TVResult(
                        id=id, title=title, year=year, providers=providerSearch.results)
                # If cached, perform TV caching procedure
                else:
                    newResult = TVCache(id)
            # If media type is movie
            else:
                try:
                    year = result["release_date"].split('-')[0]
                except:
                    year = ''

                # Check if the movie result is already cached
                exists = MovieResult.query.filter_by(id=id).first()
                # If not cached
                if not exists:
                    # Retrieve watch providers and create new 'MovieResult' instance
                    providerSearch = tmdb.Movies(id)
                    providerSearch.watch_providers()
                    newResult = MovieResult(
                        id=id, title=title, year=year, providers=providerSearch.results)
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

            # If there is no provider filter, add the current result to results
            if providerFilter == "all":
                results.append(newResult)
            else:
                # Only do filtering AFTER commiting the unchanged version to the database
                providerCheck(newResult, providerFilter)
                if 'US' in newResult.providers.keys() and len(newResult.providers['US']) != 0:
                    db.session.expunge(newResult)
                    make_transient(newResult)
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

            # If there is no provider filter, add the current result to results
            if providerFilter == "all":
                results.append(currentResult)
            else:
                providerCheck(currentResult, providerFilter)
                if 'US' in currentResult.providers.keys() and len(currentResult.providers['US']) != 0:
                    db.session.expunge(currentResult)
                    make_transient(currentResult)
                    results.append(currentResult)

    return results


def TVCache(id):
    # Check if there is a cached result in the database that is not "stale"
    currentResult = db.session.query(TVResult).from_statement(sqlalchemy.text("""
        SELECT
            "TVResults".id AS "TVResults_id", "TVResults".title AS "TVResults_title", "TVResults".year AS "TVResults_year",
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
            "MovieResults".id AS "MovieResults_id", "MovieResults".title AS "MovieResults_title", "MovieResults".year AS "MovieResults_year",
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


def providerCheck(result, providerFilter):
    # Function to check if result is on a specified provider, deletes providers
    # that do not match the filter

    # Checking for if providers are available in specified country (just US for now)
    if 'US' in result.providers.keys():
        # List of keys in the country dict to delete (since they are empty or the link)
        itemsToDelete = []
        for purchaseType, providers in result.providers['US'].items():
            # Always mark the link for deletion, we don't use it
            if (purchaseType == 'link'):
                itemsToDelete.append(purchaseType)
            # Checking each provider if it contains a key string from the providerFilter
            # in the provider name and adding to the list to delete it if it does not
            else:
                # Iterating over a sliced copy of the list so removals can occur in iteration
                for provider in providers[:]:
                    # If the provider name does not contain the filter key string, remove it
                    if providerFilter not in provider["provider_name"].lower():
                        providers.remove(provider)
                # If all of the providers have been removed from a purchaseType, mark it for deletion
                if len(providers) == 0:
                    itemsToDelete.append(purchaseType)
        # Delete all the purchaseTypes marked for deletion from the providers dict
        for item in itemsToDelete:
            del result.providers['US'][item]


def useDBModels():
    db.create_all()
    if not TVResult.query.filter_by(id=-1).first():
        db.session.add(TVResult(id=-1))
        db.session.commit()
    if not MovieResult.query.filter_by(id=-1).first():
        db.session.add(MovieResult(id=-1))
        db.session.commit()
