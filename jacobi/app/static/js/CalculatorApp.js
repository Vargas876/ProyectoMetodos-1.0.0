// CalculatorApp.js
import APIService from './apiService.js';
import FormValidator from './formValidator.js';
import MathQuillManager from './mathQuillManager.js';
import ParserUtil from './parserUtil.js';
import ResultRenderer from './resultRenderer.js';
import UIManager from './uiManager.js';

class CalculatorApp {
  constructor() {
    try {
      // Inicialización de módulos
      this.uiManager = new UIManager();
      this.mathQuillManager = new MathQuillManager();
      this.formValidator = new FormValidator();
      this.apiService = new APIService();
      this.resultRenderer = new ResultRenderer();
      this.parserUtil = new ParserUtil();

      // Configuración e inicialización de la aplicación
      this.initialize();

      // Opcional: hacer la instancia accesible globalmente
      window.calculatorApp = this;
    } catch (error) {
      this.handleInitializationError(error);
    }
  }

  initialize() {
    // Inicializar la interfaz de usuario y los elementos del DOM
    this.uiManager.initializeElements();
    // Configurar los listeners de eventos, pasando el contexto (this) de CalculatorApp
    this.uiManager.setupEventListeners(this);

    // Inicializar los campos MathQuill usando el ParserUtil para conversión de LaTeX
    this.mathQuillManager.initializeMathQuill(
      this.uiManager.getElements(),
      this.parserUtil
    );

    // Aquí se podrían inicializar o configurar otros módulos si fuera necesario
  }

  /**
   * Maneja el evento de envío del formulario.
   * Este método se conecta con el listener configurado en UIManager.
   */
  async handleFormSubmit(event) {
    event.preventDefault();
    try {
      this.uiManager.clearErrors();
      this.uiManager.showLoading();

      // Validar y preparar los datos del formulario
      const formData = this.formValidator.validateAndPrepareFormData(
        this.uiManager.getElements(),
        this.parserUtil
      );

      console.log("Datos de formulario validados:", formData);

      // Obtener el endpoint adecuado según el método seleccionado
      const endpoint = this.apiService.getEndpointForMethod(formData.method);

      // Realizar la solicitud a la API
      const response = await this.apiService.sendCalculationRequest(endpoint, formData);

      // Renderizar los resultados (tablas, gráficas, etc.)
      this.resultRenderer.renderResults(response, formData.method, this.uiManager.getElements());
    } catch (error) {
      this.handleError(error);
    } finally {
      this.uiManager.hideLoading();
    }
  }

  handleError(error) {
    console.error("Error en la aplicación:", error);
    this.uiManager.showError(error.message);
  }

  handleInitializationError(error) {
    console.error("Error de inicialización:", error);
    document.body.innerHTML = `
      <div class="container mt-5">
        <div class="alert alert-danger">
          <h4 class="alert-heading">Error de Inicialización</h4>
          <p>Lo sentimos, no se pudo inicializar la calculadora.</p>
          <hr>
          <p class="mb-0">Error: ${error.message}</p>
          <button class="btn btn-primary mt-3" onclick="location.reload()">Recargar Página</button>
        </div>
      </div>
    `;
  }
}

// Inicializa la aplicación cuando el DOM esté cargado
document.addEventListener("DOMContentLoaded", () => {
  try {
    new CalculatorApp();
    console.log("CalculatorApp inicializado correctamente.");
  } catch (error) {
    console.error("Error fatal al inicializar la aplicación:", error);
  }
});

export default CalculatorApp;
