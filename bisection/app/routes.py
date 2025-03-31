from flask import Blueprint, request, jsonify, render_template
from app.controller import (
    bisection_controller,
    secant_controller,
    newton_controller,
    fixed_point_controller,
    gauss_controller,
    jacobi_controller,
    Broyden_controller,
    simpson_controller,
    trapecio_controller
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

@main.route('/bisection', methods=['POST'])
def bisection_endpoint():
    data = request.get_json()
    return bisection_controller.controller_bisection(data)

@main.route('/secant', methods=['POST'])
def secant_endpoint():
    data = request.get_json()
    return secant_controller.controller_secant(data)

@main.route('/newton_raphson', methods=['POST'])
def newton_raphson_endpoint():
    data = request.get_json()
    return newton_controller.controller_newton(data)

@main.route('/fixed_point', methods=['POST'])
def fixed_point_endpoint():
    data = request.get_json()
    return fixed_point_controller.controller_fixed(data)

@main.route('/gauss_seidel', methods=['POST'])
def gauss_seidel_endpoint():
    data = request.get_json()
    return gauss_controller.controller_gauss(data)

@main.route('/jacobi', methods=['POST'])
def jacobi_endpoint():
    data = request.get_json()
    return jacobi_controller.controller_jacobi(data)

@main.route('/broyden', methods=['POST'])
def broyden_endpoint():
    data = request.get_json()
    return Broyden_controller.controller_broyden(data)

@main.route('/simpson', methods=['POST'])
def simpson_endpoint():
    data = request.get_json()
    return simpson_controller.controller_simpson(data)

@main.route('/trapezoidal', methods=['POST'])
def trapezoidal_endpoint():
    data = request.get_json()
    return trapecio_controller.controller_trapecio(data)

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
