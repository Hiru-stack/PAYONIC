from flask import Blueprint

bp = Blueprint('vendor', __name__)

from app.vendor import routes
