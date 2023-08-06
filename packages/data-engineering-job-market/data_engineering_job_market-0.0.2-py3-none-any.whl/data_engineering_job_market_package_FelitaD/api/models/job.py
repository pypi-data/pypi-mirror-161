import json

from api.db import db


class JobModel(db.Model):
    """
    Internal representation of the Job resource and helper.
    Client doesn't interact directly with these methods.
    """
    __tablename__ = 'jobs'

    id = db.Column(db.Integer)
    url = db.Column(db.String(500), primary_key=True)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    stack = db.Column(db.String)
    location = db.Column(db.String(100))
    remote = db.Column(db.String(100))
    type = db.Column(db.String(100))
    language = db.Column(db.String(2))
    created_at = db.Column(db.Date)
    text = db.Column(db.Text)

    def __init__(self, id, url, title, company, industry, stack, location, remote, _type, language, created_at, text):
        self.id = id
        self.url = url
        self.title = title
        self.company = company
        self.industry = industry
        self.stack = stack
        self.location = location
        self.remote = remote
        self.type = _type
        self.language = language
        self.created_at = created_at
        self.text = text

    def json(self):
        return {
                'id': self.id,
                'url': self.url,
                'title': self.title,
                'company': self.company,
                'location': self.location,
                'remote': self.remote,
                'type': self.type,
                'industry': self.industry,
                'text': self.text
                }

    @classmethod
    def find_by_id(cls, id):
        return JobModel.query.filter_by(id=id).first()  # returns JobModel instance with init attributes

    def save_to_db(self):
        """ Upsert : update or insert """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
