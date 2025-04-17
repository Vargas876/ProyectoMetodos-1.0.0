class CalculatorApp {
    constructor() {
        try {
          
            this.activeMathField = null;
            this.allMathFields = new Map(); 
            this.initializeElements();
            this.initializeMathQuill();
            this.setupEventListeners();
         

            // Hacer la instancia disponible globalmente
            window.calculatorApp = this;
        } catch (error) {
            this.handleInitializationError(error);
        }
    }

    // Inicializa todos los elementos del DOM requeridos
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
                // ¡Importante! Se incluye el contenedor para el método secante:
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
                // Elementos nuevos (teclado virtual, función g(x), integración)
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
                // Los campos para el método secante (x₀ y x₁)
                x0: this.getRequiredElement("x0"),
                x1: this.getRequiredElement("x1"),
            };
            console.log("Elementos inicializados correctamente:", this.elements);
        } catch (error) {
            throw new Error(`Error inicializando elementos: ${error.message}`);
        }
    }
    getActiveMathField() {
        return this.activeMathField;
      }
      

    // Método que obtiene un elemento del DOM y lanza error si no se encuentra
    getRequiredElement(id) {
        const element = document.getElementById(id);
        if (!element) {
            throw new Error(`Elemento requerido no encontrado: ${id}`);
        }
        return element;
    }

    // Inicializa MathQuill para los campos de ecuación y función g(x)
    initializeMathQuill() {
        try {
            if (typeof MathQuill === "undefined") {
                throw new Error("MathQuill no está disponible");
            }
            const MQ = MathQuill.getInterface(2);

            // Inicializar el campo para g(x)
            const gFunctionField = MQ.MathField(this.elements.gFunctionInput, {
                handlers: {
                    edit: () => {
                        try {
                            const latex = gFunctionField.latex();
                            this.elements.gFunctionHidden.value = this.latexToJavaScript(latex);
                        } catch (error) {
                            this.showError("Error al procesar la función g(x)");
                            console.error("Error en MathQuill handler:", error);
                        }
                    },
                    focus: () => {
                        this.activeMathField = gFunctionField;
                        console.log("Campo MathQuill enfocado: gFunctionInput");
                    },
                    blur: () => { }
                },
            });
            this.allMathFields.set("gFunctionInput", gFunctionField);


       
            // Inicializar el campo principal de ecuación
            const mathInputField = MQ.MathField(this.elements.mathInput , {
                handlers: {
                    edit: () => {
                        try {
                            const latex = mathInputField.latex().trim();
                            this.elements.equationHidden.value = this.latexToJavaScript(latex);
                        } catch (error) {
                            this.showError("Error en la ecuación: " + error.message);
                            console.error("Error en MathQuill handler:", error);
                        }
                    },
                    focus: () => {
                        this.activeMathField = gFunctionField;
                        currentActiveMathField = gFunctionField; // ¡Actualiza la variable global!
                        console.log("Campo MathQuill enfocado: gFunctionInput");
                    },
                    
                    blur: () => { }
                },
            });
            this.allMathFields.set("mathInput", mathInputField);

               // Se establece el campo principal como activo
               this.activeMathField = mathInputField, gFunctionField;

            console.log("MathQuill inicializado correctamente con múltiples campos");
        } catch (error) {
            throw new Error(`Error inicializando MathQuill: ${error.message}`);
        }
    }

    // Configuración de los event listeners
    setupEventListeners() {
        try {
            this.elements.form.addEventListener("submit", this.handleFormSubmit.bind(this));
            this.elements.methodSelect.addEventListener("change", this.handleMethodChange.bind(this));
            this.elements.findIntervalBtn.addEventListener("click", this.handleFindInterval.bind(this));

            this.elements.addEquationBtn.addEventListener("click", this.addEquationField.bind(this));

            const numVariablesInput = this.elements.form.querySelector("#numVariables");
            if (numVariablesInput) {
                numVariablesInput.addEventListener("change", this.updateVariables.bind(this));
                numVariablesInput.addEventListener("keydown", (e) => {
                    if (e.key === "Enter") {
                        e.preventDefault();
                        this.updateVariables();
                    }
                });
            }

            const initialGuessSystemInput = this.elements.initialGuessSystem.querySelector("input");
            if (initialGuessSystemInput) {
                initialGuessSystemInput.addEventListener("input", this.validateInitialGuessSystem.bind(this));
            }

            // Inicializar estado según método seleccionado
            this.handleMethodChange({ target: this.elements.methodSelect });

            this.elements.toggleKeyboardBtn.addEventListener("click", this.toggleKeyboard.bind(this));

            // Remover ecuaciones dinámicamente
            this.elements.equationsContainer.addEventListener("click", this.handleEquationRemoval.bind(this));

            console.log("Event listeners configurados correctamente.");
        } catch (error) {
            throw new Error(`Error configurando event listeners: ${error.message}`);
        }
    }

    // Actualiza la visualización de los campos según el método seleccionado
    handleMethodChange(event) {
        const selectedMethod = event.target.value;

        // Reiniciar la propiedad "required" en todos los inputs
        this.elements.form.querySelectorAll("input").forEach((input) => (input.required = false));

        if (selectedMethod === "bisection") {
            this.elements.intervalInputs.style.display = "flex";
            this.elements.findIntervalBtn.style.display = "block";
            this.elements.aBisection.required = true;
            this.elements.bBisection.required = true;
            this.hideFields([
                "secantInputs",
                "initialGuessInput",
                "fixedPointInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
                "integrationInputs",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.enableFields(["a_bisection", "b_bisection"]);
        } else if (selectedMethod === "secant") {
            this.elements.secantInputs.style.display = "flex";
            this.elements.secantInputs.querySelectorAll("input").forEach((input) => (input.required = true));
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "initialGuessInput",
                "fixedPointInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
                "integrationInputs",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.disableFields(["a_bisection", "b_bisection"]);
        } else if (selectedMethod === "newton") {
            this.elements.initialGuessInput.style.display = "block";
            this.elements.initialGuessInput.querySelector("input").required = true;
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "secantInputs",
                "fixedPointInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
                "integrationInputs",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.disableFields(["a_bisection", "b_bisection"]);
        } else if (selectedMethod === "fixed_point") {
            this.elements.initialGuessInput.style.display = "block";
            this.elements.fixedPointInputs.style.display = "block";
            this.elements.initialGuessInput.querySelector("input").required = true;
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "secantInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
                "integrationInputs",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.disableFields(["a_bisection", "b_bisection"]);
        } else if (["jacobi", "gauss_seidel", "broyden"].includes(selectedMethod)) {
            this.elements.systemInputs.style.display = "block";
            this.elements.equationsContainer.style.display = "block";
            this.elements.variablesContainer.style.display = "block";
            this.elements.initialGuessSystem.style.display = "block";
            this.elements.initialGuessSystem.querySelector("input").required = true;
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "secantInputs",
                "initialGuessInput",
                "fixedPointInputs",
                "singleEquationInput",
                "integrationInputs",
            ]);
            this.disableFields(["a_bisection", "b_bisection"]);
            const variableInputs = this.elements.variablesContainer.querySelectorAll('input[name="variables[]"]');
            variableInputs.forEach((input) => (input.required = true));
        } else if (["trapezoidal", "simpson"].includes(selectedMethod)) {
            this.elements.integrationInputs.style.display = "flex";
            this.elements.integrationInputs.querySelectorAll("input").forEach((input) => (input.required = true));
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "secantInputs",
                "initialGuessInput",
                "fixedPointInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.disableFields(["a_bisection", "b_bisection"]);
        } else {
            this.hideFields([
                "intervalInputs",
                "findIntervalBtn",
                "initialGuessInput",
                "fixedPointInputs",
                "secantInputs",
                "systemInputs",
                "equationsContainer",
                "variablesContainer",
                "initialGuessSystem",
                "integrationInputs",
            ]);
            this.elements.singleEquationInput.style.display = "block";
            this.disableFields(["a_bisection", "b_bisection"]);
        }

        // Reinicializa o limpia el campo MathQuill según el método
        this.toggleMathQuill(selectedMethod);

        // Ejemplo en MathQuill (puedes ajustar según prefieras)
        const examples = {
            bisection: "x**2 - 4",
            newton: "x**3 - 2*x - 5",
            secant: "x**2-4*x-1",
            fixed_point: "",
            jacobi: "x + y - 3",
            gauss_seidel: "x + y - 3",
            broyden: "x**2 + y**2 - 4, x**2 - y - 1",
            trapezoidal: "x**2 - 4",
            simpson: "x**2 - 4",
        };
        if (this.activeMathField && examples[selectedMethod] !== undefined) {
            this.activeMathField.latex(examples[selectedMethod]);
        } else if (this.activeMathField) {
            this.activeMathField.latex("");
        }
    }

    hideFields(fields) {
        fields.forEach((field) => {
            if (this.elements[field]) {
                this.elements[field].style.display = "none";
            }
        });
    }

    enableFields(ids) {
        ids.forEach((id) => {
            const field = this.elements.form.querySelector(`#${id}`);
            if (field) {
                field.disabled = false;
            }
        });
    }

    disableFields(ids) {
        ids.forEach((id) => {
            const field = this.elements.form.querySelector(`#${id}`);
            if (field) {
                field.disabled = true;
                field.value = "";
            }
        });
    }

    // Para métodos que requieren MathQuill, se inicializa o limpia según corresponda
    toggleMathQuill(selectedMethod) {
        if (["bisection", "newton", "secant", "fixed_point", "trapezoidal", "simpson"].includes(selectedMethod)) {
          if (!this.mathField && this.elements.mathInput.offsetParent !== null) {
            const MQ = MathQuill.getInterface(2);
            this.mathField = MQ.MathField(this.elements.mathInput, {
              handlers: {
                edit: () => {
                  try {
                    const latex = this.mathField.latex();
                    this.elements.equationHidden.value = this.latexToJavaScript(latex);
                  } catch (error) {
                    this.showError("Error al procesar la ecuación matemática");
                    console.error("Error en MathQuill handler:", error);
                  }
                },
              },
            });
            this.elements.mathInput.addEventListener("focus", () => {
              this.activeMathField = this.mathField;
            });
            this.elements.mathInput.addEventListener("blur", () => {
              setTimeout(() => {
                if (!document.activeElement.classList.contains("mathquill-editable")) {
                  this.activeMathField = null;
                }
              }, 100);
            });
            // Agregar listener para gFunctionInput usando la referencia correcta
            this.elements.gFunctionInput.addEventListener("focus", () => {
           
              if (gf) {
                this.activeMathField = gFunctionInput;
                // También actualizamos la variable global usada por el teclado
                currentActiveMathField = gFunctionInput;
                console.log("Campo MathQuill enfocado: gFunctionInput (desde toggle)");
              }
            });
            // (Opcional) Puedes agregar un blur similar para gFunctionInput si lo requieres.
          }
        } else if (["jacobi", "gauss_seidel", "broyden"].includes(selectedMethod)) {
          if (this.mathField) {
            this.mathField = null;
          }
          this.elements.mathInput.innerHTML = "";
        }
      }
      


    addEquationField() {
        const selectedMethod = this.elements.methodSelect.value;
        if (!["jacobi", "gauss_seidel", "broyden"].includes(selectedMethod)) {
            this.showError("Solo se pueden agregar ecuaciones adicionales en métodos de sistemas de ecuaciones.");
            return;
        }
        const numVariablesInput = this.elements.form.querySelector("#numVariables");
        let numVariables = parseInt(numVariablesInput.value, 10);
        numVariables += 1;
        numVariablesInput.value = numVariables;
        this.updateVariables();

        const equationList = this.elements.equationsContainer.querySelector("#equationsList");
        const currentEquations = equationList.querySelectorAll(".equation-input").length;
        const newEquationIndex = currentEquations + 1;

        const equationDiv = document.createElement("div");
        equationDiv.className = "input-group mb-2 equation-input";
        equationDiv.innerHTML = `
        <span class="input-group-text">Ecuación ${newEquationIndex}:</span>
        <div class="mathquill-field form-control" id="mathquill_equation_${newEquationIndex}"></div>
        <input type="hidden" name="equations[]" id="equation_${newEquationIndex}">
        <button type="button" class="btn btn-danger removeEquationBtn">Eliminar</button>
      `;
        equationList.appendChild(equationDiv);

        const mathQuillDiv = equationDiv.querySelector(".mathquill-field");
        const equationHiddenInput = equationDiv.querySelector(`#equation_${newEquationIndex}`);

        const MQ = MathQuill.getInterface(2);
        const mathField = MQ.MathField(mathQuillDiv, {
            handlers: {
                edit: () => {
                    try {
                        const latex = mathField.latex();
                        equationHiddenInput.value = this.latexToJavaScript(latex);
                    } catch (error) {
                        this.showError("Error al procesar la ecuación matemática");
                        console.error("Error en MathQuill handler:", error);
                    }
                },
                focus: () => {
                    this.activeMathField = mathField;
                    currentActiveMathField = mathField;
                    console.log(`Campo MathQuill enfocado: equation ${newEquationIndex}`);
                },
                
                blur: () => { }
            }
        });
        this.allMathFields.set(`equation_${newEquationIndex}`, mathField);
        mathField.focus();
    }

    updateVariables() {
        const numVariables = parseInt(this.elements.form.querySelector("#numVariables").value, 10);
        const variablesList = this.elements.variablesContainer.querySelector("#variablesList");
        variablesList.innerHTML = "";

        for (let i = 1; i <= numVariables; i++) {
            const varDiv = document.createElement("div");
            varDiv.className = "input-group mb-2";
            varDiv.innerHTML = `
          <span class="input-group-text">Variable ${i}:</span>
          <input type="text" class="form-control" name="variables[]" placeholder="Ingrese la variable ${i}" required pattern="[a-zA-Z]+">
        `;
            variablesList.appendChild(varDiv);
        }

        const equationsList = this.elements.equationsContainer.querySelector("#equationsList");
        equationsList.innerHTML = "";
        for (let i = 1; i <= numVariables; i++) {
            const equationDiv = document.createElement("div");
            equationDiv.className = "input-group mb-2 equation-input";
            equationDiv.innerHTML = `
          <span class="input-group-text">Ecuación ${i}:</span>
          <div class="mathquill-field form-control" id="mathquill_equation_${i}"></div>
          <input type="hidden" name="equations[]" id="equation_${i}">
          <button type="button" class="btn btn-danger removeEquationBtn">Eliminar</button>
        `;
            equationsList.appendChild(equationDiv);

            const mathQuillDiv = equationDiv.querySelector(".mathquill-field");
            const equationHiddenInput = equationDiv.querySelector(`#equation_${i}`);
            const MQ = MathQuill.getInterface(2);
            const mathField = MQ.MathField(mathQuillDiv, {
                handlers: {
                    edit: () => {
                        try {
                            const latex = mathField.latex();
                            equationHiddenInput.value = this.latexToJavaScript(latex);
                        } catch (error) {
                            this.showError("Error al procesar la ecuación matemática");
                            console.error("Error en MathQuill handler:", error);
                        }
                    },
                    focus: () => {
                        this.activeMathField = mathField;
                        console.log(`Campo MathQuill enfocado: equation ${i}`);
                    },
                    blur: () => { }
                }
            });
            this.allMathFields.set(`equation_${i}`, mathField);
        }

        const firstMathField = this.allMathFields.get("equation_1");
        if (firstMathField) {
            firstMathField.focus();
        }
    }

    handleEquationRemoval(event) {
        if (event.target.classList.contains("removeEquationBtn") || event.target.closest(".removeEquationBtn")) {
            const equationInputDiv = event.target.closest(".equation-input");
            if (equationInputDiv) {
                const mathQuillDiv = equationInputDiv.querySelector(".mathquill-field");
                const fieldId = mathQuillDiv.id;
                const equationNumber = fieldId.split("_").pop();
                this.allMathFields.delete(`equation_${equationNumber}`);
                equationInputDiv.remove();
                this.updateEquationLabels();
                this.updateVariables();
            }
        }
    }

    updateEquationLabels() {
        const equations = this.elements.equationsContainer.querySelectorAll(".equation-input");
        equations.forEach((eq, index) => {
            const label = eq.querySelector(".input-group-text");
            label.textContent = `Ecuación ${index + 1}:`;
            const hiddenInput = eq.querySelector('input[type="hidden"]');
            hiddenInput.id = `equation_${index + 1}`;
            const mathQuillDiv = eq.querySelector(".mathquill-field");
            mathQuillDiv.id = `mathquill_equation_${index + 1}`;
        });
    }

    toggleKeyboard() {
        const isVisible = this.elements.keyboardContainer.classList.contains("show");
        this.elements.keyboardContainer.classList.toggle("show");
        this.elements.toggleKeyboardBtn.setAttribute("aria-pressed", !isVisible);
        this.elements.toggleKeyboardBtn.setAttribute("aria-label", isVisible ? "Mostrar Teclado Virtual" : "Ocultar Teclado Virtual");
    }

    validateInitialGuessSystem(event) {
        const input = event.target;
        const pattern = /^-?\d+(\.\d+)?(?:\s*,\s*-?\d+(\.\d+)?)*$/;
        if (!pattern.test(input.value)) {
            input.setCustomValidity("Ingrese valores numéricos separados por comas, por ejemplo: 1,1");
        } else {
            input.setCustomValidity("");
        }
    }

    async handleFindInterval() {
        const equation = this.elements.equationHidden.value.trim();
        if (!equation) {
            this.showError("La ecuación es requerida para encontrar el intervalo.");
            return;
        }
        try {
            const response = await fetch("http://localhost:5001/find_valid_interval", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ equation }),
            });
            const data = await response.json();
            if (data.error) {
                this.showError(data.error);
            } else {
                this.elements.aBisection.value = data.a;
                this.elements.bBisection.value = data.b;
            }
        } catch (error) {
            this.showError("Error al comunicarse con el servidor.");
            console.error("Error en handleFindInterval:", error);
        }
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        this.clearErrors();
        this.showLoading();
        try {
            const formData = await this.validateAndPrepareFormData();
            console.log("Datos de formulario validados:", formData);
            const endpoint = this.getEndpointForMethod(formData.method);
            const response = await this.sendCalculationRequest(endpoint, formData);
            await this.handleCalculationResponse(response, formData.method);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.hideLoading();
        }
    }

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

    hideLoading() {
        const spinner = document.getElementById("loading-spinner");
        if (spinner) {
            spinner.remove();
        }
    }

    clearErrors() {
        document.querySelectorAll(".alert-danger").forEach((error) => error.remove());
        this.elements.resultTable.innerHTML = "";
        this.elements.plotHtmlContainer.innerHTML = "";
        this.elements.resultsDiv.style.display = "none";
    }

    async sendCalculationRequest(endpoint, formData) {
        try {

            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.error || `Error del servidor: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    getEndpointForMethod(method) {
        const endpoints = {
            bisection: "http://localhost:5001/bisection",
            secant: "http://localhost:5003/secant",
            newton: "http://localhost:5002/newton_raphson",
            fixed_point: "http://localhost:5004/fixed_point",
            jacobi: "http://localhost:5005/jacobi",
            gauss_seidel: "http://localhost:5006/gauss_seidel",
            broyden: "http://localhost:5007/broyden",
            trapezoidal: "http://localhost:5009/trapezoidal",
            simpson: "http://localhost:5008/simpson",
        };
        return endpoints[method];
    }

    async handleCalculationResponse(response, method) {
        if (response.error) {
            this.showError(response.error);
            return;
        }
        try {
            if (["trapezoidal", "simpson"].includes(method)) {
                if (response.area !== undefined) {
                    this.displayIntegrationResults(response);
                }
                if (response.plot_json) {
                    this.renderPlot(response.plot_json, method);
                }
            } else if (["jacobi", "gauss_seidel", "broyden"].includes(method)) {
                 // *** Muestra la tabla principal de resultados de sistema
                    if (response.solution) {
                        this.displaySystemResults(response);
                    }
                    // *** Muestra la tabla de iteraciones (si existe iteration_history)
                    if (response.iteration_history && response.iteration_history.length > 0) {
                        // En este caso, pasamos también la solución (variables) para formatear las columnas
                        this.displayIterationHistory(response.iteration_history, response.solution);
                    }
                    // *** Gráfica, si aplica
                    if (response.plot_json) {
                        this.renderPlot(response.plot_json, method);
                    }
            } else {
                if (response.root !== undefined) {
                    this.displayMainResults(response);
                }
                if (response.iteration_history && response.iteration_history.length > 0) {
                    this.displayIterationHistory(response.iteration_history);
                }
                if (response.plot_json) {
                    this.renderPlot(response.plot_json, method);
                }
            }
            this.elements.resultsDiv.style.display = "block";
        } catch (error) {
            this.showError(`Error al mostrar resultados: ${error.message}`);
        }
    }

    displayIntegrationResults(result) {
        this.addResultRow(
            this.elements.resultTable,
            "Área calculada",
            result.area !== undefined ? result.area.toFixed(6) : "No disponible"
        );
    }

    renderPlot(plotJson, method) {
        try {
            const plotData = JSON.parse(plotJson);
            if (!plotData.data || !plotData.layout) {
                throw new Error("plot_json no contiene los campos necesarios 'data' y 'layout'.");
            }
            plotData.layout.title =
                "Método " +
                method.charAt(0).toUpperCase() +
                method.slice(1);
            Plotly.newPlot(this.elements.plotHtmlContainer, plotData.data, plotData.layout)
                .then(() => {
                    if (plotData.frames && plotData.frames.length > 0) {
                        Plotly.addFrames(this.elements.plotHtmlContainer, plotData.frames);
                        Plotly.animate(this.elements.plotHtmlContainer, {
                            transition: { duration: 700, easing: "linear" },
                            frame: { duration: 700, redraw: false },
                        });
                    }
                })
                .catch((error) => {
                    console.error("Error al renderizar la gráfica:", error);
                    this.showError("No se pudo renderizar la gráfica correctamente.");
                });
        } catch (error) {
            console.error("Error al parsear plot_json:", error);
            this.showError("Error al procesar los datos de la gráfica.");
        }
    }

    displayMainResults(result) {
        this.addResultRow(this.elements.resultTable, "Convergió", result.converged ? "Sí" : "No");
        this.addResultRow(this.elements.resultTable, "Iteraciones realizadas", result.iterations);
        this.addResultRow(
            this.elements.resultTable,
            "Raíz encontrada",
            result.root !== undefined ? result.root.toFixed(6) : "No disponible"
        );
    }

    displayIterationHistory(history, solution = null) {
        const iterationTable = this.createIterationTable(history, solution);
        this.elements.resultTable.appendChild(iterationTable);
    }

    createIterationTable(iterations, solution = null) {
        const table = document.createElement("table");
        table.className = "table table-striped table-bordered mt-3";
        let headers = ["Iteración"];
        if (solution && typeof solution === "object" && !Array.isArray(solution)) {
            const vars = Object.keys(solution);
            headers = headers.concat(vars, "Error");
        } else if (Array.isArray(solution)) {
            headers = headers.concat(["Iteración", "Área Parcial", "Error"]);
        } else {
            headers = headers.concat(["x", "f(x)", "Error"]);
        }
        table.appendChild(this.createTableHeader(headers));
        table.appendChild(this.createTableBody(iterations, solution));
        return table;
    }

    createTableHeader(headers) {
        const thead = document.createElement("thead");
        const row = document.createElement("tr");
        headers.forEach((text) => {
            const th = document.createElement("th");
            th.textContent = text;
            th.className = "text-center";
            row.appendChild(th);
        });
        thead.appendChild(row);
        return thead;
    }

    createTableBody(iterations, solution = null) {
        const tbody = document.createElement("tbody");
        iterations.forEach((iter) => {
            const row = document.createElement("tr");
            const cells = [];
            const iterCell = document.createElement("td");
            iterCell.textContent = iter.iteration;
            iterCell.className = "text-center";
            cells.push(iterCell);

            if (solution && typeof solution === "object" && !Array.isArray(solution)) {
                iter.x.forEach((val) => {
                    const valCell = document.createElement("td");
                    valCell.textContent = val.toFixed(6);
                    valCell.className = "text-center";
                    cells.push(valCell);
                });
                const errorCell = document.createElement("td");
                errorCell.textContent = iter.error !== undefined ? iter.error.toFixed(6) : "-";
                errorCell.className = "text-center";
                cells.push(errorCell);
            } else if (Array.isArray(solution)) {
                const areaCell = document.createElement("td");
                areaCell.textContent = iter.area !== undefined ? iter.area.toFixed(6) : "-";
                areaCell.className = "text-center";
                cells.push(areaCell);
                const errorCell = document.createElement("td");
                errorCell.textContent = iter.error !== undefined ? iter.error.toFixed(6) : "-";
                errorCell.className = "text-center";
                cells.push(errorCell);
            } else {
                const xCell = document.createElement("td");
                xCell.textContent = iter.x.toFixed(6);
                xCell.className = "text-center";
                cells.push(xCell);
                const fxCell = document.createElement("td");
                fxCell.textContent = iter.fx !== undefined ? iter.fx.toFixed(6) : "-";
                fxCell.className = "text-center";
                cells.push(fxCell);
                const errorCell = document.createElement("td");
                errorCell.textContent = iter.error !== undefined ? iter.error.toFixed(6) : "-";
                errorCell.className = "text-center";
                cells.push(errorCell);
            }
            cells.forEach((cell) => row.appendChild(cell));
            tbody.appendChild(row);
        });
        return tbody;
    }

   
  // Enhanced error handling for handleError method
    handleError(error) {
        console.error("Error en la aplicación:", error);
        let userMessage = "";
        
        // Organized category-based error detection
        
        // Interval errors
        if (error.message.includes("límite inferior") || 
            error.message.includes("a debe ser menor") || 
            error.message.includes("a >= b")) {
            userMessage = "Error de intervalo: El límite inferior (a) debe ser menor que el superior (b).";
        }
        // Function sign change errors (bisection method)
        else if (error.message.includes("no cambia de signo") || 
                error.message.includes("no sign change") || 
                error.message.includes("intervalo dado")) {
            userMessage = "Error en el método de bisección: La función no cambia de signo en el intervalo dado.\n\n" + 
                        "Posibles causas:\n" + 
                        "• El intervalo contiene un número par de raíces\n" + 
                        "• La función no tiene raíces reales en este intervalo\n\n" + 
                        "Sugerencias: Visualice la función para identificar cruces con el eje X o pruebe con intervalos más pequeños.";
        }
        // Syntax errors in equations
        else if (error.message.includes("sintaxis") || 
                error.message.includes("syntax") || 
                error.message.includes("ecuación") || 
                error.message.includes("inválida")) {
            userMessage = "Error de sintaxis: La ecuación ingresada contiene errores.\n\n" +
                        "Verifique:\n" +
                        "• Paréntesis balanceados\n" +
                        "• Operadores matemáticos correctos\n" +
                        "• Variables definidas adecuadamente";
        }
        // Convergence errors
        else if (error.message.includes("converge") || 
                error.message.includes("diverge")) {
            userMessage = "Error de convergencia: El método no converge con los parámetros proporcionados.\n\n" +
                        "Sugerencias:\n" +
                        "• Aumente el número máximo de iteraciones\n" +
                        "• Pruebe con otros valores iniciales\n" +
                        "• Considere un método numérico diferente";
        }
        // Function definition errors (for g(x) in fixed point)
        else if (error.message.includes("g(x)") || 
                error.message.includes("gFunction")) {
            userMessage = "Error en la definición de g(x): La función de punto fijo no es válida.\n\n" +
                        "Verificar que:\n" +
                        "• Contenga la variable 'x'\n" +
                        "• Tenga una sintaxis correcta\n" +
                        "• Cumpla los requisitos para convergencia de punto fijo";
        }
        // System of equations errors
        else if (error.message.includes("sistema") || 
                error.message.includes("variables") || 
                error.message.includes("ecuaciones")) {
            userMessage = "Error en el sistema de ecuaciones:\n\n" +
                        "Verificar que:\n" +
                        "• El número de ecuaciones sea igual al número de variables\n" +
                        "• Las variables estén correctamente definidas\n" +
                        "• El vector de valores iniciales tenga la dimensión correcta";
        }
        // Division by zero
        else if (error.message.includes("división por cero") || 
                error.message.includes("division by zero") || 
                error.message.includes("divide by zero")) {
            userMessage = "Error matemático: División por cero detectada.\n\n" +
                        "Este error puede ocurrir cuando:\n" +
                        "• La derivada es cero en el método de Newton\n" +
                        "• El denominador se hace cero en el método de la secante\n" +
                        "• Hay una división por cero en la evaluación de la función";
        }
        // MathQuill/LaTeX parsing errors
        else if (error.message.includes("MathQuill") || 
                error.message.includes("LaTeX") || 
                error.message.includes("latex")) {
            userMessage = "Error al procesar la notación matemática:\n\n" +
                        "Verifique que la expresión matemática cumpla con la sintaxis correcta.";
        }
        // Plot errors
        else if (error.message.includes("gráfico") || 
                error.message.includes("plot") || 
                error.message.includes("plotting")) {
            userMessage = "Error al generar el gráfico. Los resultados numéricos están disponibles si el cálculo fue exitoso.";
        }
        // Server communication errors
        else if (error.message.includes("servidor") || 
                error.message.includes("server") || 
                error.message.includes("comunicación")) {
            userMessage = "Error de comunicación con el servidor:\n\n" +
                        "• Verifique su conexión a internet\n" +
                        "• El servidor puede estar temporalmente no disponible\n" +
                        "• Intente nuevamente en unos momentos";
        }
        // Default error message for uncategorized errors
        else {
            userMessage = "Error: " + (error.message || "Ha ocurrido un error inesperado.");
        }
        
        this.showError(userMessage);
    }

    showError(message) {
        this.elements.resultTable.innerHTML = "";
        this.elements.plotHtmlContainer.innerHTML = "";
        this.elements.resultsDiv.style.display = "none";
        
        // Remove any existing error alerts
        document.querySelectorAll(".alert-danger").forEach(error => error.remove());
        
        const errorDiv = document.createElement("div");
        errorDiv.className = "alert alert-danger alert-dismissible fade show mt-3";
        
        // Process message for better display
        const formattedMessage = message.replace(/\n/g, '<br>').replace(/•/g, '&bull; ');
        
        // Add icon for better visibility
        errorDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <i class="fas fa-exclamation-triangle fs-3"></i>
                </div>
                <div>
                    <strong>${formattedMessage.split(':')[0]}</strong>
                    ${formattedMessage.includes(':') ? formattedMessage.split(':').slice(1).join(':') : ''}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                </div>
            </div>
        `;
        
        this.elements.form.insertBefore(errorDiv, this.elements.form.firstChild);
        
        // Scroll to error message
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

    async validateAndPrepareFormData() {
        const method = this.elements.methodSelect.value;
        const iterations = parseInt(this.elements.form.iterations.value, 10);
        if (!method) {
            throw new Error("Debe seleccionar un método numérico");
        }
        if (isNaN(iterations) || iterations < 1 || iterations > 1000) {
            throw new Error("El número de iteraciones debe estar entre 1 y 1000");
        }
        let formData = { method, iterations };
    
        if (["jacobi", "gauss_seidel", "broyden"].includes(method)) {
            const equations = Array.from(this.elements.form.querySelectorAll('input[name="equations[]"]')).map((input) =>
                input.value.trim()
            );
            const variables = Array.from(this.elements.form.querySelectorAll('input[name="variables[]"]')).map((input) =>
                input.value.trim()
            );
            if (!equations.length || !variables.length) {
                throw new Error("Debe ingresar al menos una ecuación y una variable.");
            }
            if (equations.length !== variables.length) {
                throw new Error("El número de ecuaciones debe ser igual al número de variables.");
            }
            for (const variable of variables) {
                if (!variable || !/^[a-zA-Z]+$/.test(variable)) {
                    throw new Error("Cada variable debe contener letras válidas.");
                }
            }
            formData.equations = equations;
            formData.variables = variables;
            const initial_guess_str = this.elements.initialGuessSystem.querySelector("input").value.trim();
            if (!initial_guess_str) {
                throw new Error("El punto inicial es requerido para métodos de sistemas.");
            }
            const initial_guess = initial_guess_str.split(",").map((val) => parseFloat(val.trim()));
            if (initial_guess.length !== variables.length) {
                throw new Error("El punto inicial debe tener el mismo número de elementos que variables.");
            }
            formData.initial_guess = initial_guess;
        } else if (["trapezoidal", "simpson"].includes(method)) {
            const equation = this.elements.equationHidden.value.trim();
            const a = parseFloat(this.elements.integrationInputs.querySelector("#a_integration").value);
            const b = parseFloat(this.elements.integrationInputs.querySelector("#b_integration").value);
            const n = parseInt(this.elements.integrationInputs.querySelector("#n_integration").value, 10);
            if (!equation) {
                throw new Error("La ecuación es requerida para métodos de integración.");
            }
            if (isNaN(a) || isNaN(b)) {
                throw new Error("Los límites del intervalo deben ser números válidos.");
            }
            if (a >= b) {
                throw new Error("El límite inferior (a) debe ser menor que el superior (b).");
            }
            if (isNaN(n) || n < 1) {
                throw new Error("El número de subintervalos (n) debe ser un entero positivo.");
            }
            formData.equation = equation;
            formData.a = a;
            formData.b = b;
            formData.n = n;
        } else {
            const equation = this.elements.equationHidden.value.trim();
            if (!equation) {
                throw new Error("La ecuación es requerida");
            }
            formData.equation = equation;
            if (method === "bisection") {
                const a = parseFloat(this.elements.intervalInputs.querySelector("#a_bisection").value);
                const b = parseFloat(this.elements.intervalInputs.querySelector("#b_bisection").value);
                if (isNaN(a) || isNaN(b)) {
                    throw new Error("Los límites del intervalo deben ser números válidos");
                }
                if (a >= b) {
                    throw new Error("El límite inferior (a) debe ser menor que el superior (b)");
                }
                formData.a = a;
                formData.b = b;
            } else if (method === "secant") {
                const x0 = parseFloat(this.elements.x0.value);
                const x1 = parseFloat(this.elements.x1.value);
                if (isNaN(x0) || isNaN(x1)) {
                    throw new Error("Las estimaciones iniciales x₀ y x₁ deben ser números válidos");
                }
                if (x0 === x1) {
                    throw new Error("Las estimaciones iniciales x₀ y x₁ deben ser distintas");
                }
                formData.x0 = x0;
                formData.x1 = x1;
            } else if (method === "newton" || method === "fixed_point") {
                const initial_guess = parseFloat(this.elements.initialGuessInput.querySelector("input").value);
                if (isNaN(initial_guess)) {
                    throw new Error("El punto inicial debe ser un número válido");
                }
                formData.initial_guess = initial_guess;
                if (method === "fixed_point") {
                    const gFunction = this.elements.gFunctionHidden.value.trim();
                    if (!gFunction) {
                        throw new Error("La función g(x) es requerida para el método de Punto Fijo");
                    }
                    
                    // Aquí solo validamos sintaxis básica, no usamos eval para evitar problemas de seguridad
                    // La validación real se hará en el servidor
                    try {
                        // Verificar paréntesis balanceados
                        let parenCount = 0;
                        for (let char of gFunction) {
                            if (char === '(') parenCount++;
                            if (char === ')') parenCount--;
                            if (parenCount < 0) throw new Error("Paréntesis desbalanceados");
                        }
                        if (parenCount !== 0) throw new Error("Paréntesis desbalanceados");
                        
                        // Asegurar que 'x' esté presente (requisito mínimo para una función de punto fijo)
                        if (!gFunction.includes('x')) {
                            throw new Error("La función g(x) debe contener la variable 'x'");
                        }
                    } catch (error) {
                        throw new Error(`La función g(x) no es válida: ${error.message}`);
                    }
                    
                    formData.gFunction = gFunction;
                }
            }
        }
        if (["jacobi", "gauss_seidel", "broyden"].includes(method)) {
            for (let i = 1; i <= formData.variables.length; i++) {
                this.validateParentheses(formData.equations[i - 1]);
            }
        } else if (
            ["bisection", "secant", "newton", "fixed_point", "trapezoidal", "simpson"].includes(method)
        ) {
            this.validateParentheses(formData.equation);
            if (method === "fixed_point") {
                this.validateParentheses(formData.gFunction);
            }
        }
        return formData;
    }

    validateParentheses(expression) {
        const openParens = (expression.match(/\(/g) || []).length;
        const closeParens = (expression.match(/\)/g) || []).length;
        if (openParens !== closeParens) {
            throw new Error("La ecuación contiene paréntesis desbalanceados.");
        }
    }

    replaceFractions(eq) {
        while (eq.includes("\\frac")) {
            const match = eq.match(/\\frac\{([^{}]+)\}\{([^{}]+)\}/);
            if (!match) break;
            const [fullMatch, numerator, denominator] = match;
            const replacement = `(${numerator})/(${denominator})`;
            eq = eq.replace(fullMatch, replacement);
        }
        return eq;
    }

    latexToJavaScript(latex) {
        let processedLatex = latex;
        processedLatex = this.replaceFractions(processedLatex);
        processedLatex = processedLatex.replace(/\\sqrt\{([^{}]+)\}/g, "sqrt($1)");
        processedLatex = processedLatex.replace(/\\left|\\right/g, "");
        processedLatex = processedLatex.replace(/\\cdot|\\times/g, "*");
        processedLatex = processedLatex.replace(/\\div/g, "/");
        processedLatex = processedLatex.replace(/\\pi/g, "pi");
        processedLatex = processedLatex.replace(/\\exp\{([^{}]+)\}/g, "exp($1)");
        processedLatex = processedLatex.replace(/\\sin/g, "sin");
        processedLatex = processedLatex.replace(/\\cos/g, "cos");
        processedLatex = processedLatex.replace(/\\tan/g, "tan");
        processedLatex = processedLatex.replace(/(\d)\s*([a-zA-Z(])/g, "$1*$2");
        processedLatex = processedLatex.replace(/(\))\s*([a-zA-Z(])/g, "$1*$2");
        processedLatex = processedLatex.replace(/\^(\d+)/g, "**$1");
        processedLatex = processedLatex.replace(/\^(\{[^}]+\})/g, "**$1");
        return processedLatex;
    }

    gFunctionToJavaScript(gFunc) {
        let processedGFunc = gFunc;
        processedGFunc = this.replaceFractions(processedGFunc);
        processedGFunc = processedGFunc.replace(/\\sqrt\{([^{}]+)\}/g, "sqrt($1)");
        processedGFunc = processedGFunc.replace(/\\left|\\right/g, "");
        processedGFunc = processedGFunc.replace(/\\cdot|\\times/g, "*");
        processedGFunc = processedGFunc.replace(/\\div/g, "/");
        processedGFunc = processedGFunc.replace(/\\pi/g, "pi");
        processedGFunc = processedGFunc.replace(/\\ln/g, "log");
        processedGFunc = processedGFunc.replace(/\\log/g, "log10");
        processedGFunc = processedGFunc.replace(/\\exp\{([^{}]+)\}/g, "exp($1)");
        processedGFunc = processedGFunc.replace(/\\sin/g, "sin");
        processedGFunc = processedGFunc.replace(/\\cos/g, "cos");
        processedGFunc = processedGFunc.replace(/\\tan/g, "tan");
        processedGFunc = processedGFunc.replace(/(\d)([a-zA-Z(])/g, "$1*$2");
        processedGFunc = processedGFunc.replace(/([a-zA-Z)])([a-zA-Z(])/g, "$1*$2");
        processedGFunc = processedGFunc.replace(/\)([a-zA-Z(])/g, ")*$1");
        processedGFunc = processedGFunc.replace(/([a-zA-Z)])([a-zA-Z(])/g, "$1*$2");
        const openParens = (processedGFunc.match(/\(/g) || []).length;
        const closeParens = (processedGFunc.match(/\)/g) || []).length;
        if (openParens !== closeParens) {
            throw new Error("gFunction contiene paréntesis desbalanceados.");
        }
        return processedGFunc;
    }

    displaySystemResults(result) {
        const solution = result.solution;
        const keys = Object.keys(solution);
        const values = Object.values(solution);
        this.addResultRow(this.elements.resultTable, "Convergió", result.converged ? "Sí" : "No");
        this.addResultRow(this.elements.resultTable, "Iteraciones realizadas", result.iterations);
        keys.forEach((varName, index) => {
            this.addResultRow(this.elements.resultTable, `Solución para ${varName}`, values[index].toFixed(6));
        });
    }

    addResultRow(table, label, value) {
        const row = document.createElement("tr");
        const labelCell = document.createElement("td");
        const valueCell = document.createElement("td");

        labelCell.innerHTML = label;
        valueCell.innerHTML = value;
        labelCell.className = "fw-bold";

        row.appendChild(labelCell);
        row.appendChild(valueCell);
        table.appendChild(row);
    }

    displayResults(result) {
        this.elements.resultTable.innerHTML = "";
        if (result.solution) {
            const solution = result.solution;
            const table = document.createElement("table");
            table.className = "table table-bordered";

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");
            const varHeader = document.createElement("th");
            varHeader.textContent = "Variable";
            const valHeader = document.createElement("th");
            valHeader.textContent = "Valor";
            headerRow.appendChild(varHeader);
            headerRow.appendChild(valHeader);
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement("tbody");

            for (const [varName, value] of Object.entries(solution)) {
                const row = document.createElement("tr");
                const varCell = document.createElement("td");
                varCell.textContent = varName;
                const valCell = document.createElement("td");
                valCell.textContent = value.toFixed(6);
                row.appendChild(varCell);
                row.appendChild(valCell);
                tbody.appendChild(row);
            }

            table.appendChild(tbody);
            this.elements.resultTable.appendChild(table);
        }
    }
}

// Inicializa la aplicación al cargar el DOM
document.addEventListener("DOMContentLoaded", () => {
    try {
        window.calculatorApp = new CalculatorApp();
        console.log("CalculatorApp inicializado y asignado a window.calculatorApp.");
    } catch (error) {
        console.error("Error fatal al inicializar la aplicación:", error);
        document.body.innerHTML = `
        <div class="container mt-5">
          <div class="alert alert-danger">
            <h4 class="alert-heading">Error Fatal</h4>
            <p>No se pudo iniciar la aplicación. Por favor, recargue la página o contacte al soporte técnico.</p>
            <button class="btn btn-primary mt-3" onclick="location.reload()">Recargar Página</button>
          </div>
        </div>
      `;
    }
});
