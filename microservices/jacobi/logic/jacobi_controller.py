from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from . import jacobi
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import logging
from microservices.app.util import equation as eq

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_jacobi_plot(iteration_history, variables):
    """
    Genera una visualización detallada de la convergencia del método de Jacobi.
    
    Args:
        iteration_history (list): Historial de iteraciones
        variables (list): Nombres de las variables
    
    Returns:
        plotly.graph_objs.Figure: Figura de Plotly con la visualización
    """
    # Paleta de colores para las variables
    color_palette = [
        'rgb(31, 119, 180)',   # Azul
        'rgb(255, 127, 14)',   # Naranja
        'rgb(44, 160, 44)',    # Verde
        'rgb(214, 39, 40)',    # Rojo
        'rgb(148, 103, 189)'   # Púrpura
    ]
    
    # Preparar trazas para cada variable
    traces = []
    iterations_range = list(range(len(iteration_history)))
    
    for i in range(len(variables)):
        # Valores de la variable en cada iteración
        var_values = [entry['x'][i] for entry in iteration_history]
        
        # Traza principal con línea y marcadores
        trace = go.Scatter(
            x=iterations_range,
            y=var_values,
            mode='lines+markers',
            name=variables[i],
            line=dict(
                color=color_palette[i % len(color_palette)], 
                width=3
            ),
            marker=dict(
                size=10,
                color=color_palette[i % len(color_palette)],
                symbol='circle',
                line=dict(width=1, color='white')
            ),
            hovertemplate=(
                f'<b>{variables[i]}</b><br>' +
                'Iteración: %{x}<br>' +
                'Valor: %{y:.6f}<extra></extra>'
            )
        )
        traces.append(trace)
    
    layout = go.Layout(
        title=dict(
            text='Convergencia del Método de Jacobi',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Iteración',
            gridcolor='rgb(230, 230, 230)',
            showgrid=True
        ),
        yaxis=dict(
            title='Valor de las Variables',
            gridcolor='rgb(230, 230, 230)',
            showgrid=True
        ),
        plot_bgcolor='rgb(250, 250, 250)',
        paper_bgcolor='rgb(250, 250, 250)',
        legend=dict(
            x=1.1,
            y=1,
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        hovermode='closest',
        margin=dict(l=75, r=100, b=50, t=80)
    )
    
    # Combinar todas las trazas
    fig = go.Figure(data=traces, layout=layout)
    
    # Anotaciones con información adicional
    annotations = []
    
    # Información de convergencia
    last_iter = iteration_history[-1]
    convergence_text = f"Solución Final:<br>"
    for i, var in enumerate(variables):
        convergence_text += f"{var}: {last_iter['x'][i]:.6f}<br>"
    
    annotations.append(dict(
        xref='paper',
        yref='paper',
        x=1.05,
        y=0.2,
        text=convergence_text,
        showarrow=False,
        font=dict(size=12),
        align='left',
        bordercolor='black',
        borderwidth=1,
        borderpad=4,
        bgcolor='rgba(255, 255, 255, 0.7)'
    ))
    
    # Añadir anotaciones al diseño
    layout.update(annotations=annotations)
    
    return fig

def controller_jacobi(data):
    """
    Controlador para el método de Jacobi con mejoras en registro y manejo de errores.
    
    Args:
        data (dict): Datos de entrada para el método de Jacobi
    
    Returns:
        flask.Response: Respuesta JSON con resultados y gráfica
    """
    logger.debug(f"Datos recibidos: {data}")
    
    # Validación de campos requeridos
    required_fields = ['equations', 'variables', 'initial_guess', 'iterations']
    for field in required_fields:
        if field not in data:
            logger.error(f"Falta el campo requerido: {field}")
            return jsonify({'error': f'Falta el campo requerido: {field}'}), 400

    try:
        equations = data['equations']
        variables = data['variables']
        initial_guess = data['initial_guess']
        
        logger.info(f"Resolviendo sistema de {len(equations)} ecuaciones")
        logger.debug(f"Ecuaciones: {equations}")
        logger.debug(f"Variables: {variables}")
        logger.debug(f"Vector inicial x0: {initial_guess}")

        # Parsear ecuaciones y preparar matrices
        A, b = eq.parse_equations(equations, variables)
        x0 = np.array(initial_guess)
        max_iter = int(data['iterations'])
        
        # Ejecutar método de Jacobi
        root, converged, iterations, iteration_history = jacobi.jacobi_method(A, b, x0, max_iter)
        
        # Validaciones de resultados
        if root is None or iteration_history is None:
            logger.error("El método de Jacobi no convergió o devolvió un valor None")
            return jsonify({
                'error': 'El método de Jacobi no logró encontrar una solución',
                'converged': False
            }), 400

        # Generar gráfica de convergencia
        fig = generate_jacobi_plot(iteration_history, variables)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Preparar respuesta
        response = {
            'solution': {var: round(float(root[i]), 6) for i, var in enumerate(variables)},
            'converged': converged,
            'iterations': iterations,
            'iteration_history': iteration_history,
            'plot_json': graphJSON
        }
        
        logger.info(f"Método de Jacobi completado. Convergencia: {converged}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en el método de Jacobi: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500