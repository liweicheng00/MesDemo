from flask_restful import Resource, reqparse


class User (Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help='Email is required')
    # parser.add_argument('password', required=True, help='Password is required')

    def get(self, name):
        print('user get')
        return [name]

    def post(self, name):
        arg = self.parser.parse_args()
        return {
            'message': 'Insert user success',
            'email': arg['email'],
            'name': name
        }

    def put(self, name):
        pass

    def delete(self, name):
        pass
