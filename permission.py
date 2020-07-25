from flask import current_app
from flask_principal import Permission, RoleNeed
from functools import wraps
from model import *
# """權限管理"""
# admin_permission = Permission(RoleNeed('super_admin'))
# user_permission = Permission(RoleNeed('user'))


def auth_manager(func):
    @wraps(func)
    def wrapper():

        route = func.__name__
        q_per = AuthManager.query.filter(AuthManager.route_name == '/'+route).all()
        if q_per:
            role = set()
            for p in q_per:
                permission = p.permission
                if permission:
                    roles = permission.split(',')
                    role.update(roles)

            if role:
                per = Permission()
                for r in role:
                    if r:
                        per = per.union(Permission(RoleNeed(r)))

                @per.require(http_exception=403)
                def f():
                    return func()
                return f()
            else:
                return func()
        else:
            return func()
    return wrapper

