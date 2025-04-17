from flask import Blueprint, request, jsonify, render_template
from .logic import simpson_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/simpson', methods=['POST'])
def simpson_endpoint():
    data = request.get_json()
    return simpson_controller.controller_simpson(data)
