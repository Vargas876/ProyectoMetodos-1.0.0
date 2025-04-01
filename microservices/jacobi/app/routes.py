from flask import Blueprint, request, jsonify, render_template
from app.controller import (
    jacobi_controller
)
from app.util import equation as eq
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('calculator.html')


@main.route('/jacobi', methods=['POST'])
def jacobi_endpoint():
    data = request.get_json()
    return jacobi_controller.controller_jacobi(data)
