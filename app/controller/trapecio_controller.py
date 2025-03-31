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

def controller_trapecio(data):
    """
    Controlador para el método Trapezoidal de integración numérica.
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
        if n <= 0:
            return jsonify({'error': 'El número de subintervalos debe ser mayor que cero'}), 400
            
        if a >= b:
            return jsonify({'error': 'El límite inferior (a) debe ser menor que el límite superior (b)'}), 400
        
        # Parsear la ecuación y calcular la integral
        logger.info(f"Calculando integral de '{equation}' en [{a}, {b}] con n={n} usando método trapezoidal")
        expr, f = eq.parse_equation(equation)
        area, trapezoids = trapecio.trapezoidal_method(f, a, b, n)
        
        # Generar visualización mejorada
        fig = generate_trapezoid_plot(f, a, b, n, trapezoids, equation)
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

def generate_trapezoid_plot(f, a, b, n, trapezoids, equation_str):
    """
    Genera una visualización mejorada del método trapezoidal.
    
    Args:
        f (function): Función a integrar
        a (float): Límite inferior
        b (float): Límite superior
        n (int): Número de subintervalos
        trapezoids (list): Lista de formas para graficar
        equation_str (str): Ecuación en formato string para mostrar en el título
        
    Returns:
        plotly.graph_objs.Figure: Figura de Plotly con la visualización
    """
    # Crear un rango de valores x más denso para una curva más suave
    x_vals = np.linspace(a, b, 1000)
    y_vals = [f(x) for x in x_vals]
    
    # Puntos de control del método trapezoidal (nodos)
    x_nodes = np.linspace(a, b, n+1)
    y_nodes = [f(x) for x in x_nodes]
    
    # Traza de la función
    trace_function = go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name='f(x)',
        line=dict(color='rgb(0, 0, 255)', width=3)
    )
    
    # Puntos de los nodos
    trace_nodes = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers',
        name='Nodos',
        marker=dict(color='rgb(255, 0, 0)', size=8)
    )
    
    # Crear trazas para los trapezoides con diferentes colores
    # Generamos una paleta de colores variada para los diferentes trapezoides
    colors = [
        'rgba(255, 165, 0, 0.3)',  # naranja
        'rgba(50, 205, 50, 0.3)',   # verde
        'rgba(75, 0, 130, 0.3)',    # índigo
        'rgba(0, 191, 255, 0.3)',   # azul cielo
        'rgba(255, 105, 180, 0.3)'  # rosa
    ]
    
    trapezoid_shapes = []
    for i, shape in enumerate(trapezoids):
        color_idx = i % len(colors)
        trapezoid_shapes.append(
            go.Scatter(
                x=shape['x'],
                y=shape['y'],
                fill='tozeroy',
                fillcolor=colors[color_idx],
                mode='lines',
                line=dict(color=colors[color_idx].replace('0.3', '0.8'), width=1),
                name=f'Trapecio {i+1}' if i == 0 else "",
                showlegend=i == 0,
                hoverinfo='none'
            )
        )
    
    # Mejorar el diseño del gráfico
    layout = go.Layout(
        title=dict(
            text=f"Integración de {equation_str} usando el Método Trapezoidal",
            font=dict(size=18)
        ),
        xaxis=dict(
            title='x',
            gridcolor='rgb(230, 230, 230)',
            zerolinecolor='rgb(200, 200, 200)',
            zeroline=True,
            showgrid=True
        ),
        yaxis=dict(
            title='f(x)',
            gridcolor='rgb(230, 230, 230)',
            zerolinecolor='rgb(200, 200, 200)',
            zeroline=True,
            showgrid=True
        ),
        plot_bgcolor='rgb(248, 248, 248)',
        paper_bgcolor='rgb(248, 248, 248)',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        margin=dict(l=65, r=50, b=65, t=90),
        annotations=[
            dict(
                x=0.5,
                y=-0.15,
                showarrow=False,
                text=f"Área calculada = {round(sum([t.get('area', 0) for t in trapezoids]), 6)}",
                xref="paper",
                yref="paper",
                font=dict(size=14)
            )
        ]
    )
    
    # Crear figura con todas las trazas
    fig = go.Figure(data=[trace_function, trace_nodes] + trapezoid_shapes, layout=layout)
    
    # Agregar líneas verticales en los nodos y líneas horizontales para los trapezoides
    for i, x_node in enumerate(x_nodes):
        # Líneas verticales en los nodos
        fig.add_shape(
            type="line",
            x0=x_node,
            y0=0,
            x1=x_node,
            y1=f(x_node),
            line=dict(color="rgba(128, 128, 128, 0.7)", dash="dash", width=1)
        )
        
        # Añadir anotaciones para cada nodo
        if i < len(x_nodes) - 1:
            # Calcular el ancho del subintervalo
            h = (b - a) / n
            # Añadir línea horizontal superior del trapecio
            x_mid = (x_nodes[i] + x_nodes[i+1]) / 2
            y_mid = (f(x_nodes[i]) + f(x_nodes[i+1])) / 2
            
            fig.add_annotation(
                x=x_mid,
                y=y_mid,
                text=f"h={h:.2f}",
                showarrow=False,
                font=dict(size=10),
                bgcolor="rgba(255, 255, 255, 0.7)"
            )
    
    # Añadir un indicador de eje X=0 y Y=0
    if a <= 0 <= b:
        fig.add_shape(
            type="line",
            x0=0,
            y0=min(y_vals),
            x1=0,
            y1=max(y_vals),
            line=dict(color="black", width=1)
        )
    
    if min(y_vals) <= 0 <= max(y_vals):
        fig.add_shape(
            type="line",
            x0=a,
            y0=0,
            x1=b,
            y1=0,
            line=dict(color="black", width=1)
        )
    
    return fig