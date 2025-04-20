from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from . import secant

import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import re
import logging
from microservices.app.util import equation as eq

# Definir las transformaciones incluyendo 'convert_xor'
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def controller_secant(data):
    if not data or 'equation' not in data or 'x0' not in data or 'x1' not in data or 'iterations' not in data:
        return jsonify({'error': 'Faltan campos requeridos: equation, x0, x1, iterations'}), 400

    equation = data['equation']
    x0 = float(data['x0'])
    x1 = float(data['x1'])
    max_iter = int(data['iterations'])

    try:
        expr, f = eq.parse_equation(equation)
        iteration_history = []  # Inicializa iteration_history
        root, converged, iterations, iteration_history = secant.secant_method(f, x0, x1, max_iter)

        # Generar puntos para la gráfica en un rango que abarque adecuadamente la función
        x_vals = np.linspace(min(x0, x1) - 10, max(x0, x1) + 10, 1000)
        y_vals = []
        for x in x_vals:
            try:
                y_val = f(x)
                y_vals.append(y_val)
            except Exception as e:
                y_vals.append(np.nan)

        # Trazado de la función f(x)
        trace_function = go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name='f(x)',
            line=dict(color='blue')
        )

        # Trazado del punto raíz encontrado (si existe)
        data_traces = [trace_function]
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
                marker=dict(color='red', size=10, symbol='star'),
                hovertemplate=f"x = {root:.6f}<br>f(x) = {root_y:.6f}<extra></extra>"
            )
            data_traces.append(root_trace)

        # Crear trazas para los ejes
        # Eje X: línea horizontal en y=0
        axis_x = go.Scatter(
            x=[x_vals[0], x_vals[-1]],
            y=[0, 0],
            mode='lines',
            name='Eje X',
            line=dict(color='black', width=1),
            hoverinfo='none',
            showlegend=False
        )
        data_traces.append(axis_x)

        # Eje Y: línea vertical en x=0, solo si 0 está dentro del rango de x
        if x_vals[0] <= 0 <= x_vals[-1]:
            # Para el eje Y usamos el rango de y obtenido (filtrando valores válidos)
            y_vals_filtered = [y for y in y_vals if np.isfinite(y)]
            if y_vals_filtered:
                y_axis_min = min(y_vals_filtered)
                y_axis_max = max(y_vals_filtered)
            else:
                y_axis_min, y_axis_max = -10, 10

            axis_y = go.Scatter(
                x=[0, 0],
                y=[y_axis_min, y_axis_max],
                mode='lines',
                name='Eje Y',
                line=dict(color='black', width=1),
                hoverinfo='none',
                showlegend=False
            )
            data_traces.append(axis_y)

        # Layout del gráfico con fondo y papel blancos, ejes con cuadrícula similar a los otros métodos
        layout = go.Layout(
            title="Convergencia del Método de la Secante",
            xaxis=dict(
                title='x',
                gridcolor='#e0e0e0',
                zerolinecolor='#2c3e50',
                zerolinewidth=2,
                showgrid=True,
            ),
            yaxis=dict(
                title='f(x)',
                gridcolor='#e0e0e0',
                zerolinecolor='#2c3e50',
                zerolinewidth=2,
                showgrid=True,
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff'
        )

        # Ajuste manual del eje Y similar a los otros métodos
        y_vals_filtered = [y for y in y_vals if np.isfinite(y)]
        if y_vals_filtered:
            y_min, y_max = min(y_vals_filtered), max(y_vals_filtered)
            # Limitar manualmente la escala a un máximo (por ejemplo, ±50)
            if y_min < -50:
                y_min = -50
            if y_max > 50:
                y_max = 50
            y_range = y_max - y_min
            y_buffer = y_range * 0.1 if y_range != 0 else 1
            layout.update(
                yaxis=dict(
                    range=[y_min - y_buffer, y_max + y_buffer],
                    title='f(x)',
                    gridcolor='#e0e0e0',
                    zerolinecolor='#2c3e50',
                    zerolinewidth=2,
                    showgrid=True,
                )
            )

        # Generar la figura y serializarla a JSON
        fig = go.Figure(data=data_traces, layout=layout)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        root_rounded = round(root, 6) if root is not None else None
        response = {
            'root': root_rounded,
            'converged': converged,
            'iterations': iterations,
            'iteration_history': iteration_history,
            'plot_json': graphJSON
        }
        logger.debug("Returning response")
        return jsonify(response)
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        return jsonify({'error': str(e)}), 500
