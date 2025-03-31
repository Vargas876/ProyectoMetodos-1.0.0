from flask import Blueprint, request, jsonify, render_template
from app.controller import (
    secant_controller
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

@main.route('/secant', methods=['POST'])
def secant_endpoint():
    data = request.get_json()
    return secant_controller.controller_secant(data)
