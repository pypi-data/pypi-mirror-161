import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from hmac import compare_digest

from api.models.user import UserModel

_user_parser = reqparse.RequestParser() # _ you should not import it from somewhere else because private
_user_parser.add_argument('username', type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument('password', type=str, required=True, help="This field cannot be blank")


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created succesfully."}, 201


class UserLogin(Resource):
    # Endpoint to authenticate with JWT extended

    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data['username'])

        # check password
        if user and compare_digest(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {'message': 'Invalid credentials'}, 401

        # create access token
        # create refresh token

