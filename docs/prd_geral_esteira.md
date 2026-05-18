# Documento de Requisitos do Produto (PRD) - Esteira de Mídias

Este documento detalha os requisitos e especificações para o projeto **Esteira de Mídias** (também chamado de **Esteira**), uma plataforma de processamento assíncrono de mídias projetada para o ecossistema de marketplace.

---

## 1. Visão Geral e Objetivo

A **Esteira de Mídias** é uma plataforma de processamento assíncrono de mídias projetada para o ecossistema de marketplace. 

O objetivo é permitir que lojistas façam upload de imagens de produtos em alta resolução de forma rápida e segura. O sistema deve receber esses arquivos, enfileirá-los e processá-los em segundo plano (gerando versões otimizadas em WebP para web e mobile), sem impactar a performance da API principal, garantindo alta disponibilidade e segurança.

---

## 2. O Problema que Resolvemos

*   **Lentidão no Upload Síncrono:** APIs tradicionais travam enquanto processam imagens, causando *timeout*.
*   **Custo de Armazenamento/Banda:** Imagens pesadas e não otimizadas aumentam custos de CDN e pioram o SEO do e-commerce.
*   **Vulnerabilidade:** Uploads de arquivos são vetores comuns de ataques (arquivos maliciosos ou *payloads* gigantes que derrubam o servidor).

---

## 3. Escopo Macro (O que será entregue)

*   **Frontend Administrativo Simples:** Tela para arrastar e soltar múltiplas imagens, com feedback visual do status ("Enviado", "Processando", "Concluído").
*   **API Gateway / Core (Backend):** Rota segura para receber as imagens, validar os dados e colocar na fila de processamento.
*   **Serviço de Mensageria:** Fila (*Broker*) para gerenciar o fluxo de trabalhos pendentes.
*   **Processador de Otimização (Worker):** Microsserviço isolado que consome a fila, reduz a imagem, converte para `.webp` e salva as versões (*Miniatura*, *Média*, *Grande*).
*   **Setup de Infraestrutura:** Arquivo `docker-compose.yml` para rodar todos os serviços simultaneamente de forma orquestrada.

---

## 4. Requisitos Não-Funcionais (Atendendo à Vaga Magalu Cloud)

### Segurança (Security-First)
*   **Controle de Taxa (Rate Limiting):** Implementação de limite de taxa (ex: máximo de 10 uploads por minuto por IP).
*   **Validação Rigorosa de Arquivos:** Verificar o *"Magic Byte"* do arquivo (e não apenas a extensão `.jpg` ou `.png`) para evitar injeção de malware.
*   **Tamanho do Payload:** Limite de tamanho (ex: máximo de 5MB por arquivo).

### Escalabilidade & Performance
*   **Arquitetura Orientada a Eventos:** Processamento assíncrono. Se o volume de imagens crescer, basta adicionar mais instâncias do *Worker* (Processador) sem a necessidade de alterar a API Principal.

### Boas Práticas & Qualidade (CI/CD)
*   **Testes Automatizados:** Testes unitários e de integração essenciais (ex: testar se a API bloqueia arquivos falsos e se a fila recebe a mensagem de forma correta).
*   **Pipeline Integrada:** Pipeline no GitHub Actions que bloqueia o *merge* se os testes quebrarem.
*   **Código Limpo:** Estruturado seguindo boas práticas de Arquitetura Limpa (*Clean Architecture*) e ferramenta de *linting* ativa.
