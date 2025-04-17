from flask import Blueprint, request, jsonify, render_template
from .logic import broyden_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/broyden', methods=['POST'])
def broyden_endpoint():
    data = request.get_json()
    return Broyden_controller.controller_broyden(data)