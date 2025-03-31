from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from app.numeric_methods import Simpson as simpson
from app.numeric_methods import Trapecio as trapecio
from app.numeric_methods import GaussSeidel as gauss
from app.numeric_methods import Jacobi as jacobi
from app.numeric_methods import bisection
from app.numeric_methods import Broyden as broyden
from app.numeric_methods import fixed_point
from app.numeric_methods import newton_raphson
from app.numeric_methods import secant
from app.util import equation as eq
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import re
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

def controller_simpson(data):
    """
    Controlador para el método de Simpson de integración numérica.
    Procesa los datos de entrada, calcula la integral y genera una visualización mejorada.
    
    Args:
        data (dict): Diccionario con los parámetros 'equation', 'a', 'b', 'n'
        
    Returns:
        tuple: Respuesta JSON con el resultado y la visualización, o mensaje de error
    """
    # Validar datos de entrada
    if not data or 'equation' not in data or 'a' not in data or 'b' not in data or 'n' not in data:
        return jsonify({'error': 'Faltan campos requeridos: equation, a, b, n'}), 400
    
    try:
        equation = data['equation']
        a = float(data['a'])
        b = float(data['b'])
        n = int(data['n'])
        
        # Validación adicional
        if n % 2 != 0:
            return jsonify({'error': 'El valor de n debe ser par para el método de Simpson'}), 400
            
        if a >= b:
            return jsonify({'error': 'El límite inferior (a) debe ser menor que el límite superior (b)'}), 400
        
        # Parsear la ecuación y calcular la integral
        logger.info(f"Calculando integral de '{equation}' en [{a}, {b}] con n={n}")
        expr, f = eq.parse_equation(equation)
        area, shapes = simpson.simpson_method(f, a, b, n)
        
        # Generar visualización mejorada
        fig = generate_simpson_plot(f, a, b, n, shapes, equation)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Preparar respuesta
        response = {
            'area': round(area, 6),
            'plot_json': graphJSON,
            'equation': equation,
            'interval': [a, b],
            'subintervals': n
        }
        
        logger.info(f"Integral calculada: {area}")
        return jsonify(response)
    
    except ZeroDivisionError:
        logger.error(f"Error de división por cero al evaluar '{equation}'")
        return jsonify({'error': 'La función contiene una división por cero en el intervalo dado'}), 400
    except ValueError as ve:
        logger.error(f"Error de valor: {str(ve)}")
        return jsonify({'error': f'Error en los datos: {str(ve)}'}), 400
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500

def generate_simpson_plot(f, a, b, n, shapes, equation_str):
    """
    Genera una visualización mejorada del método de Simpson.
    
    Args:
        f (function): Función a integrar
        a (float): Límite inferior
        b (float): Límite superior
        n (int): Número de subintervalos
        shapes (list): Lista de formas para graficar
        equation_str (str): Ecuación en formato string para mostrar en el título
        
    Returns:
        plotly.graph_objs.Figure: Figura de Plotly con la visualización
    """
    # Crear un rango de valores x más denso para una curva más suave
    x_vals = np.linspace(a, b, 1000)
    y_vals = [f(x) for x in x_vals]
    
    # Puntos de control del método Simpson (nodos)
    x_nodes = np.linspace(a, b, n+1)
    y_nodes = [f(x) for x in x_nodes]
    
    # Traza de la función
    trace_function = go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name='f(x)',
        line=dict(color='rgb(31, 119, 180)', width=3)
    )
    
    # Puntos de los nodos
    trace_nodes = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers',
        name='Nodos',
        marker=dict(color='rgb(255, 127, 14)', size=8)
    )
    
    # Parábolas de aproximación
    area_shapes = [
        go.Scatter(
            x=shape['x'],
            y=shape['y'],
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.3)',
            mode='lines',
            line=dict(color='rgba(44, 160, 44, 0.8)', width=1),
            name=f'Subintervalo {i+1}' if i == 0 else "",
            showlegend=i == 0,
            hoverinfo='none'
        )
        for i, shape in enumerate(shapes)
    ]
    
    # Mejorar el diseño del gráfico
    layout = go.Layout(
        title=dict(
            text=f"Integración de {equation_str} usando el Método de Simpson",
            font=dict(size=18)
        ),
        xaxis=dict(
            title='x',
            gridcolor='rgb(230, 230, 230)',
            zerolinecolor='rgb(200, 200, 200)'
        ),
        yaxis=dict(
            title='f(x)',
            gridcolor='rgb(230, 230, 230)',
            zerolinecolor='rgb(200, 200, 200)'
        ),
        plot_bgcolor='rgb(250, 250, 250)',
        paper_bgcolor='rgb(250, 250, 250)',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        margin=dict(l=65, r=50, b=65, t=90)
    )
    
    # Agregar anotación para mostrar el resultado de la integral
    annotations = [dict(
        x=0.5,
        y=-0.15,
        showarrow=False,
        text=f"Área calculada = {round(sum([s.get('area', 0) for s in shapes]), 6)}",
        xref="paper",
        yref="paper",
        font=dict(size=14)
    )]
    layout.update(annotations=annotations)
    
    # Crear figura
    fig = go.Figure(data=[trace_function, trace_nodes] + area_shapes, layout=layout)
    
    # Agregar líneas verticales en los nodos
    for i, x_node in enumerate(x_nodes):
        fig.add_shape(
            type="line",
            x0=x_node,
            y0=0,
            x1=x_node,
            y1=f(x_node),
            line=dict(color="rgba(128, 128, 128, 0.5)", dash="dash")
        )
    
    return fig