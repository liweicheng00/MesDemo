import os
from dotenv import load_dotenv
load_dotenv()

from main.config import config
from flask import Flask, render_template, request, abort
from flask_cors import CORS
from flask_login import LoginManager, current_user
from flask_principal import Principal, identity_loaded, RoleNeed
from flask_apscheduler import APScheduler
from flask_principal import Permission, RoleNeed
from flask_restful import Api
import logging

env = os.environ.get('ENV')
if env:
    pass
else:
    env = 'development'

app = Flask(__name__, instance_relative_config=True)

app.config.from_object(config[env])  # from ./config.py


# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# app.config.from_pyfile('config.py')  # from ./instance/config.py
app_config = app.config


handler = logging.FileHandler('flask.log')
app.logger.addHandler(handler)


'''定時任務'''
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
from main import task
# cors = CORS(app)
# socketio = SocketIO(app, async_mode=None)

# '''建立socketIO通道'''
# socketio = SocketIO(app, async_mode=None)
# from main.socket_io import init_socket, init_socket_test
# init_socket(socketio)
# init_socket_test(socketio)
'''restFul api'''
from main.resources.user import User, Login
api = Api(app)
api.add_resource(User, "/api/user")
api.add_resource(Login, "/api/login")


'''登入需求'''
login_manager = LoginManager(app)

login_manager.login_view = 'auth.login'  # 自動導引到登入頁面
from main.model import User
@login_manager.user_loader  # 回傳登入物件資訊，供current_user使用
def load_user(user):
    user_obj = User.query.filter_by(id=user).first()
    return user_obj


'''權限管理'''
principal = Principal(app)
@identity_loaded.connect_via(app)  # 取得當前使用者權限
def on_identity_loaded(sender, identity):
    identity.user = current_user

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    # if hasattr(identity.user, 'auth'):
    #     identity.provides.add(RoleNeed(identity.user.auth))
    if hasattr(identity.user, 'role'):
        for r in identity.user.role:
            identity.provides.add(RoleNeed(r.role))


'''關閉資料庫連接'''
from main.model import AuthManager, db_session as db1
@app.teardown_appcontext
def shutdown_session(exception=None):  # exception=None 很重要
    db1.remove()


"""request執行前"""
@app.before_first_request
def before_first_request():
    pass


@app.before_request
def before_request():
    q_per = AuthManager.query.filter(AuthManager.route_name == request.path).all()
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

            # print(per.can())
            if current_user.username == 'god':
                return
            if not per.can():
                abort(403)

    else:
        # print(request.path, "is not set auth.")
        pass


'''設定藍圖，提供url_for引導到指定url'''
from main.mes import bp  # 登入、使用者、權限功能
app.register_blueprint(bp)
app.add_url_rule("/", endpoint='index')

from main.mes.framework import bp  # 主要頁面框架功能、功能測試
app.register_blueprint(bp)
app.add_url_rule("/frame", endpoint='index')

from main.mes.production import bp  # 現場管理功能
app.register_blueprint(bp)
app.add_url_rule("/production", endpoint='index')

from main.mes.schedule import bp  # 生產管理功能
app.register_blueprint(bp)
app.add_url_rule("/schedule", endpoint='index')


from main.mes.revise import bp  # 數據管理功能
app.register_blueprint(bp)
app.add_url_rule("/revise", endpoint='index')


@app.route('/hello')
def hello():
    # socketio.emit('my_event', 'someone say hi')
    app.logger.debug('debug log test')
    app.logger.info('info log test')
    app.logger.warning('warn log test')
    return 'hello'



if __name__ == '__main__':
    app.run(port='8080', host="0.0.0.0")
    # socketio.run(app, debug=True)
