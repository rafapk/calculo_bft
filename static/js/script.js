document.getElementById('sexo').addEventListener('change', function() {
    const quadrilGroup = document.getElementById('quadrilGroup');
    quadrilGroup.style.display = this.value === 'feminino' ? 'block' : 'none';
});

document.getElementById('bfpForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const data = {
        nome: document.getElementById('nome').value,
        peso: parseFloat(document.getElementById('peso').value),
        sexo: document.getElementById('sexo').value,
        idade: parseFloat(document.getElementById('idade').value),
        altura: parseFloat(document.getElementById('altura').value),
        pescoco: parseFloat(document.getElementById('pescoco').value),
        cintura: parseFloat(document.getElementById('cintura').value),
        quadril: document.getElementById('sexo').value === 'feminino' ? parseFloat(document.getElementById('quadril').value) : null
    };

    fetch('/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        } else {
            const tabelaResultados = document.getElementById('tabela-resultados');
            tabelaResultados.innerHTML = `
                <tr><td>Gordura Corporal</td><td>${data.bfp}%</td></tr>
                <tr><td>Categoria</td><td>${data.categoria}</td></tr>
                <tr><td>Massa de Gordura</td><td>${data.massa_gorda} kg</td></tr>
                <tr><td>Massa Corporal Magra</td><td>${data.massa_magra} kg</td></tr>
                <tr><td>Gordura Ideal</td><td>${data.gordura_ideal}%</td></tr>
                <tr><td>Gordura a Perder</td><td>${data.gordura_perder} kg</td></tr>
                <tr><td>Gordura (método IMC)</td><td>${data.bfp_imc}%</td></tr>
            `;

            document.getElementById('result').innerHTML = `
                <div class="alert alert-success">BFP: ${data.bfp.toFixed(2)}%</div>
                <img src="${data.grafico}" class="img-fluid" alt="Gráfico de BFP">
            `;
        }
    });
});

document.getElementById('importarPdfBtn').addEventListener('click', function() {
    document.getElementById('bfpForm').reset();
    const formData = new FormData();
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf';
    
    fileInput.click();

    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file) {
            formData.append('pdf', file);

            fetch('/importar_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.nome) {
                    document.getElementById('nome').value = data.nome;
                }
                if (data.peso) {
                    document.getElementById('peso').value = data.peso;
                }
                if (data.altura) {
                    document.getElementById('altura').value = data.altura;
                }
                if (data['Circunf. do Pescoço'] || data['Circunferência do Pescoço']) {
                    document.getElementById('pescoco').value = data['Circunf. do Pescoço'] || data['Circunferência do Pescoço'];
                }
                if (data['Circunferência da Cintura']) {
                    document.getElementById('cintura').value = data['Circunferência da Cintura'];
                }
                if (data['Circunferência do Quadril']) {
                    document.getElementById('quadril').value = data['Circunferência do Quadril'];
                }
            })
            .catch(error => {
                alert('Erro ao importar o PDF: ' + error);
            });
        }
    });
});
