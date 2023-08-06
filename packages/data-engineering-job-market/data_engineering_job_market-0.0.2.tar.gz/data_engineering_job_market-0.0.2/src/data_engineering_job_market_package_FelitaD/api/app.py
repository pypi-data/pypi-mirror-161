from flask import render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import datetime

from api import create_app
from api.resources.user import UserRegister, UserLogin
from api.resources.job import Job, JobList

app = create_app()
app.app_context().push()

jwt = JWTManager(app)
api = Api(app)

api.add_resource(Job, '/job/<int:id>')
api.add_resource(JobList, '/jobs')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')


@app.route("/")
def hello():
    return render_template('index.html', now=datetime.now())


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/jobs/')
def jobs():
    jobs = JobList().get().get('jobs')

    return render_template('jobs.html', jobs=jobs)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
