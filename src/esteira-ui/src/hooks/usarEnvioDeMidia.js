import { useState, useRef } from 'react';
import axios from 'axios';

const ENDPOINT_API = "http://localhost:8000/api/v1/midias";
const ID_VENDEDOR_PADRAO = "1fb993c0-1839-4bd6-9243-7d161cc77345";

export function usarEnvioDeMidia() {
    const [jobs, setJobs] = useState([]);
    const [alerta, setAlerta] = useState(null);
    const pollingRefs = useRef({});

    const mostrarAlerta = (mensagem) => {
        setAlerta(mensagem);
        setTimeout(() => setAlerta(null), 8000);
    };

    const processarArquivos = (arquivos) => {
        setAlerta(null);
        if (!arquivos || arquivos.length === 0) return;

        if (arquivos.length > 5) {
            mostrarAlerta("Limite excedido: Você pode enviar no máximo 5 arquivos por vez.");
            return;
        }

        Array.from(arquivos).forEach(arquivo => {
            const extensoesPermitidas = ["image/png", "image/jpeg", "image/jpg"];
            const nomeLower = arquivo.name.toLowerCase();
            const extensaoValida = extensoesPermitidas.includes(arquivo.type) || 
                                  nomeLower.endsWith(".png") || 
                                  nomeLower.endsWith(".jpg") || 
                                  nomeLower.endsWith(".jpeg");

            if (!extensaoValida) {
                mostrarAlerta(`O arquivo "${arquivo.name}" possui formato inválido. Apenas PNG ou JPEG são aceitos.`);
                return;
            }

            const limiteTamanho = 5 * 1024 * 1024; // 5MB
            if (arquivo.size > limiteTamanho) {
                mostrarAlerta(`O arquivo "${arquivo.name}" excede o tamanho máximo permitido de 5MB.`);
                return;
            }

            iniciarUploadEsteira(arquivo);
        });
    };

    const iniciarUploadEsteira = async (arquivo) => {
        const idTemporario = crypto.randomUUID();
        
        const novoJob = {
            id: idTemporario,
            nomeArquivo: arquivo.name,
            status: "ENVIANDO",
            erro: null
        };

        setJobs(prev => [novoJob, ...prev]);

        const formData = new FormData();
        formData.append("arquivo", arquivo);
        formData.append("id_vendedor", ID_VENDEDOR_PADRAO);

        try {
            const resposta = await axios.post(`${ENDPOINT_API}/enviar`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            const idTrabalho = resposta.data.id_trabalho;
            
            setJobs(prev => prev.map(job => 
                job.id === idTemporario 
                ? { ...job, id: idTrabalho, status: "PENDENTE" } 
                : job
            ));

            iniciarPolling(idTrabalho);
            
        } catch (erro) {
            const erroMensagem = erro.response?.data?.detail || erro.message;
            setJobs(prev => prev.map(job => 
                job.id === idTemporario 
                ? { ...job, status: "FALHOU", erro: erroMensagem } 
                : job
            ));
        }
    };

    const iniciarPolling = (idTrabalho) => {
        const intervalId = setInterval(() => {
            verificarStatusTrabalho(idTrabalho, intervalId);
        }, 2000);
        pollingRefs.current[idTrabalho] = intervalId;
    };

    const verificarStatusTrabalho = async (idTrabalho, intervalId) => {
        try {
            const resposta = await axios.get(`${ENDPOINT_API}/status/${idTrabalho}`);
            const status = resposta.data.status;
            
            setJobs(prev => prev.map(job => 
                job.id === idTrabalho 
                ? { ...job, status: status, erro: status === 'FALHOU' ? resposta.data.mensagem_erro : null } 
                : job
            ));

            if (status === "CONCLUIDO" || status === "FALHOU") {
                clearInterval(intervalId);
                delete pollingRefs.current[idTrabalho];
            }
        } catch (erro) {
            console.error("Erro no polling: ", erro);
        }
    };

    return { jobs, alerta, processarArquivos, ID_VENDEDOR_PADRAO };
}
