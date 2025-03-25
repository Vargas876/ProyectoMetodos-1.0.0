from flask import Blueprint, request, jsonify, render_template
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import sympy as sp
import re
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
import numpy as np
import logging

logger = logging.getLogger(__name__)

def jacobi_method(A, b, x0, max_iter=100, tol=1e-6):
    """
    Método de Jacobi para resolver sistemas de ecuaciones lineales.
    
    Args:
        A (numpy.ndarray): Matriz de coeficientes
        b (numpy.ndarray): Vector de términos independientes
        x0 (numpy.ndarray): Vector de estimación inicial
        max_iter (int): Número máximo de iteraciones
        tol (float): Tolerancia para convergencia
    
    Returns:
        tuple: (solución, convergencia, número de iteraciones, historial de iteraciones)
    """
    n = len(b)
    x = np.array(x0, dtype=float)
    iteration_history = []
    
    # Verificar matriz cuadrada
    if A.shape[0] != A.shape[1] or A.shape[0] != len(b):
        raise ValueError("Las dimensiones de A, b deben ser consistentes")
    
    # Verificar matriz no singular
    if np.linalg.det(A) == 0:
        raise ValueError("La matriz A es singular")
    
    converged = False
    for i in range(1, max_iter + 1):
        x_old = x.copy()
        
        # Implementación del método de Jacobi
        for j in range(n):
            # Suma de todos los términos excepto el de la diagonal
            s = sum(A[j][k] * x_old[k] for k in range(n) if k != j)
            x[j] = (b[j] - s) / A[j][j]
        
        # Calcular error
        error = np.linalg.norm(x - x_old, ord=np.inf)
        
        # Almacenar historial de iteraciones
        iteration_history.append({
            'iteration': i,
            'x': x.tolist(),
            'error': float(error)
        })
        
        logger.info(f"Jacobi Iteración {i}: x = {x}, error = {error}")
        
        # Criterio de convergencia
        if error < tol:
            converged = True
            break
    
    logger.info(f"Resultado final: x = {x}, converged = {converged}, iterations = {i}")
    
    return x.tolist(), converged, i, iteration_history