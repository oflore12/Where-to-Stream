from CMSC447Project.resources.sharedDB.sharedDB import db
from sqlalchemy.dialects.postgresql import JSON as SQL_JSON

class TVResult(db.Model):
    __tablename__ = 'TVResults'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(500))
    providers = db.Column(SQL_JSON)
    last_updated = db.Column(db.DateTime(timezone=True),
                             server_default=db.func.now(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<TVResult: {self.title} ({self.id})>'


class MovieResult(db.Model):
    __tablename__ = 'MovieResults'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(500))
    providers = db.Column(SQL_JSON)
    last_updated = db.Column(db.DateTime(timezone=True),
                             server_default=db.func.now(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<MovieResult: {self.title} ({self.id})>'


class Query(db.Model):
    __tablename__ = 'Queries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    q = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<Query: {self.q}>'


class QueryResultMapping(db.Model):
    __tablename__ = 'QueryResultMappings'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    q = db.Column(db.Integer, db.ForeignKey('Queries.id'), nullable=False)
    tv_result = db.Column(db.Integer, db.ForeignKey(
        'TVResults.id'))
    movie_result = db.Column(db.Integer, db.ForeignKey(
        'MovieResults.id'))

    def __repr__(self):
        return f'<QueryResultMapping: {self.q}, {self.tv_result}, {self.movie_result}>'
