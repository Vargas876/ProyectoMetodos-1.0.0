from flask import Blueprint, request, jsonify
from .logic import euler_controller
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/euler', methods=['POST'])
def euler_endpoint():
    """Endpoint para el método de Euler"""
    try:
        data = request.get_json()
        logger.info(f"Recibida solicitud para método de Euler: {data}")
        return euler_controller.controller_euler(data)
    except Exception as e:
        logger.error(f"Error en endpoint de Euler: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500