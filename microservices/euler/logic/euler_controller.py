from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from microservices.app.util import equation as eq
from . import euler
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import re
import logging

# Definir las transformaciones
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def controller_euler(data):
    """
    Controlador para el método de Euler para resolver EDOs.
    
    Args:
        data (dict): Diccionario con parámetros 'equation', 'x0', 'y0', 'h', 'n', 'method_type'
        
    Returns:
        tuple: Respuesta JSON con el resultado y visualización, o mensaje de error
    """
    # Validar datos de entrada
    required_fields = ['equation', 'x0', 'y0', 'h', 'n']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Faltan campos requeridos: {", ".join(required_fields)}'}), 400

    try:
        equation = data['equation']
        x0 = float(data['x0'])
        y0 = float(data['y0'])
        h = float(data['h'])
        n = int(data['n'])
        method_type = data.get('method_type', 'basic')  # 'basic' o 'improved'
        
        # Validaciones
        if n <= 0:
            return jsonify({'error': 'El número de pasos debe ser mayor que cero'}), 400
            
        if h <= 0:
            return jsonify({'error': 'El tamaño del paso debe ser mayor que cero'}), 400
            
        if h > 1.0:
            return jsonify({'error': 'El tamaño del paso es muy grande, use h ≤ 1.0 para estabilidad'}), 400
        
        # Parsear la ecuación diferencial f(x,y)
        logger.info(f"Resolviendo EDO '{equation}' con condiciones iniciales ({x0}, {y0}), h={h}, n={n}")
        
        # Crear función f(x,y) a partir de la ecuación
        f_func = parse_differential_equation(equation)
        
        # Aplicar método de Euler
        if method_type == 'improved':
            x_values, y_values, iteration_history = euler.improved_euler_method(f_func, x0, y0, h, n)
            method_name = "Euler Mejorado"
        else:
            x_values, y_values, iteration_history = euler.euler_method(f_func, x0, y0, h, n)
            method_name = "Euler Básico"
        
        # Generar visualización
        fig = generate_euler_plot(x_values, y_values, x0, y0, h, equation, method_name, iteration_history)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Preparar respuesta
        response = {
            'converged': True,
            'method': method_name,
            'final_point': {
                'x': round(float(x_values[-1]), 6),
                'y': round(float(y_values[-1]), 6)
            },
            'steps': n,
            'step_size': h,
            'plot_json': graphJSON,
            'iteration_history': iteration_history,
            'equation': equation,
            'initial_conditions': {'x0': x0, 'y0': y0}
        }
        
        logger.info(f"EDO resuelta: punto final ({x_values[-1]:.6f}, {y_values[-1]:.6f})")
        return jsonify(response)
    
    except ZeroDivisionError:
        logger.error(f"Error de división por cero al evaluar '{equation}'")
        return jsonify({'error': 'La función contiene una división por cero'}), 400
    except ValueError as ve:
        logger.error(f"Error de valor: {str(ve)}")
        return jsonify({'error': f'Error en los datos: {str(ve)}'}), 400
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500

def parse_differential_equation(equation_str):
    """
    Parsea una ecuación diferencial de la forma dy/dx = f(x,y)
    
    Args:
        equation_str: String con la ecuación en términos de x e y
        
    Returns:
        function: Función f(x,y) evaluable
    """
    try:
        # Preprocesar la ecuación
        processed_eq = eq.preprocess_equation(equation_str)
        
        # Crear símbolos
        x, y = sp.symbols('x y')
        
        # Funciones permitidas
        allowed_funcs = {
            'E': sp.E,
            'e': sp.E,
            'exp': sp.exp,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'log': sp.log,
            'ln': sp.log,
            'sqrt': sp.sqrt,
            'abs': sp.Abs,
            'pi': sp.pi
        }
        
        # Parsear expresión
        expr = parse_expr(processed_eq, local_dict={'x': x, 'y': y, **allowed_funcs}, 
                         transformations=transformations)
        
        # Crear función lambda
        f_func = sp.lambdify((x, y), expr, modules=['numpy'])
        
        # Probar la función con valores de prueba
        test_result = f_func(1.0, 1.0)
        if not np.isfinite(test_result):
            raise ValueError("La función produce valores no finitos")
            
        return f_func
        
    except Exception as e:
        logger.error(f"Error parseando ecuación diferencial: {str(e)}")
        raise ValueError(f"Error al procesar la ecuación diferencial: {str(e)}")

def generate_euler_plot(x_values, y_values, x0, y0, h, equation_str, method_name, iteration_history):
    """
    Genera visualización del método de Euler
    """
    # Curva de solución aproximada
    solution_trace = go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        name='Solución Aproximada',
        line=dict(color='blue', width=3),
        marker=dict(size=6, color='blue')
    )
    
    # Campo de direcciones (opcional, solo algunos vectores)
    direction_traces = []
    if len(x_values) <= 20:  # Solo para conjuntos pequeños
        for i in range(0, len(x_values)-1, max(1, len(x_values)//10)):
            x_point = x_values[i]
            y_point = y_values[i]
            
            # Calcular pendiente
            try:
                f_func = parse_differential_equation(equation_str.replace('Math.', ''))
                slope = f_func(x_point, y_point)
                
                # Vector direccional
                dx = h * 0.5
                dy = slope * dx
                
                direction_traces.append(go.Scatter(
                    x=[x_point - dx/2, x_point + dx/2],
                    y=[y_point - dy/2, y_point + dy/2],
                    mode='lines',
                    line=dict(color='red', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            except:
                pass
    
    # Punto inicial destacado
    initial_point = go.Scatter(
        x=[x0],
        y=[y0],
        mode='markers',
        name='Condición Inicial',
        marker=dict(size=10, color='red', symbol='star')
    )
    
    # Layout
    layout = go.Layout(
        title=dict(
            text=f"{method_name}: dy/dx = {equation_str}",
            font=dict(size=18)
        ),
        xaxis=dict(
            title='x',
            gridcolor='rgb(230, 230, 230)',
            showgrid=True
        ),
        yaxis=dict(
            title='y',
            gridcolor='rgb(230, 230, 230)',
            showgrid=True
        ),
        plot_bgcolor='rgb(248, 248, 248)',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        annotations=[
            dict(
                x=0.5,
                y=-0.15,
                showarrow=False,
                text=f"Condición inicial: y({x0}) = {y0}, Paso h = {h}",
                xref="paper",
                yref="paper",
                font=dict(size=12)
            )
        ]
    )
    
    # Crear figura
    traces = [solution_trace, initial_point] + direction_traces
    fig = go.Figure(data=traces, layout=layout)
    
    return fig