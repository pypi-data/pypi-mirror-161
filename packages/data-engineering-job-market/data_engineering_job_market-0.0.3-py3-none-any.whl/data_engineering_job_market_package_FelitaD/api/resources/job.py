from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from api.models.job import JobModel


class Job(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('company',
                        type=str,
                        required=True,
                        help='This field cannot be left blank !')
    parser.add_argument('remote',
                        type=int,
                        required=False)

    @jwt_required()
    def get(self, id):
        job = JobModel.find_by_id(id)
        if job:
            return job.json()
        return {'message': 'Item not found'}, 404

    @jwt_required()
    def post(self, id):
        if JobModel.find_by_id(id):
            return {'message': "A job with id '{}' already exists.".format(id)}, 400  # Bad Request, client's fault (should have checked if item existed)

        data = Job.parser.parse_args()
        job = JobModel(id, **data)

        try:
            job.save_to_db()
        except:
            return {'message': "An error occured"}, 500

        return job.json(), 201

    @jwt_required()
    def delete(self, id):
        job = JobModel.find_by_id(id)
        if job:
            job.delete_from_db()

        return {'message': 'Item deleted'}

    @jwt_required()
    def put(self, id):
        data = Job.parser.parse_args()

        job = JobModel.find_by_id(id)

        if job is None:
            job = JobModel(id, **data)
        else:
            job.company = data['company']
            job.remote = data['remote']

        job.save_to_db()

        return job.json()


class JobList(Resource):
    def get(self):
        return {'jobs': [job.json() for job in JobModel.query.all()]}
