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

# Definir las transformaciones, incluyendo 'convert_xor'
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

def controller_bisection(data):
    try:
        # Validar que existan los campos requeridos
        required_fields = ['equation', 'a', 'b', 'iterations']
        for field in required_fields:
            if field not in data:
                logger.error(f'Falta el campo requerido: {field}')
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400

        # Extraer y convertir los datos
        equation = data['equation']
        try:
            a = float(data['a'])
            b = float(data['b'])
            max_iter = int(data['iterations'])
        except ValueError:
            logger.error('Los valores de a, b deben ser números y iterations debe ser un entero.')
            return jsonify({'error': 'Los valores de a, b deben ser números y iterations debe ser un entero.'}), 400

        # Parsear la ecuación
        try:
            expr, f = eq.parse_equation(equation)
        except Exception as e:
            logger.error(f"Error al parsear la ecuación: {str(e)}")
            return jsonify({'error': f"Error al parsear la ecuación: {str(e)}"}), 400

        # Inicializar el historial de iteraciones
        iteration_history = []

        # Ejecutar el método de bisección
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

        # Preparar la gráfica mejorada con Plotly
        try:
            # Crear un diseño de gráfica mejorado
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
                        zerolinewidth=2
                    ),
                    yaxis=dict(
                        title=dict(
                            text=y_label,
                            font=dict(size=16, family='Arial, sans-serif')
                        ),
                        gridcolor='#e0e0e0',
                        zerolinecolor='#2c3e50',
                        zerolinewidth=2
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

            # Definir un rango amplio para la gráfica que muestre bien la función
            # Centro el rango en la raíz para garantizar que sea visible
            if root is not None:
                # Usar un rango más amplio centrado en la raíz
                range_factor = 2.0  # Factor para ampliar el rango
                interval_size = max(abs(b - a) * range_factor, 5.0)  # Mínimo 5 unidades de rango total
                plot_a = root - interval_size / 2
                plot_b = root + interval_size / 2
                
                # Si el intervalo original [a, b] queda fuera del nuevo rango, lo expandimos
                plot_a = min(plot_a, a)
                plot_b = max(plot_b, b)
            else:
                # Si no hay raíz, usar el intervalo original con un margen grande
                margin = (b - a) * 0.5
                plot_a = a - margin
                plot_b = b + margin

            logger.info(f"Generando gráfica en el rango x: [{plot_a}, {plot_b}]")

            # Evaluar la función en puntos discretos para la gráfica principal
            num_points = 1000  # Más puntos para una gráfica más suave
            x_vals = np.linspace(plot_a, plot_b, num_points)
            y_vals = []
            valid_indices = []

            # Evaluar la función en cada punto del rango
            for i, xi in enumerate(x_vals):
                try:
                    yi = f(xi)
                    # Filtrar valores extremos o no finitos
                    if np.isfinite(yi) and abs(yi) < 1000:
                        y_vals.append(yi)
                        valid_indices.append(i)
                    else:
                        y_vals.append(None)
                except Exception as e:
                    logger.warning(f"No se pudo evaluar f({xi}): {str(e)}")
                    y_vals.append(None)

            logger.info(f"Puntos válidos generados: {len(valid_indices)} de {num_points}")

            # Si hay muy pocos puntos válidos, intentar encontrar un rango donde la función sea evaluable
            if len(valid_indices) < 100:  # Requerimos al menos 100 puntos para una buena gráfica
                # Intentar con un rango más centrado en la raíz
                narrow_margin = max(abs(b - a) * 0.5, 2.0)
                x_vals = np.linspace(root - narrow_margin, root + narrow_margin, num_points)
                y_vals = []
                valid_indices = []
                
                for i, xi in enumerate(x_vals):
                    try:
                        yi = f(xi)
                        if np.isfinite(yi) and abs(yi) < 1000:
                            y_vals.append(yi)
                            valid_indices.append(i)
                        else:
                            y_vals.append(None)
                    except Exception as e:
                        y_vals.append(None)
                        
                logger.info(f"Segundo intento - Puntos válidos generados: {len(valid_indices)} de {num_points}")

            # Crear arreglos con solo los puntos válidos para la gráfica
            valid_x = [x_vals[i] for i in valid_indices]
            valid_y = [y_vals[i] for i in valid_indices]

            # Calcular límites del eje Y basados solo en puntos válidos
            if valid_y:
                y_min = min(valid_y)
                y_max = max(valid_y)
                
                # Detección de valores cercanos a cero para mostrar mejor el cruce con el eje X
                near_zero_values = [y for x, y in zip(valid_x, valid_y) if abs(y) < 0.1]
                if near_zero_values:
                    # Asegurar que el eje Y muestre claramente el cruce por cero
                    if abs(y_min) < 1 and abs(y_max) < 1:
                        # Si los valores son pequeños, usar un rango fijo alrededor de cero
                        y_plot_min = -1
                        y_plot_max = 1
                    else:
                        # Añadir margen proporcional al rango de valores
                        y_range = y_max - y_min
                        y_plot_min = y_min - y_range * 0.2
                        y_plot_max = y_max + y_range * 0.2
                else:
                    # Añadir margen para y
                    y_range = max(y_max - y_min, 0.1)  # Evitar rango cero
                    y_plot_min = y_min - y_range * 0.2
                    y_plot_max = y_max + y_range * 0.2
            else:
                # Valores predeterminados si no hay puntos válidos
                y_plot_min, y_plot_max = -10, 10

            # Trazado de la función principal con mejor visualización
            function_trace = go.Scatter(
                x=valid_x,
                y=valid_y,
                mode='lines',
                name='f(x)',
                line=dict(color='blue', width=2.5),
                connectgaps=False,  # No conectar a través de valores nulos
                hoverinfo='x+y'
            )

            # Trazar el eje x (línea y=0)
            x_axis_trace = go.Scatter(
                x=[plot_a, plot_b],
                y=[0, 0],
                mode='lines',
                name='Eje X',
                line=dict(color='black', width=1.5, dash='dot'),
                hoverinfo='none'
            )

            # Agregar la traza para la raíz encontrada
            if root is not None:
                try:
                    y_root = f(root)
                    if not np.isfinite(y_root):
                        y_root = 0
                except Exception as e:
                    logger.error(f"Error al evaluar f(root): {str(e)}")
                    y_root = 0

                # Trazar el punto de la raíz con una estrella grande
                root_trace = go.Scatter(
                    x=[root],
                    y=[y_root],
                    mode='markers+text',
                    name='Raíz',
                    marker=dict(
                        color='green', 
                        size=14,
                        symbol='star',
                        line=dict(color='black', width=1)
                    ),
                    text=["Raíz"],
                    textposition="top center",
                    hovertemplate="<b>Raíz</b><br>x = %{x:.6f}<br>f(x) = %{y:.6f}<extra></extra>"
                )
                
                # Trazar líneas auxiliares para resaltar la raíz
                v_line_trace = go.Scatter(
                    x=[root, root],
                    y=[y_plot_min, y_root],
                    mode='lines',
                    name='',
                    line=dict(color='green', width=1.5, dash='dash'),
                    showlegend=False,
                    hoverinfo='none'
                )
                
                h_line_trace = go.Scatter(
                    x=[plot_a, root],
                    y=[y_root, y_root],
                    mode='lines',
                    name='',
                    line=dict(color='green', width=1.5, dash='dash'),
                    showlegend=False,
                    hoverinfo='none'
                )
                
                # Añadir estas trazas a los datos
                data_traces = [function_trace, x_axis_trace, root_trace, v_line_trace, h_line_trace]
            else:
                # Si no hay raíz, solo incluir la función y el eje X
                data_traces = [function_trace, x_axis_trace]

            # Configurar un layout mejorado para la gráfica
            layout = create_enhanced_layout('Visualización del Método de Bisección')
            
            # Forzar los límites del eje X e Y para una mejor visualización
            layout.update(
                xaxis=dict(
                    range=[-10, 10],
                    title=dict(
                        text='x',
                        font=dict(size=16, family='Arial, sans-serif')
                    ),
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2
                ),
                yaxis=dict(
                    range=[y_plot_min, y_plot_max],
                    title=dict(
                        text='f(x)',
                        font=dict(size=16, family='Arial, sans-serif')
                    ),
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2
                )
            )
            
            # Añadir anotaciones para mostrar información importante
            if root is not None:
                layout.update(
                    annotations=[
                        dict(
                            x=root,
                            y=y_root,
                            xref="x",
                            yref="y",
                            text=f"Raíz: x = {root:.6f}",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor="#636363",
                            ax=0,
                            ay=-40
                        )
                    ]
                )
            
            # Construir la figura final
            fig = go.Figure(data=data_traces, layout=layout)
            
            # Serializar la figura a JSON para devolver al frontend
            try:
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            except Exception as e:
                logger.error(f"Error al serializar la figura: {str(e)}")
                # Intentar una versión simplificada si hay problemas
                simplified_fig = go.Figure(data=[function_trace, x_axis_trace], layout=layout)
                graphJSON = json.dumps(simplified_fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Preparar la respuesta con los resultados y la gráfica
            response = {
                'root': round(root, 6) if root is not None else None,
                'converged': converged,
                'iterations': iterations,
                'iteration_history': iteration_history,
                'plot_json': graphJSON
            }
            return jsonify(response)

        except Exception as e:
            logger.error(f"Error al generar la gráfica para la ecuación: {str(e)}")
            return jsonify({'error': f"Error al generar la gráfica para la ecuación: {str(e)}"}), 400

    except Exception as e:
        logger.exception("Error inesperado en el controlador de bisección.")
        return jsonify({'error': 'Ocurrió un error inesperado durante el cálculo.'}), 500