import tmdbsimple as tmdb
from flask import Flask, render_template, request, url_for, redirect, jsonify
import sqlalchemy
from sqlalchemy.orm.session import make_transient
from .resources.sharedDB.sharedDB import db
from .resources.models.models import *
from flask_markdown import markdown
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
markdown(app)

app.config['SECRET_KEY'] = 'our-secret-key'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wts:team3@localhost:5432/wts_db"

db.init_app(app)

tmdb.API_KEY = "523e00cfc7fcc6bed883c38162ea974d"
# As recommended by the tmdbsimple developers, this timeout ensures the code won't get stuck if TMDb is down
tmdb.REQUESTS_TIMEOUT = 5

# Defines the expiration time for cached API results
CACHE_CLOCK = "1 minute"

login_manager = LoginManager()
login_manager.login_view = 'sign_in'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return UserAccount.query.get(user_id)


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


@app.route('/details/tv/<int:id>', methods=['GET'])
def tvDetails(id):
    item = TVResult.query.filter_by(id=id).first()
    if (current_user.is_authenticated):
        test = Watchlist.query.filter_by(
            tv_id=id, user_id=current_user.get_id()).first()
        item.watchlist = True if test else False
        item.type = 'tv'
    return render_template('details.html', item=item, details=True)


@app.route('/details/movie/<int:id>', methods=['GET'])
def movieDetails(id):
    item = MovieResult.query.filter_by(id=id).first()
    if (current_user.is_authenticated):
        test = Watchlist.query.filter_by(
            movie_id=id, user_id=current_user.get_id()).first()
        item.watchlist = True if test else False
        item.type = 'movie'
    return render_template('details.html', item=item, details=True)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    useDBModels()

    error = None
    if request.method == 'POST':
        # check if that username password pair  is in the database
        exists = UserAccount.query.filter_by(
            username=request.form['username'], password=request.form['password']).first()
        print(exists)

        # returning error if username or password is wrong
        if not exists:
            error = 'Username or password is incorrect, enter the correct information or sign up for an account.'

        # need to set logged in as yes
        # returning home after successful log in
        else:
            login_user(exists)
            next = request.args.get('next')
            return redirect(next or url_for('home'))

    return render_template('sign_in.html', error=error)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    useDBModels()

    error = None
    if request.method == 'POST':

        # check if that username key is in the database return error if is
        exists = UserAccount.query.filter_by(
            username=request.form['username']).first()
        if exists:
            error = 'Username already exists, please sign in instead.'

        # checking if entered passwords match
        elif request.form['password'] != request.form['passwordcheck']:
            error = 'Passwords do not match'

        # returning home after successfully creating account
        else:
            newUser = UserAccount(
                username=request.form['username'], password=request.form['password'])
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser)
            return redirect(url_for('home'))

    return render_template('sign_up.html', error=error)


@app.route('/sign_out', methods=['GET', 'POST'])
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('home'))


@app.route('/watchlist')
@login_required
def watchlist():
    results = []
    itemList = Watchlist.query.filter_by(user_id=current_user.get_id()).all()
    for item in itemList:
        if item.movie_id == -1:
            result = TVResult.query.filter_by(id=item.tv_id).first()
            result.type = 'tv'
        else:
            result = MovieResult.query.filter_by(id=item.movie_id).first()
            result.type = 'movie'
        results.append(result)
    results.reverse()
    return render_template('watchlist.html', results=results)


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


@app.route('/filter')
def filter():
    return render_template('filter.html')


@app.route('/watchlist/add/tv/<int:item_id>')
@login_required
def addTvToWatchlist(item_id):
    useDBModels()

    item = Watchlist.query.filter_by(
        tv_id=item_id, user_id=current_user.get_id()).first()
    if not item:
        try:
            newItem = Watchlist(user_id=current_user.get_id(),
                                tv_id=item_id, movie_id=-1)
            db.session.add(newItem)
            db.session.commit()
            return jsonify({'success': 'TV show added successfully.'}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': 'TV show not found.'}), 404
    return jsonify({'error': 'Could not add TV show.'}), 400


@app.route('/watchlist/add/movie/<int:item_id>')
@login_required
def addMovieToWatchlist(item_id):
    useDBModels()

    item = Watchlist.query.filter_by(
        movie_id=item_id, user_id=current_user.get_id()).first()
    if not item:
        try:
            newItem = Watchlist(user_id=current_user.get_id(),
                                tv_id=-1, movie_id=item_id)
            db.session.add(newItem)
            db.session.commit()
            return jsonify({'success': 'Movie added successfully.'}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': 'Movie not found.'}), 404
    return jsonify({'error': 'Could not add movie.'}), 400


@app.route('/watchlist/remove/tv/<int:item_id>')
@login_required
def removeTVFromWatchlist(item_id):
    useDBModels()

    item = Watchlist.query.filter_by(
        tv_id=item_id, user_id=current_user.get_id()).first()
    if not item:
        return jsonify({'error': 'TV show not found.'}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': 'TV show removed successfully.'}), 200
    except Exception as e:
        print(e)
    return jsonify({'error': 'Could not remove TV show.'}), 400


@app.route('/watchlist/remove/movie/<int:item_id>')
@login_required
def removeMovieFromWatchlist(item_id):
    useDBModels()

    item = Watchlist.query.filter_by(
        movie_id=item_id, user_id=current_user.get_id()).first()
    if not item:
        return jsonify({'error': 'Movie not found.'}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': 'Movie removed successfully.'}), 200
    except Exception as e:
        print(e)
    return jsonify({'error': 'Could not remove movie.'}), 400


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
            score = round(result["vote_average"] * 10, 1)
            score_count = result["vote_count"]
            poster = result["poster_path"]
            backdrop = result["backdrop_path"]

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

                    tvSearch = tmdb.TV(id)

                    # Retrieve watch providers and create new 'TVResult' instance
                    tvSearch.watch_providers()
                    providerResults = tvSearch.results

                    tvSearch.reviews()
                    reviewResults = tvSearch.results

                    newResult = TVResult(
                        id=id, title=title, year=year, score=score, score_count=score_count, poster=poster, backdrop=backdrop, providers=providerResults, reviews=reviewResults)
                # If cached, perform TV caching procedure
                else:
                    newResult = TVCache(id)
                newResult.type = 'tv'
                if (current_user.is_authenticated):
                    item = Watchlist.query.filter_by(
                        tv_id=id, user_id=current_user.get_id()).first()
                    newResult.watchlist = True if item else False
            # If media type is movie
            else:
                # Check if the movie result is already cached
                exists = MovieResult.query.filter_by(id=id).first()
                # If not cached
                if not exists:
                    try:
                        year = result["release_date"].split('-')[0]
                    except:
                        year = ''

                    movieSearch = tmdb.Movies(id)

                    # Retrieve watch providers and create new 'MovieResult' instance
                    movieSearch.watch_providers()
                    providerResults = movieSearch.results

                    movieSearch.reviews()
                    reviewResults = movieSearch.results

                    newResult = MovieResult(
                        id=id, title=title, year=year, score=score, score_count=score_count, poster=poster, backdrop=backdrop, providers=providerResults, reviews=reviewResults)
                # If cached, perform movie caching procedure
                else:
                    newResult = MovieCache(id)
                newResult.type = 'movie'
                if (current_user.is_authenticated):
                    item = Watchlist.query.filter_by(
                        movie_id=id, user_id=current_user.get_id()).first()
                    newResult.watchlist = True if item else False

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
                currentResult.type = 'tv'
                if (current_user.is_authenticated):
                    item = Watchlist.query.filter_by(
                        tv_id=cached_result_id.tv_result, user_id=current_user.get_id()).first()
                    currentResult.watchlist = True if item else False
            # If the cached result is a movie result
            else:
                currentResult = MovieCache(cached_result_id.movie_result)
                currentResult.type = 'movie'
                if (current_user.is_authenticated):
                    item = Watchlist.query.filter_by(
                        movie_id=cached_result_id.movie_result, user_id=current_user.get_id()).first()
                    currentResult.watchlist = True if item else False

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
            "TVResults".id AS "TVResults_id", "TVResults".title AS "TVResults_title", "TVResults".year AS "TVResults_year", "TVResults".score AS "TVResults_score",
            "TVResults".score_count AS "TVResults_score_count", "TVResults".poster AS "TVResults_poster", "TVResults".providers AS "TVResults_providers",
            "TVResults".reviews AS "TVResults_reviews", "TVResults".last_updated AS "TVResults_last_updated", "TVResults".backdrop AS "TVResults_backdrop"
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
            "MovieResults".id AS "MovieResults_id", "MovieResults".title AS "MovieResults_title", "MovieResults".year AS "MovieResults_year", "MovieResults".score AS "MovieResults_score",
            "MovieResults".score_count AS "MovieResults_score_count", "MovieResults".poster AS "MovieResults_poster", "MovieResults".providers AS "MovieResults_providers",
            "MovieResults".reviews AS "MovieResults_reviews", "MovieResults".last_updated AS "MovieResults_last_updated", "MovieResults".backdrop AS "MovieResults_backdrop"
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
