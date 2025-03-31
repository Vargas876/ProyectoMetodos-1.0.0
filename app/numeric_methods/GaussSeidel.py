import numpy as np
import logging

logger = logging.getLogger(__name__)

def gauss_seidel_method(A, b, x0, max_iter=100, tol=1e-6):
    """
    Método de Gauss-Seidel para resolver sistemas de ecuaciones lineales.
    
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
        
        # Implementación tradicional de Gauss-Seidel
        for j in range(n):
            # Suma de términos antes del índice j (usando valores actualizados)
            s1 = np.dot(A[j, :j], x[:j])
            # Suma de términos después del índice j (usando valores antiguos)
            s2 = np.dot(A[j, j+1:], x_old[j+1:])
            
            # Actualización de x[j]
            x[j] = (b[j] - s1 - s2) / A[j, j]
        
        # Calcular error
        error = np.linalg.norm(x - x_old, ord=np.inf)
        
        # Almacenar historial de iteraciones
        iteration_history.append({
            'iteration': i,
            'x': x.tolist(),
            'error': float(error)
        })
        
        logger.info(f"Gauss-Seidel Iteración {i}: x = {x}, error = {error}")
        
        # Criterio de convergencia
        if error < tol:
            converged = True
            break
    
    logger.info(f"Resultado final: x = {x}, converged = {converged}, iterations = {i}")
    
    return x.tolist(), converged, i, iteration_history