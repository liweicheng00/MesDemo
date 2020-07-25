from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash, generate_password_hash
from flask_principal import identity_changed, AnonymousIdentity, Identity
from flask import (
    flash, redirect, url_for, current_app, session, abort, request
)
from flask_login import login_user, logout_user, login_required, current_user
from model import User as User_model, Role, db_session as db1


class User (Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('ID', required=True, help='ID is required')
    parser.add_argument('name', required=False, help='name is required')
    parser.add_argument('pwd', required=True, help='pwd is required')
    parser.add_argument('pwd_confirm', required=True, help='pwd_confirm is required')
    parser.add_argument('old_pwd', required=False, help='pwd_confirm is required')

    def get(self, name):
        print('user get')
        return [name]

    def post(self):
        arg = self.parser.parse_args()
        msg = None
        if not arg['pwd'] == arg['pwd_confirm']:
            msg = 'Password is not the same.'
        elif User_model.query.filter_by(username=arg['ID']).first() is not None:
            msg = 'user_name {} is already registered.'.format(arg['ID'])

        if msg is None:
            new_client = User_model(username=arg['ID'], password=generate_password_hash(arg['pwd']), name=arg['name'])
            db1.add(new_client)
            db1.commit()
            msg = 'register success'
            return {"msg": msg}

        return {
            "msg": msg
        }

    def put(self):
        arg = self.parser.parse_args()
        user = User_model.query.filter_by(username=arg['ID']).first()
        if user is not None:
            if check_password_hash(user.password, arg.old_pwd):
                if arg['pwd'] == arg['pwd_confirm']:
                    user.password = generate_password_hash(arg['pwd'])
                    db1.add(user)
                    db1.commit()
                    msg = 'revise success'
                else:
                    msg = "password not match."
            else:
                msg = 'Incorrect password.'

        else:
            msg = "no this user"
        return {
            'msg': msg
        }

    def delete(self):
        pass


class Login (Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('ID', required=True, help='ID is required')
    parser.add_argument('pwd', required=True, help='pwd is required')

    def get(self):
        if current_user.is_anonymous:
            return {
                "msg": "not login",
                "user": None
            }
        else:
            user = current_user.username
            name = current_user.name
            return {
                "user": {
                    "username": user,
                    "name": name
                }
            }

    def post(self):
        arg = self.parser.parse_args()

        user = User_model.query.filter_by(username=arg.ID).first()
        error = None
        if user is None:
            error = 'ID is not exist.'
        elif not check_password_hash(user.password, arg.pwd):
            error = 'Incorrect password.'

        if error is None:
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            login_user(user)
            return {"msg": error,
                    "user": {
                        "username": user.username,
                        "name": user.name
                    }}
        return {
            "msg": error,
            "user": None
        }

    def put(self, name):
        pass

    def delete(self):
        logout_user()
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)
        identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
        return {"msg": "logout!"}


