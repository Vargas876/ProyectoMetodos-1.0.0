from flask import jsonify
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from app.numeric_methods import bisection
from app.util import equation as eq
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Transformaciones de sympy
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

def controller_bisection(data):
    try:
        # 1) Validar que existan los campos requeridos
        required_fields = ['equation', 'a', 'b', 'iterations']
        for field in required_fields:
            if field not in data:
                logger.error(f'Falta el campo requerido: {field}')
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400

        # 2) Extraer y convertir los datos
        equation = data['equation']
        try:
            a = float(data['a'])
            b = float(data['b'])
            max_iter = int(data['iterations'])
        except ValueError:
            logger.error('Los valores de a, b deben ser números y iterations debe ser un entero.')
            return jsonify({'error': 'Los valores de a, b deben ser números y iterations debe ser un entero.'}), 400

        # 3) Parsear la ecuación
        try:
            expr, f = eq.parse_equation(equation)
        except Exception as e:
            logger.error(f"Error al parsear la ecuación: {str(e)}")
            return jsonify({'error': f"Error al parsear la ecuación: {str(e)}"}), 400

        # 4) Ejecutar el método de bisección
        iteration_history = []
        try:
            root, converged, iterations, iteration_history = bisection.bisection_method(
                f, a, b, max_iter, iteration_history
            )
        except ValueError as ve:
            logger.error(str(ve))
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error en el método de bisección: {str(e)}")
            return jsonify({'error': f"Error en el método de bisección: {str(e)}"}), 500

        # 5) Función para determinar dinámicamente el rango de la gráfica (similar a Newton)
        def determine_plot_range(f, center, initial_range=10):
            """
            Retorna un (x_min, x_max) basado en la forma de la función cerca de 'center'.
            initial_range es el ancho inicial por lado (ej: ±10).
            Se ajusta según los valores de la función para mostrar mejor la curva.
            """
            x_min = center - initial_range
            x_max = center + initial_range

            # Tomamos algunos puntos para "explorar" la función
            test_points = np.linspace(x_min, x_max, 200)
            y_values = []
            for x in test_points:
                try:
                    y = f(x)
                    # Filtramos valores extremos
                    if np.isfinite(y) and abs(y) < 1e4:
                        y_values.append(y)
                except:
                    pass

            # Si no se encontró ningún valor, mantenemos el rango inicial
            if not y_values:
                return x_min, x_max

            y_min, y_max = min(y_values), max(y_values)
            y_range = y_max - y_min

            # Si la variación en Y es muy pequeña, ampliamos el rango X para ver más
            if y_range < 5:
                x_min = center - initial_range * 2
                x_max = center + initial_range * 2
            else:
                # Buscar puntos de inflexión aproximados (donde la pendiente cambie de signo)
                inflection_points = []
                for i in range(1, len(test_points) - 1):
                    try:
                        left_slope = (f(test_points[i]) - f(test_points[i-1])) / (test_points[i] - test_points[i-1])
                        right_slope = (f(test_points[i+1]) - f(test_points[i])) / (test_points[i+1] - test_points[i])
                        if left_slope * right_slope < 0:
                            inflection_points.append(test_points[i])
                    except:
                        pass

                # Si encontramos inflexiones, ajustamos x_min y x_max para incluirlas con margen
                if inflection_points:
                    min_infl = min(inflection_points)
                    max_infl = max(inflection_points)
                    x_min = min(x_min, min_infl - 5)
                    x_max = max(x_max, max_infl + 5)

            # Limitar el rango a algo razonable, por ejemplo [-50, 50]
            x_min = max(x_min, -50)
            x_max = min(x_max, 50)

            return x_min, x_max

        # 6) Crear layout de la gráfica
        def create_enhanced_layout(title, x_label='x', y_label='f(x)'):
            return go.Layout(
                title=dict(
                    text=title,
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, family='Arial, sans-serif', color='#2c3e50')
                ),
                xaxis=dict(
                    title=dict(
                        text=x_label,
                        font=dict(size=16, family='Arial, sans-serif')
                    ),
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2,
                    showgrid=True,
                ),
                yaxis=dict(
                    title=dict(
                        text=y_label,
                        font=dict(size=16, family='Arial, sans-serif')
                    ),
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2,
                    showgrid=True,
                ),
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                hovermode='closest',
                showlegend=True,
                legend=dict(
                    x=1.05,
                    y=1,
                    bgcolor='rgba(255, 255, 255, 0.9)',
                    bordercolor='#2c3e50'
                ),
                margin=dict(l=80, r=80, t=100, b=80)
            )

        # 7) Determinar el rango dinámico de la gráfica
        #    Usamos la raíz como "centro" si la tenemos, de lo contrario, tomamos el centro en (a+b)/2
        if root is not None:
            center = root
        else:
            center = (a + b) / 2.0

        # Llamamos a la función para obtener x_min y x_max
        plot_a, plot_b = determine_plot_range(f, center, initial_range=10)

        # 8) Generar puntos para la gráfica
        num_points = 1000
        x_vals = np.linspace(plot_a, plot_b, num_points)
        y_vals = []

        for x in x_vals:
            try:
                val = f(x)
                # Filtrar valores muy grandes
                if np.isfinite(val) and abs(val) < 1e4:
                    y_vals.append(val)
                else:
                    y_vals.append(np.nan)
            except:
                y_vals.append(np.nan)

        # 9) Trazas de la función y eje X
        trace_function = go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name='f(x)',
            line=dict(color='blue', width=2.5),
            connectgaps=False
        )

        # Eje X
        axis_x = go.Scatter(
            x=[plot_a, plot_b],
            y=[0, 0],
            mode='lines',
            name='Eje X',
            line=dict(color='black', width=1),
            hoverinfo='none',
            showlegend=False
        )

        data_traces = [trace_function, axis_x]

        # 10) Si hay raíz, dibujarla
        if root is not None:
            try:
                root_y = f(root)
                if not np.isfinite(root_y):
                    root_y = 0
            except:
                root_y = 0

            root_trace = go.Scatter(
                x=[root],
                y=[root_y],
                mode='markers',
                name='Raíz encontrada',
                marker=dict(color='green', size=10, symbol='star'),
                hovertemplate=f"x = {root:.6f}<br>f(x) = {root_y:.6f}<extra></extra>"
            )
            data_traces.append(root_trace)

        # 11) Crear la figura con layout
        layout = create_enhanced_layout(f"Método de Bisección: {equation}")

        # --- Ajuste manual del eje Y ---
        y_vals_filtered = [v for v in y_vals if not np.isnan(v)]
        if y_vals_filtered:
            y_min, y_max = min(y_vals_filtered), max(y_vals_filtered)
            
            # Limitar manualmente la escala a un máximo (por ejemplo ±50)
            if y_min < -50:
                y_min = -50
            if y_max > 50:
                y_max = 50

            # Si quieres un pequeño margen adicional
            y_range = y_max - y_min
            y_buffer = y_range * 0.1

            layout.update(
                yaxis=dict(
                    range=[y_min - y_buffer, y_max + y_buffer]
                )
            )
        # --------------------------------

        fig = go.Figure(data=data_traces, layout=layout)

        # 12) Serializar la figura a JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # 13) Preparar la respuesta
        response = {
            'root': round(root, 6) if root is not None else None,
            'converged': converged,
            'iterations': iterations,
            'iteration_history': iteration_history,
            'plot_json': graphJSON
        }
        return jsonify(response)

    except Exception as e:
        logger.exception("Error inesperado en el controlador de bisección.")
        return jsonify({'error': 'Ocurrió un error inesperado durante el cálculo.'}), 500
