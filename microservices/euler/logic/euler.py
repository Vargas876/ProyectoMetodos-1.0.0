import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def euler_method(f, x0, y0, h, n):
    """
    Implementa el método de Euler para resolver EDOs de la forma dy/dx = f(x,y)
    
    Args:
        f: Función que define la ecuación diferencial dy/dx = f(x,y)
        x0: Valor inicial de x
        y0: Valor inicial de y
        h: Tamaño del paso
        n: Número de pasos
    
    Returns:
        tuple: (x_values, y_values, iteration_history)
    """
    try:
        x_values = [x0]
        y_values = [y0]
        iteration_history = []
        
        x_current = x0
        y_current = y0
        
        for i in range(n):
            # Calcular la pendiente
            slope = f(x_current, y_current)
            
            # Calcular el siguiente punto
            x_next = x_current + h
            y_next = y_current + h * slope
            
            # Almacenar valores
            x_values.append(x_next)
            y_values.append(y_next)
            
            # Calcular error aproximado (si es posible)
            error = abs(h * slope) if i > 0 else 0
            
            # Guardar historia de iteración
            iteration_history.append({
                'iteration': i + 1,
                'x': round(x_current, 6),
                'y': round(y_current, 6),
                'slope': round(slope, 6),
                'x_next': round(x_next, 6),
                'y_next': round(y_next, 6),
                'error': round(error, 6)
            })
            
            # Actualizar para la siguiente iteración
            x_current = x_next
            y_current = y_next
            
        logger.info(f"Método de Euler completado: {n} pasos desde x={x0} hasta x={x_current}")
        
        return np.array(x_values), np.array(y_values), iteration_history
        
    except Exception as e:
        logger.error(f"Error en método de Euler: {str(e)}")
        raise ValueError(f"Error en el cálculo del método de Euler: {str(e)}")

def calculate_euler_error(h, M, x_final, x0):
    """
    Calcula el error teórico del método de Euler
    
    Args:
        h: Tamaño del paso
        M: Cota superior de |f'| en el intervalo
        x_final: Punto final
        x0: Punto inicial
    
    Returns:
        float: Error estimado
    """
    try:
        L = x_final - x0  # Longitud del intervalo
        error_bound = (M * h * L) / 2
        return error_bound
    except Exception as e:
        logger.error(f"Error calculando cota de error: {str(e)}")
        return 0

def improved_euler_method(f, x0, y0, h, n):
    """
    Implementa el método de Euler mejorado (predictor-corrector)
    
    Args:
        f: Función que define la ecuación diferencial
        x0: Valor inicial de x
        y0: Valor inicial de y
        h: Tamaño del paso
        n: Número de pasos
    
    Returns:
        tuple: (x_values, y_values, iteration_history)
    """
    try:
        x_values = [x0]
        y_values = [y0]
        iteration_history = []
        
        x_current = x0
        y_current = y0
        
        for i in range(n):
            # Predictor (Euler normal)
            slope1 = f(x_current, y_current)
            y_predictor = y_current + h * slope1
            x_next = x_current + h
            
            # Corrector
            slope2 = f(x_next, y_predictor)
            y_next = y_current + (h/2) * (slope1 + slope2)
            
            # Almacenar valores
            x_values.append(x_next)
            y_values.append(y_next)
            
            # Calcular error entre predictor y corrector
            error = abs(y_next - y_predictor)
            
            # Guardar historia
            iteration_history.append({
                'iteration': i + 1,
                'x': round(x_current, 6),
                'y': round(y_current, 6),
                'slope1': round(slope1, 6),
                'y_predictor': round(y_predictor, 6),
                'slope2': round(slope2, 6),
                'y_corrector': round(y_next, 6),
                'error': round(error, 6)
            })
            
            # Actualizar
            x_current = x_next
            y_current = y_next
            
        return np.array(x_values), np.array(y_values), iteration_history
        
    except Exception as e:
        logger.error(f"Error en método de Euler mejorado: {str(e)}")
        raise ValueError(f"Error en el cálculo del método de Euler mejorado: {str(e)}")