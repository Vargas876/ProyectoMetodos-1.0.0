// uiManager.js
class UIManager {
    constructor() {
      this.elements = {};
    }
  
    /**
     * Inicializa todos los elementos del DOM requeridos y los almacena en this.elements.
     */
    initializeElements() {
      try {
        this.elements = {
          form: this.getRequiredElement("calculator-form"),
          mathInput: this.getRequiredElement("math-input"),
          equationHidden: this.getRequiredElement("equation"),
          methodSelect: this.getRequiredElement("method"),
          intervalInputs: this.getRequiredElement("intervalInputs"),
          initialGuessInput: this.getRequiredElement("initialGuessInput"),
          fixedPointInputs: this.getRequiredElement("fixedPointInputs"),
          secantInputs: this.getRequiredElement("secantInputs"),
          systemInputs: this.getRequiredElement("systemInputs"),
          equationsContainer: this.getRequiredElement("equationsContainer"),
          addEquationBtn: this.getRequiredElement("addEquationBtn"),
          variablesContainer: this.getRequiredElement("variablesContainer"),
          resultsDiv: this.getRequiredElement("results"),
          resultTable: this.getRequiredElement("resultTable"),
          plotHtmlContainer: this.getRequiredElement("plotHtmlContainer"),
          findIntervalBtn: this.getRequiredElement("find-interval-btn"),
          initialGuessSystem: this.getRequiredElement("initialGuessSystem"),
          singleEquationInput: this.getRequiredElement("singleEquationInput"),
          toggleKeyboardBtn: this.getRequiredElement("toggle-keyboard-btn"),
          keyboardContainer: this.getRequiredElement("keyboard-container"),
          gFunctionInput: this.getRequiredElement("gFunctionInput"),
          gFunctionHidden: this.getRequiredElement("gFunctionHidden"),
          integrationInputs: this.getRequiredElement("integrationInputs"),
          aIntegration: this.getRequiredElement("a_integration"),
          bIntegration: this.getRequiredElement("b_integration"),
          nIntegration: this.getRequiredElement("n_integration"),
          aBisection: this.getRequiredElement("a_bisection"),
          bBisection: this.getRequiredElement("b_bisection"),
          x0: this.getRequiredElement("x0"),
          x1: this.getRequiredElement("x1"),
        };
        console.log("Elementos inicializados correctamente:", this.elements);
      } catch (error) {
        throw new Error(`Error inicializando elementos: ${error.message}`);
      }
    }
  
    /**
     * Obtiene un elemento del DOM y lanza un error si no se encuentra.
     * @param {string} id - El id del elemento a buscar.
     * @returns {HTMLElement} El elemento del DOM.
     */
    getRequiredElement(id) {
      const element = document.getElementById(id);
      if (!element) {
        throw new Error(`Elemento requerido no encontrado: ${id}`);
      }
      return element;
    }
  
    /**
     * Configura los event listeners para los elementos de la UI.
     * @param {Object} app - La instancia de CalculatorApp que se pasa para acceder a los métodos de la clase principal.
     */
    setupEventListeners(app) {
      try {
        this.elements.form.addEventListener("submit", app.handleFormSubmit.bind(app));
        this.elements.methodSelect.addEventListener("change", app.handleMethodChange.bind(app));
        this.elements.findIntervalBtn.addEventListener("click", app.handleFindInterval.bind(app));
  
        this.elements.addEquationBtn.addEventListener("click", app.addEquationField.bind(app));
        const numVariablesInput = this.elements.form.querySelector("#numVariables");
        if (numVariablesInput) {
          numVariablesInput.addEventListener("change", app.updateVariables.bind(app));
          numVariablesInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              app.updateVariables();
            }
          });
        }
  
        const initialGuessSystemInput = this.elements.initialGuessSystem.querySelector("input");
        if (initialGuessSystemInput) {
          initialGuessSystemInput.addEventListener("input", app.validateInitialGuessSystem.bind(app));
        }
  
        this.elements.toggleKeyboardBtn.addEventListener("click", app.toggleKeyboard.bind(app));
  
        this.elements.equationsContainer.addEventListener("click", app.handleEquationRemoval.bind(app));
  
        console.log("Event listeners configurados correctamente.");
      } catch (error) {
        throw new Error(`Error configurando event listeners: ${error.message}`);
      }
    }
  
    /**
     * Muestra el mensaje de error en la interfaz.
     * @param {string} message - El mensaje de error a mostrar.
     */
    showError(message) {
      this.elements.resultTable.innerHTML = "";
      this.elements.plotHtmlContainer.innerHTML = "";
      this.elements.resultsDiv.style.display = "none";
      const errorDiv = document.createElement("div");
      errorDiv.className = "alert alert-danger alert-dismissible fade show mt-3";
      errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
      this.elements.form.insertBefore(errorDiv, this.elements.form.firstChild);
    }
  
    /**
     * Muestra el cargando en la interfaz.
     */
    showLoading() {
      const loadingSpinner = document.createElement("div");
      loadingSpinner.id = "loading-spinner";
      loadingSpinner.className = "text-center mt-3";
      loadingSpinner.innerHTML = `
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Calculando...</span>
        </div>
        <p class="mt-2">Calculando resultados...</p>
      `;
      this.elements.form.appendChild(loadingSpinner);
    }
  
    /**
     * Oculta el indicador de cargando.
     */
    hideLoading() {
      const spinner = document.getElementById("loading-spinner");
      if (spinner) {
        spinner.remove();
      }
    }
  
    /**
     * Limpia los errores mostrados en la interfaz.
     */
    clearErrors() {
      document.querySelectorAll(".alert-danger").forEach((error) => error.remove());
      this.elements.resultTable.innerHTML = "";
      this.elements.plotHtmlContainer.innerHTML = "";
      this.elements.resultsDiv.style.display = "none";
    }
  
    /**
     * Obtiene los elementos del DOM inicializados.
     * @returns {Object} Los elementos inicializados.
     */
    getElements() {
      return this.elements;
    }
  
    /**
     * Actualiza la visualización de los campos según el método seleccionado.
     */
    handleMethodChange(event) {
      const selectedMethod = event.target.value;
  
      // Reiniciar la propiedad "required" en todos los inputs
      this.elements.form.querySelectorAll("input").forEach((input) => (input.required = false));
  
      // Ejemplo: lógica para mostrar y ocultar campos dependiendo del método seleccionado
      if (selectedMethod === "bisection") {
        this.elements.intervalInputs.style.display = "flex";
        this.elements.findIntervalBtn.style.display = "block";
      } else {
        this.hideFields([
          "intervalInputs",
          "findIntervalBtn",
          "initialGuessInput",
          "fixedPointInputs",
        ]);
      }
    }
  
    /**
     * Oculta los campos de la interfaz.
     * @param {Array} fields - Lista de ids de campos a ocultar.
     */
    hideFields(fields) {
      fields.forEach((field) => {
        if (this.elements[field]) {
          this.elements[field].style.display = "none";
        }
      });
    }
  
    /**
     * Habilita los campos en la interfaz.
     * @param {Array} ids - Lista de ids de campos a habilitar.
     */
    enableFields(ids) {
      ids.forEach((id) => {
        const field = this.elements.form.querySelector(`#${id}`);
        if (field) {
          field.disabled = false;
        }
      });
    }
  
    /**
     * Deshabilita los campos en la interfaz.
     * @param {Array} ids - Lista de ids de campos a deshabilitar.
     */
    disableFields(ids) {
      ids.forEach((id) => {
        const field = this.elements.form.querySelector(`#${id}`);
        if (field) {
          field.disabled = true;
          field.value = "";
        }
      });
    }
  }
  
  export default UIManager;
  