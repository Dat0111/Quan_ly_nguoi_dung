from flask import Blueprint
from flask_restful import Resource, Api
from models import User  # Import from models.py

api = Blueprint('api', __name__)
rest_api = Api(api)

class UserList(Resource):
    def get(self):
        users = User.query.all()
        return [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]

class UserDetail(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return {'id': user.id, 'username': user.username, 'email': user.email}
        return {'message': 'User not found'}, 404

rest_api.add_resource(UserList, '/users')
rest_api.add_resource(UserDetail, '/users/<int:user_id>')
