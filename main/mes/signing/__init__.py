from flask import Blueprint
bp = Blueprint('signing', __name__)

from . import sign_manager
