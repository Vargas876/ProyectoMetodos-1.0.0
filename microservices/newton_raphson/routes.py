from flask import Blueprint, request, jsonify, render_template
from .logic import newton_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('calculator.html')

@main.route('/newton_raphson', methods=['POST'])
def newton_raphson_endpoint():
    data = request.get_json()
    return newton_controller.controller_newton(data)
