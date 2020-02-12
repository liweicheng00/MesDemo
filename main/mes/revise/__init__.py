from flask import Blueprint
bp = Blueprint('revise', __name__)

from . import anomaly_revise, bad_revise, bom_revise, material_revise, product_revise, upload_data, data_query
