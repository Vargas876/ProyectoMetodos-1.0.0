from flask import Blueprint, request, jsonify, render_template
from .logic import trapecio_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/trapezoidal', methods=['POST'])
def trapezoidal_endpoint():
    data = request.get_json()
    return trapecio_controller.controller_trapecio(data)
