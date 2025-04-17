from flask import Blueprint, request, jsonify, render_template
from .logic import bisection_controller
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

@main.route('/bisection', methods=['POST'])
def bisection_endpoint():
    data = request.get_json()
    return bisection_controller.controller_bisection(data)
    
@main.route('/find_valid_interval', methods=['POST'])
def find_valid_interval_route():
    try:
        data = request.get_json()
        if not data:
            logger.error("No se recibió ningún dato.")
            return jsonify({'error': 'No se recibió ningún dato.'}), 400

        if 'equation' not in data:
            logger.error('Falta el campo: equation')
            return jsonify({'error': 'Falta el campo: equation'}), 400

        equation = data['equation']
        expr, f = eq.parse_equation(equation)
        # Buscar un intervalo válido en el cual la función cambie de signo
        a, b = eq.find_valid_interval(f)
        return jsonify({'a': a, 'b': b})
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception("Error inesperado al buscar el intervalo.")
        return jsonify({'error': 'Ocurrió un error inesperado al buscar el intervalo.'}), 500
