/**
 * Auto-save de Questionários
 * Salva automaticamente as respostas do usuário no localStorage
 * e restaura quando a página é recarregada
 */

(function () {
  "use strict";

  const QuestionarioAutoSave = {
    // Configurações
    config: {
      storagePrefix: "questionario_",
      autoSaveDelay: 1000, // 1 segundo após última mudança
      showNotifications: true,
    },

    // Timer para debounce
    saveTimer: null,

    /**
     * Inicializa o auto-save para o formulário
     */
    init: function (formId, questionarioNome) {
      const form = document.getElementById(formId);
      if (!form) {
        console.warn("Formulário não encontrado:", formId);
        return;
      }

      this.formId = formId;
      this.questionarioNome = questionarioNome;
      this.storageKey = this.config.storagePrefix + questionarioNome;

      // Restaurar dados salvos
      this.restore();

      // Adicionar listeners para auto-save
      this.attachListeners(form);

      // Limpar ao submeter com sucesso
      form.addEventListener("submit", () => {
        // Aguardar um pouco para garantir que o submit foi bem-sucedido
        setTimeout(() => {
          this.clear();
        }, 500);
      });

      // Mostrar indicador de auto-save
      this.createIndicator();

      console.log("Auto-save inicializado para:", questionarioNome);
    },

    /**
     * Adiciona listeners aos campos do formulário
     */
    attachListeners: function (form) {
      // Campos de texto, textarea, select
      const textInputs = form.querySelectorAll(
        'input[type="text"], input[type="number"], input[type="email"], textarea, select',
      );
      textInputs.forEach((input) => {
        input.addEventListener("input", () => this.scheduleSave());
        input.addEventListener("change", () => this.scheduleSave());
      });

      // Radio buttons
      const radioInputs = form.querySelectorAll('input[type="radio"]');
      radioInputs.forEach((input) => {
        input.addEventListener("change", () => this.scheduleSave());
      });

      // Checkboxes
      const checkboxInputs = form.querySelectorAll('input[type="checkbox"]');
      checkboxInputs.forEach((input) => {
        input.addEventListener("change", () => this.scheduleSave());
      });

      // Range sliders
      const rangeInputs = form.querySelectorAll('input[type="range"]');
      rangeInputs.forEach((input) => {
        input.addEventListener("input", () => this.scheduleSave());
      });
    },

    /**
     * Agenda o salvamento (debounce)
     */
    scheduleSave: function () {
      clearTimeout(this.saveTimer);
      this.saveTimer = setTimeout(() => {
        this.save();
      }, this.config.autoSaveDelay);
    },

    /**
     * Salva os dados do formulário no localStorage
     */
    save: function () {
      const form = document.getElementById(this.formId);
      if (!form) return;

      const formData = {};
      const elements = form.elements;

      for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        const name = element.name;
        const type = element.type;

        if (!name) continue;

        // Ignorar botões de submit
        if (type === "submit" || type === "button") continue;

        // Radio buttons
        if (type === "radio") {
          if (element.checked) {
            formData[name] = element.value;
          }
        }
        // Checkboxes (múltiplos valores)
        else if (type === "checkbox") {
          if (!formData[name]) {
            formData[name] = [];
          }
          if (element.checked) {
            formData[name].push(element.value);
          }
        }
        // Outros campos
        else {
          formData[name] = element.value;
        }
      }

      // Salvar no localStorage
      try {
        localStorage.setItem(
          this.storageKey,
          JSON.stringify({
            data: formData,
            timestamp: new Date().toISOString(),
          }),
        );
        this.showIndicator("Rascunho salvo", "success");
        console.log("Dados salvos:", this.storageKey);
      } catch (e) {
        console.error("Erro ao salvar no localStorage:", e);
        this.showIndicator("Erro ao salvar rascunho", "error");
      }
    },

    /**
     * Restaura os dados salvos do localStorage
     */
    restore: function () {
      try {
        const saved = localStorage.getItem(this.storageKey);
        if (!saved) return;

        const { data, timestamp } = JSON.parse(saved);
        const form = document.getElementById(this.formId);
        if (!form) return;

        // Verificar se os dados não são muito antigos (7 dias)
        const savedDate = new Date(timestamp);
        const now = new Date();
        const daysDiff = (now - savedDate) / (1000 * 60 * 60 * 24);

        if (daysDiff > 7) {
          console.log("Dados muito antigos, ignorando");
          this.clear();
          return;
        }

        // Restaurar valores
        Object.keys(data).forEach((name) => {
          const value = data[name];
          const elements = form.querySelectorAll(`[name="${name}"]`);

          elements.forEach((element) => {
            const type = element.type;

            if (type === "radio") {
              if (element.value === value) {
                element.checked = true;
                // Trigger change event para atualizar UI
                element.dispatchEvent(new Event("change", { bubbles: true }));
              }
            } else if (type === "checkbox") {
              if (Array.isArray(value) && value.includes(element.value)) {
                element.checked = true;
              }
            } else {
              element.value = value;
              // Trigger input event para atualizar labels dinâmicos
              element.dispatchEvent(new Event("input", { bubbles: true }));
            }
          });
        });

        // Mostrar notificação
        const formattedDate = savedDate.toLocaleString("pt-BR");
        this.showIndicator(
          `Rascunho restaurado (${formattedDate})`,
          "info",
          5000,
        );
        console.log("Dados restaurados:", this.storageKey);
      } catch (e) {
        console.error("Erro ao restaurar do localStorage:", e);
      }
    },

    /**
     * Limpa os dados salvos
     */
    clear: function () {
      try {
        localStorage.removeItem(this.storageKey);
        console.log("Dados limpos:", this.storageKey);
      } catch (e) {
        console.error("Erro ao limpar localStorage:", e);
      }
    },

    /**
     * Cria o indicador visual de auto-save
     */
    createIndicator: function () {
      if (document.getElementById("autosave-indicator")) return;

      const indicator = document.createElement("div");
      indicator.id = "autosave-indicator";
      indicator.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                background: #28a745;
                color: white;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-size: 14px;
                font-weight: 500;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            `;
      document.body.appendChild(indicator);
    },

    /**
     * Mostra o indicador com mensagem
     */
    showIndicator: function (message, type = "success", duration = 2000) {
      if (!this.config.showNotifications) return;

      const indicator = document.getElementById("autosave-indicator");
      if (!indicator) return;

      // Cores por tipo
      const colors = {
        success: "#28a745",
        error: "#dc3545",
        info: "#17a2b8",
        warning: "#ffc107",
      };

      indicator.textContent = message;
      indicator.style.background = colors[type] || colors.success;
      indicator.style.opacity = "1";

      setTimeout(() => {
        indicator.style.opacity = "0";
      }, duration);
    },

    /**
     * Adiciona botão para limpar rascunho
     */
    addClearButton: function (containerId) {
      const container = document.getElementById(containerId);
      if (!container) return;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "btn btn-sm btn-outline-secondary";
      button.innerHTML = '<i class="fas fa-trash"></i> Limpar Rascunho';
      button.style.marginLeft = "10px";

      button.addEventListener("click", () => {
        if (confirm("Tem certeza que deseja limpar o rascunho salvo?")) {
          this.clear();
          location.reload();
        }
      });

      container.appendChild(button);
    },
  };

  // Expor globalmente
  window.QuestionarioAutoSave = QuestionarioAutoSave;
})();
