/**
 * Mock Data Generator for ADDAI ABRA Questionnaires
 * Utility to automatically fill diagnostic forms with realistic hypothetical data.
 */

const MockGenerator = {
    // Randomly select items from an array
    randomChoice: (arr) => arr[Math.floor(Math.random() * arr.length)],
    
    // Random number between min and max
    randomInt: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,

    fillForm: function() {
        const form = document.querySelector('#diagnostico-form');
        if (!form) return;

        // 1. Fill Text Inputs
        form.querySelectorAll('input[type="text"]').forEach(input => {
            if (!input.value) {
                if (input.name.includes('cargo')) input.value = this.randomChoice(['CEO', 'Diretor de TI', 'Gerente de Projetos', 'Sócio-Fundador', 'CTO']);
                else if (input.name.includes('valor')) input.value = this.randomInt(1000, 50000);
                else input.value = "Resposta Automática Exemplo";
            }
        });

        // 2. Fill Number Inputs
        form.querySelectorAll('input[type="number"]').forEach(input => {
            if (!input.value) {
                if (input.name.includes('total_funcionarios')) input.value = this.randomInt(10, 500);
                else input.value = this.randomInt(1, 100);
            }
        });

        // 3. Fill Range/Sliders
        form.querySelectorAll('input[type="range"]').forEach(input => {
            input.value = this.randomInt(parseInt(input.min) || 0, parseInt(input.max) || 10);
            input.dispatchEvent(new Event('input')); // Trigger visual update
        });

        // 4. Fill Selects (with Selectric support)
        form.querySelectorAll('select').forEach(select => {
            const options = Array.from(select.options).filter(o => o.value !== "");
            if (options.length > 0) {
                select.value = this.randomChoice(options).value;
                // Trigger change event for Selectric
                $(select).val(select.value).selectric('refresh');
            }
        });

        // 5. Fill Textareas
        form.querySelectorAll('textarea').forEach(area => {
            if (!area.value) {
                area.value = "Este é um detalhamento hipotético gerado automaticamente para fins de demonstração e testes da plataforma ADDAI ABRA. O objetivo é simular uma resposta real de um gestor.";
            }
        });

        // 6. Fill Radios
        const radioGroups = {};
        form.querySelectorAll('input[type="radio"]').forEach(radio => {
            if (!radioGroups[radio.name]) radioGroups[radio.name] = [];
            radioGroups[radio.name].push(radio);
        });
        
        Object.keys(radioGroups).forEach(name => {
            this.randomChoice(radioGroups[name]).checked = true;
        });

        // 7. Fill Checkboxes
        form.querySelectorAll('input[type="checkbox"]').forEach(check => {
            check.checked = Math.random() > 0.5;
        });

        console.log("Formulário preenchido com dados mock!");
    }
};

$(document).ready(function() {
    $(document).on('click', '.btn-fill-demo', function(e) {
        e.preventDefault();
        MockGenerator.fillForm();
        
        // Simular feedback visual
        const btn = $(this);
        const originalHtml = btn.html();
        btn.removeClass('btn-warning').addClass('btn-success').html('<i class="fas fa-check"></i> Preenchido!');
        setTimeout(() => {
            btn.removeClass('btn-success').addClass('btn-warning').html(originalHtml);
        }, 2000);
    });
});
