from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from app.numeric_methods import fixed_point
from app.util import equation as eq
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import logging

# Definir las transformaciones incluyendo 'convert_xor'
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
def controller_fixed(data):
    if not data or 'gFunction' not in data or 'initial_guess' not in data or 'iterations' not in data:
        return jsonify({'error': 'Faltan campos requeridos: gFunction, initial_guess, iterations'}), 400
    
    gFunction = data['gFunction']
    try:
        initial_guess = float(data['initial_guess'])
    except ValueError:
        return jsonify({'error': 'El valor inicial debe ser un número válido'}), 400
    
    try:
        max_iter = int(data['iterations'])
        if max_iter <= 0:
            return jsonify({'error': 'El número de iteraciones debe ser positivo'}), 400
    except ValueError:
        return jsonify({'error': 'El número de iteraciones debe ser un entero válido'}), 400
    
    try:
        logger.info(f"Procesando función g(x): {gFunction}")
        
        # Verificar si la función g(x) está vacía
        if not gFunction.strip():
            return jsonify({'error': 'La función g(x) no puede estar vacía'}), 400
        
        # Intentar parsear la función g(x)
        try:
            g = eq.parse_g_function(gFunction)
        except Exception as e:
            logger.error(f"Error al parsear g(x): {str(e)}")
            return jsonify({'error': f'Error al procesar la función g(x): {str(e)}'}), 400
        
        # Verificar si el punto inicial es válido para g(x)
        try:
            g_x0 = g(initial_guess)
            if not np.isfinite(g_x0):
                # Buscar otro punto inicial cercano que sea válido
                for delta in [0.1, 0.2, 0.5, 1.0]:
                    if np.isfinite(g(initial_guess + delta)):
                        return jsonify({
                            'error': f'La función g(x) no está definida en x={initial_guess}. Intente con x={initial_guess + delta} en su lugar.'
                        }), 400
                return jsonify({
                    'error': f'La función g(x) no está definida en x={initial_guess}. Intente con otro valor inicial.'
                }), 400
        except Exception as e:
            logger.error(f"Error al evaluar g({initial_guess}): {str(e)}")
            return jsonify({
                'error': f'Error al evaluar g(x) en el punto inicial x={initial_guess}: {str(e)}'
            }), 400
        
        # Inicializar iteration_history vacío
        iteration_history = []
        
        # Llamar al método de punto fijo
        logger.info(f"Iniciando método de punto fijo con x0={initial_guess}, max_iter={max_iter}")
        root, converged, iterations, iteration_history = fixed_point.fixed_point_method(
            g, initial_guess, max_iter, iteration_history
        )
        
        # Verificar si se encontró una raíz
        if root is None:
            return jsonify({
                'error': 'El método no convergió. Intente con otro valor inicial o función g(x).',
                'iteration_history': iteration_history
            }), 400
        
        # Preparar datos para el gráfico
        logger.info(f"Método convergió a raíz={root} en {iterations} iteraciones")
        
        # Crear rango de valores x alrededor de la raíz
        x_min = root - 2
        x_max = root + 2
        x_vals = np.linspace(x_min, x_max, 1000)
        
        # Evaluar g(x) para cada punto del rango
        g_vals = []
        for x in x_vals:
            try:
                val = g(x)
                g_vals.append(val)
            except Exception:
                g_vals.append(np.nan)
        
        # Traza para la función g(x)
        trace_function = go.Scatter(
            x=x_vals,
            y=g_vals,
            mode='lines',
            name='g(x)',
            line=dict(color='blue')
        )
        
      
        
        # Traza para el punto fijo (raíz)
        trace_root = go.Scatter(
            x=[root],
            y=[root],
            mode='markers',
            name='Raíz',
            marker=dict(size=10, color='red', symbol='star'),
            hovertemplate=f"x = {root:.6f}<br>y = {root:.6f}<extra></extra>"
        )
        
        # Definir las trazas sin incluir las iteraciones
        data_traces = [trace_function, trace_root]
        
        # Configurar el layout del gráfico
        layout = go.Layout(
            title="Método de Punto Fijo - Función y Raíz",
            xaxis=dict(
                title='x',
                gridcolor='#e0e0e0',
                zerolinecolor='#2c3e50',
                zerolinewidth=2,
                showgrid=True,
            ),
            yaxis=dict(
                title='y',
                gridcolor='#e0e0e0',
                zerolinecolor='#2c3e50',
                zerolinewidth=2,
                showgrid=True,
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            hovermode='closest',
            annotations=[
                dict(
                    x=root,
                    y=root,
                    xref='x',
                    yref='y',
                    text=f'Raíz: {round(root, 6)}',
                    showarrow=True,
                    arrowhead=2,
                    ax=40,
                    ay=-40
                )
            ]
        )
        
        # Ajuste manual del eje Y
        y_vals_valid = [y for y in g_vals if np.isfinite(y)]
        if y_vals_valid:
            y_min_val, y_max_val = min(y_vals_valid), max(y_vals_valid)
            # Limitar la escala a un máximo de ±50
            if y_min_val < -50:
                y_min_val = -50
            if y_max_val > 50:
                y_max_val = 50
            y_range = y_max_val - y_min_val
            y_buffer = y_range * 0.1 if y_range != 0 else 1
            layout.update(
                yaxis=dict(
                    range=[y_min_val - y_buffer, y_max_val + y_buffer],
                    title='y',
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2,
                    showgrid=True,
                )
            )
        
        # Crear la figura y serializarla a JSON
        fig = go.Figure(data=data_traces, layout=layout)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Preparar respuesta
        response = {
            'root': round(float(root), 6),
            'converged': converged,
            'iterations': iterations,
            'iteration_history': iteration_history,
            'plot_json': graphJSON
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en controller_fixed: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
