from flask import Blueprint
from flask_cors import CORS

bp = Blueprint('api/v1', __name__)
CORS(bp)

from app.api import routes
