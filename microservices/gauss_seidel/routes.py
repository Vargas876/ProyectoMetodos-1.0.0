from flask import Blueprint, request, jsonify, render_template
from .logic import gauss_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('calculator.html')


@main.route('/gauss_seidel', methods=['POST'])
def gauss_seidel_endpoint():
    data = request.get_json()
    return gauss_controller.controller_gauss(data)
