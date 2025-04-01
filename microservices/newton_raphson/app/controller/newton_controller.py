from flask import Blueprint, request, jsonify
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from app.numeric_methods import newton_raphson
from app.util import equation as eq
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import logging

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def controller_newton(data):
    try:
        # Verificar si faltan campos requeridos
        required_fields = ['equation', 'initial_guess', 'iterations']
        for field in required_fields:
            if field not in data:
                logger.error(f'Faltan campos requeridos: {field}')
                return jsonify({'error': f'Faltan campos requeridos: {field}'}), 400

        # Extraer y convertir los datos
        equation = data['equation']
        try:
            initial_guess = float(data['initial_guess'])
            max_iter = int(data['iterations'])
        except ValueError:
            logger.error('initial_guess debe ser un número y iterations debe ser un entero.')
            return jsonify({'error': 'initial_guess debe ser un número y iterations debe ser un entero.'}), 400

        # Parsear la función f(x) y su derivada f'(x)
        try:
            expr, f = eq.parse_equation(equation)
            f_prime = eq.parse_derivative_equation(equation)
        except Exception as e:
            logger.error(f"Error al parsear la ecuación o su derivada: {str(e)}")
            return jsonify({'error': f"Error al parsear la ecuación o su derivada: {str(e)}"}), 400

        # Inicializar el historial de iteraciones
        iteration_history = []

        # Ejecutar el método de Newton-Raphson
        try:
            root, converged, iterations, iteration_history = newton_raphson.newton_raphsonMethod(
                f, f_prime, initial_guess, max_iter, iteration_history
            )
        except ValueError as ve:
            logger.error(str(ve))
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error en el método de Newton-Raphson: {str(e)}")
            return jsonify({'error': f"Error en el método de Newton-Raphson: {str(e)}"}), 500

        # Preparar la gráfica
        try:
            # Función para detectar las características de la función y determinar un rango apropiado
            def determine_plot_range(f, root, initial_range=20):
                # Valores iniciales alrededor de la raíz
                x_min, x_max = root - initial_range, root + initial_range
                
                # Evaluamos en varios puntos para encontrar valores interesantes de la función
                test_points = np.linspace(x_min, x_max, 100)
                y_values = []
                for x in test_points:
                    try:
                        y = f(x)
                        if -1000 < y < 1000:  # Filtrar valores extremos
                            y_values.append(y)
                    except:
                        pass
                
                if not y_values:
                    return x_min, x_max  # Si no hay valores válidos, usar rango inicial
                
                # Ajuste de rangos basado en las características de la función
                y_min, y_max = min(y_values), max(y_values)
                y_range = y_max - y_min
                
                # Ampliar el rango para mostrar la forma de la función
                if y_range < 20:
                    # Para funciones con cambios pequeños, zoom out para ver más contexto
                    x_min, x_max = root - initial_range * 1.5, root + initial_range * 1.5
                else:
                    # Para funciones con cambios grandes, ajustar para ver bien las características
                    # Buscar puntos de inflexión o cambios importantes
                    inflection_points = []
                    for i in range(1, len(test_points) - 1):
                        try:
                            left_slope = (f(test_points[i]) - f(test_points[i-1])) / (test_points[i] - test_points[i-1])
                            right_slope = (f(test_points[i+1]) - f(test_points[i])) / (test_points[i+1] - test_points[i])
                            if (left_slope * right_slope < 0) or abs(right_slope - left_slope) > 10:
                                inflection_points.append(test_points[i])
                        except:
                            pass
                    
                    if inflection_points:
                        # Incluir los puntos de inflexión y un margen
                        x_min = min(inflection_points) - 5
                        x_max = max(inflection_points) + 5
                        
                        # Asegurar que la raíz esté dentro del rango
                        x_min = min(x_min, root - 5)
                        x_max = max(x_max, root + 5)
                
                # Rangos mínimos para asegurar que vemos suficiente de la función
                return max(x_min, -15), min(x_max, 15)

            # Función para crear layout mejorado
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

            # Determinar un rango apropiado para la gráfica
            plot_a, plot_b = determine_plot_range(f, root)
            
            # Generar puntos para la gráfica usando más puntos en regiones con cambios rápidos
            num_points = 2000  # Mayor número de puntos para mejor resolución
            x_vals = np.linspace(plot_a, plot_b, num_points)
            y_vals = []
            
            # Evaluar la función en cada punto con manejo de errores
            for x in x_vals:
                try:
                    y = f(x)
                    # Filtrar valores extremos para evitar distorsión en la gráfica
                    if abs(y) > 1000:
                        y = np.nan
                    y_vals.append(y)
                except:
                    y_vals.append(np.nan)
            
            # Trace de la función f(x)
            trace_function = go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name='f(x)',
                line=dict(color='blue', width=2.5),
                connectgaps=False  # No conectar puntos con valores NaN
            )

            # Trace del punto raíz
            try:
                root_y = f(root)
                root_trace = go.Scatter(
                    x=[root],
                    y=[root_y],
                    mode='markers',
                    name='Raíz encontrada',
                    marker=dict(color='red', size=10, symbol='star'),
                    hovertemplate=f"Raíz: x = {root:.6f}, f(x) = {root_y:.6f}<extra></extra>"
                )
            except:
                root_trace = go.Scatter(
                    x=[root],
                    y=[0],  # Si no podemos evaluar f(root), usamos y=0
                    mode='markers',
                    name='Raíz encontrada',
                    marker=dict(color='red', size=10, symbol='star'),
                    hovertemplate=f"Raíz: x = {root:.6f}<extra></extra>"
                )

            # Ejes X e Y
            axis_x = go.Scatter(
                x=x_vals,
                y=[0] * len(x_vals),
                mode='lines',
                name='Eje X',
                line=dict(color='black', width=1),
                hoverinfo='none',
                showlegend=False
            )
            
            axis_y = go.Scatter(
                x=[0] * len(x_vals),
                y=y_vals,
                mode='lines',
                name='Eje Y',
                line=dict(color='black', width=1),
                hoverinfo='none',
                showlegend=False
            )

            # Crear la figura con la función y la raíz
            data_traces = [trace_function, root_trace, axis_x, axis_y]
            layout = create_enhanced_layout(f'Método de Newton-Raphson: {equation}')
            
            # Ajustar los rangos de los ejes para mostrar bien la función
            y_vals_filtered = [y for y in y_vals if not np.isnan(y)]
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

            
            fig = go.Figure(data=data_traces, layout=layout)
            
            # Asegurar que se muestre una cuadrícula
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

            # Serializar la figura a JSON
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Preparar la respuesta JSON
            response = {
                'root': round(root, 6),
                'converged': converged,
                'iterations': iterations,
                'iteration_history': iteration_history,
                'plot_json': graphJSON
            }

            logger.debug("Returning response")
            return jsonify(response)

        except Exception as e:
            logger.exception(f"Error inesperado al crear la gráfica: {str(e)}")
            return jsonify({'error': 'Ocurrió un error inesperado durante la generación de la gráfica.'}), 500

    except Exception as e:
        logger.exception("Error inesperado en el controlador de Newton-Raphson.")
        return jsonify({'error': 'Ocurrió un error inesperado durante el cálculo.'}), 500