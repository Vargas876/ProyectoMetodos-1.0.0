/**
 * Integrated Virtual Keyboard Implementation
 * Combines functionality for all calculation methods including systems of linear equations
 */

class EnhancedCalculatorApp {
  constructor() {
    try {
         // Initialize the map to store all MathQuill fields
         this.allMathFields = new Map();
         
      // Initialize keyboard layout
      this.initializeKeyboardLayout();
      
      // Initialize core elements
      this.initializeElements();
      
      // Set up the virtual keyboard
      this.loadKeyboard();
      
      // Initialize all MathQuill-eligible fields
      this.initializeAllMathFields();
      
      // Set up event listeners and mutation observers
      this.setupEventListeners();
      this.setupMutationObserver();
      
      // Make the instance globally available
      window.calculatorApp = this;
      
      console.log("Enhanced Calculator App initialized successfully");
    } catch (error) {
      console.error("Initialization error:", error);
    }
  }
  
  /**
   * Initialize keyboard layout and configuration
   */
  initializeKeyboardLayout() {
    // Define keyboard keys with display values
    this.keyboard_keys = [
      [
        { "key": "AC", "print_value": '../static/resources/imgs/ac.png' },
        { "key": "^2", "print_value": '\\Box^2' },
        { "key": "^{", "print_value": '^' },
        { "key": "\\sqrt{}", "print_value": '\\sqrt{\\Box}' },
        { "key": "x", "print_value": 'x' },
        { "key": "7", "print_value": '7' },
        { "key": "8", "print_value": '8' },
        { "key": "9", "print_value": '9' },
        { "key": "+", "print_value": '+' },
        { "key": "-", "print_value": '-' },
      ],
      [
        { "key": "csc()", "print_value": 'csc' },
        { "key": "sin()", "print_value": 'sin' },
        { "key": "**-1", "print_value": '\\Box^{-1}' },
        { "key": "()/()", "print_value": '\\frac{\\Box}{\\Box}' },
        { "key": "y", "print_value": 'y' },
        { "key": "4", "print_value": '4' },
        { "key": "5", "print_value": '5' },
        { "key": "6", "print_value": '6' },
        { "key": "*", "print_value": '\\times' },
        { "key": "/", "print_value": '\\div' }
      ],
      [
        { "key": "sec()", "print_value": 'sec' },
        { "key": "cos()", "print_value": 'cos' },
        { "key": "ln()", "print_value": 'ln' },
        { "key": "log()", "print_value": 'log' },
        { "key": "e", "print_value": 'e' },
        { "key": "1", "print_value": '1' },
        { "key": "2", "print_value": '2' },
        { "key": "3", "print_value": '3' },
        { "key": "del", "print_value": '../static/resources/imgs/back.svg' }
      ],
      [
        { "key": "cot()", "print_value": 'cot' },
        { "key": "tan()", "print_value": 'tan' },
        { "key": "(", "print_value": '(' },
        { "key": ")", "print_value": ')' },
        { "key": "pi", "print_value": '\\pi' },
        { "key": "0", "print_value": '0' },
        { "key": ".", "print_value": '.' },
        { "key": "right", "print_value": '../static/resources/imgs/right.svg' },
        { "key": "left", "print_value": '../static/resources/imgs/left.svg' },
        { "key": "enter", "print_value": '../static/resources/imgs/return.svg' }
      ]
    ];
    
    // Define special keys that need special handling
    this.special_keys = ["del", "left", "right", "enter", "AC"];
    
    // Define selectors for all possible input fields
    this.INPUT_SELECTORS = [
      // Main equation input
      '#math-input',
      // Fixed Point method g(x) input
      '#gFunctionInput',
      // System of equations inputs (dynamic)
      '[id^="mathquill_equation_"]',
      // Other specific method inputs
      '#initial_guess',
      '#initial_guess_system',
      '#a_bisection',
      '#b_bisection',
      '#x0',
      '#x1',
      '#a_integration',
      '#b_integration'
    ];
    
    // Selectors specifically for MathQuill fields
    this.MATHQUILL_ELIGIBLE_SELECTORS = [
      '#math-input',
      '#gFunctionInput',
      '[id^="mathquill_equation_"]'
    ];
    
    console.log("Keyboard layout initialized");
  }
  
  /**
   * Initialize core elements for the calculator
   */
  initializeElements() {
    this.elements = {
      // Main field for equation
      mathInput: document.getElementById("math-input"),
      equationHidden: document.getElementById("equation"),
      // Field for g(x) function
      gFunctionInput: document.getElementById("gFunctionInput"),
      gFunctionHidden: document.getElementById("gFunctionHidden"),
      // Virtual keyboard elements
      toggleKeyboardBtn: document.getElementById("toggle-keyboard-btn"),
      keyboardContainer: document.getElementById("keyboard-container"),
      keyboard: document.getElementById("keyboard"),
      // System equation elements
      addEquationBtn: document.getElementById("addEquationBtn"),
      equationsContainer: document.getElementById("equationsContainer"),
      systemMethodsContainer: document.getElementById("systemMethodsContainer")
    };
    
    // Track current active MathQuill field
    this.activeMathField = null;
    
    // Initialize MathQuill interface
    this.MQ = MathQuill.getInterface(2);
    
    console.log("Core elements initialized");
  }
  
  /**
   * Initialize a single MathQuill field
   */
  initializeMathField(field) {
    // Skip if already initialized
    if (field.mathquillInstance) return;
  
    // Check if this field should be a MathQuill instance
    const shouldBeMathQuill = this.MATHQUILL_ELIGIBLE_SELECTORS.some(selector => field.matches(selector));
  
    if (shouldBeMathQuill) {
      console.log(`Initializing MathQuill for field: ${field.id}`);

      const updateExamplesNoLineal = ( { newValue, field } ) => {
        const methodSelected = document.querySelector("#method").value;
        if( field.id === 'math-input' ) {
          if (["bisection", "newton", "secant", "fixed_point", "trapezoidal", "simpson"].includes(methodSelected)) {
            if ( methodSelected === "fixed_point") {
              examples["fixed_point"][0] = newValue;
            } else {
              examples[methodSelected] = newValue
            }
          } 
        } else if ( field.id === "gFunctionInput") {
          examples["fixed_point"][1] = newValue;
        }
        
      }
  
      // Initialize MathQuill for this field
      const mathQuillInstance = this.MQ.MathField(field, {
        spaceBehavesLikeTab: false,
        handlers: {
          enter: () => {
            const form = document.getElementById('calculator-form');
            if (form) {
              form.requestSubmit();
            }
          },
          edit: () => {
            // Update the corresponding hidden field
            if (field.id === 'math-input' && this.elements.equationHidden) {
              const latex = mathQuillInstance.latex();
              const parsedExpression = this.latexToJavaScript(latex);
              this.elements.equationHidden.value = parsedExpression;
              updateExamplesNoLineal( {newValue:parsedExpression, field} );
              console.log(`Updated equation hidden with: ${parsedExpression}`);
            } 
            // Fix for gFunction - directly update without special logic
            else if (field.id === 'gFunctionInput' && this.elements.gFunctionHidden) {
               // Get the raw LaTeX from the MathQuill field
              const latex = mathQuillInstance.latex();
              
              // Convert LaTeX to JavaScript with special handling
              let parsedExpression = this.latexToJavaScript(latex);
              
              // Make sure the expression is valid JavaScript
              try {
                // Simple validation - check if it can be parsed as a function
                // This is just a syntax check, not a full validation
                new Function('x', `return ${parsedExpression}`);
                
                // Update the hidden field with the parsed expression
                this.elements.gFunctionHidden.value = parsedExpression;
                
                console.log(`Updated gFunctionHidden with: ${parsedExpression}`);
                console.log(`Current gFunctionHidden value: ${this.elements.gFunctionHidden.value}`);
              } catch (error) {
                console.error(`Invalid g(x) expression: ${error.message}`);
                // Don't update the hidden field if the expression is invalid
              }
            }
          }
        }
      });

      // Store reference to mathQuillInstance
      field.mathquillInstance = mathQuillInstance;
      
      // Add to the map of all MathQuill fields
      if (field.id === 'math-input' || field.id === 'gFunctionInput') {
        this.allMathFields.set(field.id, mathQuillInstance);
      } else if (field.id.startsWith('mathquill_equation_')) {
        const equationNumber = field.id.split('_').pop();
        this.allMathFields.set(`equation_${equationNumber}`, mathQuillInstance);
      }
  
      // Add listener to set as active field when clicked
      field.addEventListener('click', (e) => {
        e.preventDefault();
        this.activeMathField = mathQuillInstance;
        console.log(`Active MathQuill field updated to: ${field.id}`);
        mathQuillInstance.focus();
      });
    } else {
      // For regular input fields
      field.addEventListener('click', (e) => {
        this.activeMathField = field;
        console.log(`Active regular field updated to: ${field.id}`);
        field.focus();
      });
    }
  
    // Shared focus listener for both types
    field.addEventListener('focus', (e) => {
      if (field.mathquillInstance) {
        this.activeMathField = field.mathquillInstance;
      } else {
        this.activeMathField = field;
      }
      console.log(`Focus set on field: ${field.id}`);
    });
  }
  
  /**
   * Initialize all available MathQuill fields
   */
  initializeAllMathFields() {
    
    console.log("Initializing keyboard focus management");
    
    // Find all eligible input fields
    const allInputFields = document.querySelectorAll(this.INPUT_SELECTORS.join(', '));
    
    // Initialize each field
    allInputFields.forEach(field => {
      this.initializeMathField(field);
    });
    
    console.log(`${allInputFields.length} fields initialized for virtual keyboard`);
    
    // Specifically check for dynamic equation fields
    this.initializeDynamicEquationFields();
  }
  
  /**
   * Initialize dynamically created equation fields (for systems of equations)
   */
  initializeDynamicEquationFields() {
    console.log("Looking for dynamic equation fields...");
    
    // Find fields that match the dynamic equation pattern
    const dynamicFields = document.querySelectorAll('[id^="mathquill_equation_"]');
    
    dynamicFields.forEach(field => {
      // Only initialize if it doesn't already have a MathQuill instance
      if (!field.mathquillInstance) {
        this.initializeMathField(field);
        console.log(`Dynamic field initialized: ${field.id}`);
      }
    });
    
    console.log(`${dynamicFields.length} dynamic fields found/verified`);
  }
  
  /**
   * Load the virtual keyboard
   */
  loadKeyboard() {
    console.log("Loading virtual keyboard...");
    
    const keyboard = this.elements.keyboard;
    if (!keyboard) {
      console.error("Keyboard container (id='keyboard') not found.");
      return;
    }
    
    keyboard.innerHTML = '';
    
    this.keyboard_keys.forEach(rows => {
      let rowDiv = document.createElement('div');
      rowDiv.classList.add("row-keyboard");
      keyboard.appendChild(rowDiv);
      
      rows.forEach(key => {
        let button = document.createElement('button');
        button.type = 'button';
        button.classList.add("calc-btn");
        button.setAttribute('tabindex', '-1');
        button.setAttribute('aria-label', key["key"]);
        
        if (this.special_keys.includes(key["key"])) {
          if (key["key"] === "del") {
            button.classList.add("del-btn");
          }
          let img = document.createElement('img');
          img.src = key["print_value"];
          img.classList.add("btn-icon");
          button.appendChild(img);
        } else {
          try {
            katex.render(key["print_value"], button, {
              throwOnError: false,
              displayMode: false
            });
          } catch (error) {
            console.error(`Error rendering symbol: ${key["print_value"]}`, error);
          }
        }
        
        button.addEventListener('mousedown', (e) => {
          e.preventDefault();
        });
        
        button.addEventListener('click', (e) => {
          e.preventDefault();
          console.log(`Button pressed: ${key["key"]}`);
          this.handleKeyPress(key["key"]);
        });
        
        button.addEventListener('mouseup', (e) => {
          e.preventDefault();
        });
        
        rowDiv.appendChild(button);
      });
    });
    
    console.log("Virtual keyboard loaded successfully");
  }
  
  /**
   * Handle key press on the virtual keyboard
   */
  handleKeyPress(key) {
    console.log(`Handling key: ${key}`);
    
    // Try to get the active field
    let currentField = this.activeMathField;
    
    // If no active field, look for the focused field
    if (!currentField) {
      const focusedField = document.activeElement;
      // Check if the focused field is one of our target fields
      if (this.INPUT_SELECTORS.some(selector => focusedField.matches && focusedField.matches(selector))) {
        currentField = focusedField.mathquillInstance || focusedField;
      }
    }
    
    // If still no field found, use the first available field
    if (!currentField) {
      const firstMathField = document.querySelector(this.MATHQUILL_ELIGIBLE_SELECTORS.join(', '));
      if (firstMathField) {
        currentField = firstMathField.mathquillInstance || firstMathField;
      } else {
        console.warn("No active field. Please select a field to enter data.");
        return;
      }
    }
    
    // Handle symbol insertion differently for MathQuill and regular fields
    if (currentField.latex && typeof currentField.latex === 'function') {
      // It's a MathQuill field
      this.insertSymbol(currentField, key);
    } else {
      // It's a regular input field
      if (key === 'del') {
        currentField.value = currentField.value.slice(0, -1);
      } else if (key === 'AC') {
        currentField.value = '';
      } else if (!this.special_keys.includes(key)) {
        currentField.value += key;
      }
    }
  }
  
  /**
   * Insert symbol into the active MathQuill field
   */
  insertSymbol(currentMathField, key) {
    console.log("Active mathField:", currentMathField);
    
    // Get current LaTeX
    const currentLatex = currentMathField.latex();
    console.log(`Current LaTeX: ${currentLatex}`);
    
    // List of symbols to avoid repeating
    const avoidRepeats = ['+', '-', 'x', '\\pi'];
    
    // Define a function to avoid repeating signs
    const avoidRepeatingSigns = (newSign) => {
      const lastChar = currentLatex.slice(-1);
      return avoidRepeats.includes(newSign) && lastChar === newSign;
    };
    
    const actions = {
      "AC": () => {
        console.log("Action: AC");
        currentMathField.latex("");
      },
      "del": () => {
        console.log("Action: del");
        currentMathField.keystroke('Backspace');
      },
      "left": () => {
        console.log("Action: left");
        currentMathField.keystroke('Left');
      },
      "right": () => {
        console.log("Action: right");
        currentMathField.keystroke('Right');
      },
      "enter": () => {
        console.log("Action: enter");
        const form = document.getElementById('calculator-form');
        if (form) {
          form.requestSubmit();
        } else {
          console.error("Form (id='calculator-form') not found.");
        }
      },
      "pi": () => {
        console.log("Action: pi");
        if (!avoidRepeatingSigns('\\pi')) {
          currentMathField.write("\\pi");
        }
      },
      "x": () => {
        console.log("Action: x");
        if (!avoidRepeatingSigns('x')) {
          currentMathField.write('x');
        }
      },
      "y": () => {
        console.log("Action: y");
        if (!avoidRepeatingSigns('y')) {
          currentMathField.write('y');
        }
      },
      "+": () => {
        console.log("Action: +");
        if (!avoidRepeatingSigns('+')) {
          currentMathField.write('+');
        }
      },
      "-": () => {
        console.log("Action: -");
        if (!avoidRepeatingSigns('-')) {
          currentMathField.write('-');
        }
      },
      "^2": () => {
        console.log("Action: ^2");
        currentMathField.write("^2");
      },
      "^{": () => {
        console.log("Action: ^{");
        currentMathField.write("^{}");
        currentMathField.keystroke('Left');
      },
      "()/()": () => {
        console.log("Action: fraction");
        currentMathField.write("\\frac{}{}");
        currentMathField.keystroke('Left');
        currentMathField.keystroke('Left');
      },
      "csc()": () => {
        console.log("Action: csc()");
        currentMathField.write("\\csc()");
        currentMathField.keystroke('Left');
      },
      "sec()": () => {
        console.log("Action: sec()");
        currentMathField.write("\\sec()");
        currentMathField.keystroke('Left');
      },
      "cot()": () => {
        console.log("Action: cot()");
        currentMathField.write("\\cot()");
        currentMathField.keystroke('Left');
      },
      "sin()": () => {
        console.log("Action: sin()");
        currentMathField.write("\\sin()");
        currentMathField.keystroke('Left');
      },
      "cos()": () => {
        console.log("Action: cos()");
        currentMathField.write("\\cos()");
        currentMathField.keystroke('Left');
      },
      "tan()": () => {
        console.log("Action: tan()");
        currentMathField.write("\\tan()");
        currentMathField.keystroke('Left');
      },
      "ln()": () => {
        console.log("Action: ln()");
        currentMathField.write("\\ln()");
        currentMathField.keystroke('Left');
      },
      "log()": () => {
        console.log("Action: log()");
        currentMathField.write("\\log()");
        currentMathField.keystroke('Left');
      },
      "\\sqrt{}": () => {
        console.log("Action: square root");
        currentMathField.write("\\sqrt{}");
        currentMathField.keystroke('Left');
      }
    };
    
    // Check if the key has a defined action
    if (actions[key]) {
      actions[key]();
    } else if (key.endsWith("()")) {
      console.log(`Action: insert parentheses for ${key}`);
      currentMathField.write(key.slice(0, -2) + "\\left(\\right)");
      currentMathField.keystroke('Left');
    } else {
      // For other symbols, check for repetition
      console.log(`Action: insert symbol ${key}`);
      if (!avoidRepeatingSigns(key)) {
        currentMathField.write(key);
      }
    }
    
    // Re-focus the MathQuill field after handling the key
    currentMathField.focus();
    console.log("MathQuill field re-focused");
  }
  
  /**
   * Toggle keyboard visibility
   */
  toggleKeyboard() {
    const keyboardContainer = this.elements.keyboardContainer;
    if (!keyboardContainer) {
      console.error("Keyboard container not found");
      return;
    }
    
    const isVisible = keyboardContainer.classList.contains("show");
    keyboardContainer.classList.toggle("show", !isVisible);
    
    const toggleButton = this.elements.toggleKeyboardBtn;
    if (toggleButton) {
      toggleButton.setAttribute("aria-pressed", String(!isVisible));
      toggleButton.setAttribute(
        "aria-label",
        isVisible ? "Show Virtual Keyboard" : "Hide Virtual Keyboard"
      );
    }
    
    console.log(`Virtual keyboard ${isVisible ? "hidden" : "shown"}`);
  }
  
  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Toggle keyboard visibility
    if (this.elements.toggleKeyboardBtn) {
      this.elements.toggleKeyboardBtn.addEventListener("click", this.toggleKeyboard.bind(this));
    }
    
    // Set up add equation button (for systems of linear equations)
    if (this.elements.addEquationBtn) {
      console.log("Setting up add equation button");
      this.elements.addEquationBtn.addEventListener('click', () => {
        // Use a timeout to ensure elements have been added to the DOM
        setTimeout(() => {
          this.initializeDynamicEquationFields();
        }, 200);
      });
    }
  }
  
  /**
   * Set up mutation observer to detect new dynamic fields
   */
  setupMutationObserver() {
    const containers = [
      this.elements.equationsContainer,
      this.elements.systemMethodsContainer,
    ].filter(container => container !== null);
    
    if (containers.length > 0) {
      console.log(`Setting up mutation observer for ${containers.length} containers`);
      
      const observer = new MutationObserver((mutationsList) => {
        let needsInitialization = false;
        
        for (let mutation of mutationsList) {
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Check if any of the added nodes contain equation fields
            for (let node of mutation.addedNodes) {
              if (node.nodeType === Node.ELEMENT_NODE) {
                // Check if the node or its children have IDs that match our selectors
                if (node.querySelector && (
                  node.querySelector('[id^="mathquill_equation_"]') ||
                  (node.id && node.id.startsWith('mathquill_equation_'))
                )) {
                  needsInitialization = true;
                  break;
                }
              }
            }
            
            if (needsInitialization) break;
          }
        }
        
        if (needsInitialization) {
          console.log("Changes detected in dynamic equations");
          setTimeout(() => this.initializeDynamicEquationFields(), 100);
        }
      });
      
      // Observe each container
      containers.forEach(container => {
        observer.observe(container, {
          childList: true,
          subtree: true
        });
        console.log(`Observing container: ${container.id}`);
      });
    }
  }
  
  /**
   * Convert LaTeX to JavaScript expression
   */
//   latexToJavaScript(latex) {
//     return latex
//       .replace(/\\pi/g, "pi")
//       .replace(/\\sqrt\{([^{}]+)\}/g, "sqrt($1)")
//       .replace(/\\left|\\right/g, "")
//       .replace(/\\cdot|\\times/g, "*")
//       .replace(/\\div/g, "/")
//       .replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "($1)/($2)")
//       .replace(/\\sin/g, "sin")
//       .replace(/\\cos/g, "cos")
//       .replace(/\\tan/g, "tan")
//       .replace(/\\cot/g, "cot")
//       .replace(/\\sec/g, "sec")
//       .replace(/\\csc/g, "csc")
//       .replace(/\\ln/g, "ln")
//       .replace(/\\log/g, "log");
//   }
  latexToJavaScript(latex) {
    if (!latex) return '';
    
    // Conversión paso a paso
    let jsExpr = latex
      .replace(/(\d+)([a-zA-Z])/g, '$1*$2')       // 9x → 9*x
      .replace(/([a-zA-Z])(\d+)/g, '$1*$2')       // x9 → x*9
      .replace(/([a-zA-Z])(\()/g, '$1*$2')        // x( → x*(
      .replace(/(\))([a-zA-Z])/g, '$1*$2')        // )x → )*x
      .replace(/(\))(\()/g, '$1*$2')              // )( → )*(
      .replace(/\\frac\{(.*?)\}\{(.*?)\}/g, '($1)/($2)')  // Fracciones
      .replace(/\^/g, '**')                       // Exponentes
      .replace(/\\sqrt\{(.*?)\}/g, 'Math.sqrt($1)') // Raíces cuadradas
      .replace(/\\cdot/g, '*');                   // Multiplicación con punto

    return jsExpr;
  }
}



// Initialize the app when the DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.calculatorApp = new EnhancedCalculatorApp();
  console.log("Enhanced Calculator App initialized");
});