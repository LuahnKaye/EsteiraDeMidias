// ==========================================================================
// LOGICA DE NEGOCIO E INTERATIVIDADE REATIVA - ESTEIRA DE MIDIAS FRONTEND
// ==========================================================================

// Configurações Globais da API Principal e Simulação
const ENDPOINT_API = "http://localhost:8000/api/v1/midias";
const ID_VENDEDOR_PADRAO = "1fb993c0-1839-4bd6-9243-7d161cc77345"; // Simula lojista padrão

// Captura de Elementos do DOM
const dropzone = document.getElementById("dropzone");
const inputArquivo = document.getElementById("input-arquivo");
const areaAlertas = document.getElementById("area-alertas");
const listaJobs = document.getElementById("lista-jobs");
const linhaVazia = document.getElementById("linha-vazia");

// Dicionário de controle para evitar duplicidade de atualizações e rastrear pooling ativo
const jobsAtivos = {};

/* ==========================================
   1. Gerenciamento de Drag & Drop (UI/UX)
   ========================================== */

// Abre o seletor de arquivos nativo do Windows ao clicar na área do dropzone
dropzone.addEventListener("click", () => inputArquivo.click());

// Adiciona classes visuais de pulsação e destaque ao arrastar o mouse sobre a área
["dragenter", "dragover"].forEach(nomeEvento => {
    dropzone.addEventListener(nomeEvento, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("arrastando");
    }, false);
});

// Remove realces visuais quando o mouse sair da área ou soltar
["dragleave", "drop"].forEach(nomeEvento => {
    dropzone.addEventListener(nomeEvento, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("arrastando");
    }, false);
});

// Trata os arquivos soltos diretamente na área de dropzone
dropzone.addEventListener("drop", (e) => {
    const dadosTransferidos = e.dataTransfer;
    const arquivos = dadosTransferidos.files;
    processarArquivos(arquivos);
});

// Trata os arquivos selecionados manualmente via botão de clique
inputArquivo.addEventListener("change", (e) => {
    const arquivos = e.target.files;
    processarArquivos(arquivos);
    inputArquivo.value = ""; // Limpa para permitir novas seleções
});

/* ==========================================
   2. Pré-Validação de Segurança (Client-Side)
   ========================================== */
function processarArquivos(listaDeArquivos) {
    limparAlertas();

    if (listaDeArquivos.length === 0) return;

    // Bloqueia se a quantidade de imagens enviadas simultaneamente exceder 5
    if (listaDeArquivos.length > 5) {
        exibirAlerta("Limite excedido: Você pode enviar no máximo 5 arquivos por vez.");
        return;
    }

    // Processa individualmente cada arquivo
    Array.from(listaDeArquivos).forEach(arquivo => {
        // Validação de formato (Magic Bytes será feito no backend, mas barramos no front de forma inicial)
        const extensoesPermitidas = ["image/png", "image/jpeg", "image/jpg"];
        const nomeLower = arquivo.name.toLowerCase();
        const extensaoValida = extensoesPermitidas.includes(arquivo.type) || 
                              nomeLower.endsWith(".png") || 
                              nomeLower.endsWith(".jpg") || 
                              nomeLower.endsWith(".jpeg");

        if (!extensaoValida) {
            exibirAlerta(`O arquivo "${arquivo.name}" possui formato inválido. Apenas PNG ou JPEG são aceitos.`);
            return;
        }

        // Validação de tamanho (limite de 5MB)
        const limiteTamanho = 5 * 1024 * 1024; // 5 Megabytes
        if (arquivo.size > limiteTamanho) {
            exibirAlerta(`O arquivo "${arquivo.name}" excede o tamanho máximo permitido de 5MB.`);
            return;
        }

        // Se passar em todas as pré-validações do cliente, inicia o upload na esteira
        iniciarUploadEsteira(arquivo);
    });
}

function exibirAlerta(mensagem) {
    const divAlerta = document.createElement("div");
    divAlerta.className = "alerta-erro";
    divAlerta.innerHTML = `<span>⚠️</span> <p>${mensagem}</p>`;
    areaAlertas.appendChild(divAlerta);

    // Auto-remove alertas após 8 segundos para não poluir visualmente a console
    setTimeout(() => {
        divAlerta.style.opacity = "0";
        divAlerta.style.transform = "translateY(-5px)";
        divAlerta.style.transition = "all 0.3s ease";
        setTimeout(() => divAlerta.remove(), 300);
    }, 8000);
}

function limparAlertas() {
    areaAlertas.innerHTML = "";
}

/* ==========================================
   3. Criação de Linha de Monitoramento (Tabela)
   ========================================== */
function criarLinhaTabela(idTemporario, nomeArquivo) {
    // Esconde a linha padrão de "Esteira Vazia" caso exista
    if (linhaVazia) {
        linhaVazia.style.display = "none";
    }

    const tr = document.createElement("tr");
    tr.id = `job-${idTemporario}`;
    
    tr.innerHTML = `
        <td class="nome-arquivo-td" title="${nomeArquivo}">${nomeArquivo}</td>
        <td class="uuid-td" id="uuid-${idTemporario}">
            <span style="opacity: 0.5;">Aguardando ID...</span>
        </td>
        <td id="status-${idTemporario}">
            <span class="badge-status pendente">
                <span class="spinner-status"></span>
                Enviando...
            </span>
        </td>
        <td id="acoes-${idTemporario}">
            <span style="opacity: 0.5; font-size: 0.85rem;">Aguardando processamento...</span>
        </td>
    `;

    listaJobs.insertBefore(tr, listaJobs.firstChild);
}

/* ==========================================
   4. Upload e Pooling de Rastreabilidade E2E
   ========================================== */
function iniciarUploadEsteira(arquivo) {
    const idTemporario = uuidv4();
    criarLinhaTabela(idTemporario, arquivo.name);

    // Monta o formulário de envio Multipart
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    formData.append("id_vendedor", ID_VENDEDOR_PADRAO);

    fetch(`${ENDPOINT_API}/enviar`, {
        method: "POST",
        body: formData
    })
    .then(async resposta => {
        if (!resposta.ok) {
            const erroJSON = await resposta.json().catch(() => ({}));
            throw new Error(erroJSON.detail || `Erro HTTP ${resposta.status}`);
        }
        return resposta.json();
    })
    .then(dados => {
        const idTrabalho = dados.id_trabalho;
        
        // Atualiza a linha da tabela com o ID real e status PENDENTE
        document.getElementById(`uuid-${idTemporario}`).innerHTML = `
            ${idTrabalho.substring(0, 8)}...
            <span class="copiar-uuid" onclick="navigator.clipboard.writeText('${idTrabalho}')" title="Copiar UUID completo">Copiar</span>
        `;

        // Modifica a linha correspondente para usar o ID real do trabalho no rastreamento
        const trJob = document.getElementById(`job-${idTemporario}`);
        trJob.id = `job-${idTrabalho}`;
        
        const tdStatus = document.getElementById(`status-${idTemporario}`);
        tdStatus.id = `status-${idTrabalho}`;
        tdStatus.innerHTML = `<span class="badge-status pendente">Pendente</span>`;

        const tdAcoes = document.getElementById(`acoes-${idTemporario}`);
        tdAcoes.id = `acoes-${idTrabalho}`;
        tdAcoes.innerHTML = `<span style="opacity: 0.7; font-size: 0.85rem;">Enfileirado...</span>`;

        // Inicializa o Pooling reativo periódico (a cada 2 segundos)
        iniciarPooling(idTrabalho);
    })
    .catch(erro => {
        console.error(erro);
        
        // Altera o status visual para FALHOU de forma imediata
        const tdStatus = document.getElementById(`status-${idTemporario}`);
        tdStatus.innerHTML = `<span class="badge-status falhou">FALHOU</span>`;

        const tdAcoes = document.getElementById(`acoes-${idTemporario}`);
        tdAcoes.innerHTML = `
            <span class="mensagem-erro-td" title="${erro.message}">${erro.message}</span>
        `;
    });
}

function iniciarPooling(idTrabalho) {
    // Roda a verificação periódica de 2 em 2 segundos
    const interValId = setInterval(() => {
        verificarStatusTrabalho(idTrabalho, interValId);
    }, 2000);

    jobsAtivos[idTrabalho] = interValId;
}

function verificarStatusTrabalho(idTrabalho, intervalId) {
    fetch(`${ENDPOINT_API}/status/${idTrabalho}`)
    .then(resposta => {
        if (!resposta.ok) {
            throw new Error("Erro ao consultar status");
        }
        return resposta.json();
    })
    .then(dados => {
        const status = dados.status;
        const tdStatus = document.getElementById(`status-${idTrabalho}`);
        const tdAcoes = document.getElementById(`acoes-${idTrabalho}`);

        if (!tdStatus || !tdAcoes) {
            clearInterval(intervalId);
            return;
        }

        if (status === "PENDENTE") {
            tdStatus.innerHTML = `<span class="badge-status pendente">Pendente</span>`;
        } 
        else if (status === "PROCESSANDO") {
            tdStatus.innerHTML = `
                <span class="badge-status processando">
                    <span class="spinner-status"></span>
                    Otimizando...
                </span>
            `;
            tdAcoes.innerHTML = `<span style="opacity: 0.8; font-size: 0.85rem;">Convertendo para WebP...</span>`;
        } 
        else if (status === "CONCLUIDO") {
            // Limpa o loop do pooling de verificação
            clearInterval(intervalId);
            delete jobsAtivos[idTrabalho];

            tdStatus.innerHTML = `<span class="badge-status concluido">Concluído</span>`;
            
            // Renderiza com sofisticação os links de downloads das 3 mídias WebP otimizadas
            // O Nginx do front servirá estaticamente a pasta definitiva mapeada no volume via `/assets/`
            const linkMiniatura = `/assets/${ID_VENDEDOR_PADRAO}/${idTrabalho}/miniatura.webp`;
            const linkMedia = `/assets/${ID_VENDEDOR_PADRAO}/${idTrabalho}/media.webp`;
            const linkGrande = `/assets/${ID_VENDEDOR_PADRAO}/${idTrabalho}/grande.webp`;

            tdAcoes.innerHTML = `
                <div class="grupo-downloads">
                    <a href="${linkMiniatura}" target="_blank" class="link-download" title="Ver Miniatura (150x150)">
                        <span class="icone-download">🖼️</span> Mini
                    </a>
                    <a href="${linkMedia}" target="_blank" class="link-download" title="Ver Média (640x640)">
                        <span class="icone-download">🖼️</span> Média
                    </a>
                    <a href="${linkGrande}" target="_blank" class="link-download" title="Ver Alta Resolução (1920x1920)">
                        <span class="icone-download">🖼️</span> Alta
                    </a>
                </div>
            `;
        } 
        else if (status === "FALHOU") {
            clearInterval(intervalId);
            delete jobsAtivos[idTrabalho];

            tdStatus.innerHTML = `<span class="badge-status falhou">Falhou</span>`;
            
            const erroMensagem = dados.mensagem_erro || "Erro desconhecido";
            tdAcoes.innerHTML = `
                <span class="mensagem-erro-td" title="${erroMensagem}">${erroMensagem}</span>
            `;
        }
    })
    .catch(erro => {
        console.error("Erro no polling: ", erro);
    });
}

// Auxiliar: Gerador de UUID v4 simples para simular IDs temporários no Front
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
