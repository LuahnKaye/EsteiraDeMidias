import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import axios from 'axios';

// Moca a biblioteca axios para garantir que a rede real não seja acionada
vi.mock('axios');

describe('Segurança no Cliente - Upload de Arquivos', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve bloquear upload de imagem maior que 5MB (10MB simulado) e não disparar chamada HTTP', async () => {
    render(<App />);

    // Cria um arquivo simulado de 10MB
    const tamanhoDe10MB = 10 * 1024 * 1024;
    const arrayDeBytes = new Uint8Array(tamanhoDe10MB);
    const arquivoGigante = new File([arrayDeBytes], 'imagem_gigante.png', { type: 'image/png' });

    // Localiza o input do dropzone
    const input = screen.getByTestId('input-arquivo');
    
    // Dispara o evento de seleção
    fireEvent.change(input, { target: { files: [arquivoGigante] } });

    // Aguarda e valida se o alerta de erro foi exibido na tela
    await waitFor(() => {
      const alerta = screen.getByTestId('alerta-erro');
      expect(alerta).toBeInTheDocument();
      expect(alerta).toHaveTextContent('excede o tamanho máximo permitido de 5MB');
    });

    // CRÍTICO: Garante que o Axios NÃO foi chamado em nenhum momento (Economia de banda e bloqueio ativo)
    expect(axios.post).not.toHaveBeenCalled();
  });
});
