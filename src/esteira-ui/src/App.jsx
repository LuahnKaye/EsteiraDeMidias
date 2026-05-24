import React, { useRef, useState } from 'react';
import { usarEnvioDeMidia } from './hooks/usarEnvioDeMidia';

function App() {
  const { jobs, alerta, processarArquivos, ID_VENDEDOR_PADRAO } = usarEnvioDeMidia();
  const inputRef = useRef(null);
  const [arrastando, setArrastando] = useState(false);

  const lidarComDragOver = (e) => {
    e.preventDefault();
    setArrastando(true);
  };
  
  const lidarComDragLeave = (e) => {
    e.preventDefault();
    setArrastando(false);
  };

  const lidarComDrop = (e) => {
    e.preventDefault();
    setArrastando(false);
    processarArquivos(e.dataTransfer.files);
  };

  const lidarComSelecao = (e) => {
    processarArquivos(e.target.files);
    e.target.value = '';
  };

  return (
    <>
      <div className="fundo-gradiente" />
      <div className="conteiner-app">
        <header className="text-center space-y-2">
          <div className="flex items-center justify-center gap-3">
            <span className="text-4xl">⚡</span>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300">Esteira de Mídias</h1>
          </div>
          <p className="text-slate-400 text-lg">Console de Processamento e Otimização Assíncrona de Imagens</p>
        </header>

        <section className="secao-upload card-glass">
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-1">Otimizar Novas Imagens</h2>
            <p className="text-slate-400 text-sm">Arraste e solte seus arquivos ou clique na área abaixo. Limite de até 5 imagens de 5MB nos formatos PNG ou JPEG.</p>
          </div>
          
          <div 
            data-testid="area-dropzone"
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${arrastando ? 'border-blue-400 bg-blue-500/10' : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/30'}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={lidarComDragOver}
            onDragLeave={lidarComDragLeave}
            onDrop={lidarComDrop}
          >
            <input 
              type="file" 
              ref={inputRef} 
              multiple 
              accept="image/png, image/jpeg, image/jpg" 
              className="hidden" 
              onChange={lidarComSelecao}
              data-testid="input-arquivo"
            />
            <div className="flex flex-col items-center gap-3">
              <span className={`text-5xl ${arrastando ? 'opacity-100' : 'opacity-50'}`}>☁️</span>
              <p className="font-medium text-lg">Arraste múltiplos arquivos ou <span className="text-blue-400 font-semibold">clique para selecionar</span></p>
              <p className="text-slate-500 text-sm">Formatos aceitos: PNG, JPEG ou JPG (Máx. 5MB por imagem)</p>
            </div>
          </div>

          {alerta && (
            <div className="mt-4 p-4 bg-rose-500/20 border border-rose-500/30 rounded-lg flex items-center gap-3 text-rose-300 transition-all animate-in fade-in zoom-in duration-300" data-testid="alerta-erro">
              <span className="text-xl flex-shrink-0">⚠️</span>
              <p>{alerta}</p>
            </div>
          )}
        </section>

        <section className="secao-monitoramento card-glass">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold mb-1">Painel de Monitoramento</h2>
              <p className="text-slate-400 text-sm">Acompanhe em tempo real os status das suas mídias otimizadas na esteira</p>
            </div>
            <div className="flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-full border border-slate-700/50">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs font-medium text-emerald-400">Conexão Ativa</span>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-700/50 bg-slate-900/30">
            <table className="tabela-jobs w-full text-left">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="p-4 border-b border-slate-700 text-slate-400 font-medium text-sm">Nome do Arquivo</th>
                  <th className="p-4 border-b border-slate-700 text-slate-400 font-medium text-sm">ID do Trabalho (UUID)</th>
                  <th className="p-4 border-b border-slate-700 text-slate-400 font-medium text-sm">Status da Esteira</th>
                  <th className="p-4 border-b border-slate-700 text-slate-400 font-medium text-sm">Imagens Otimizadas (WebP)</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="text-center py-12 text-slate-500 border-b border-slate-700/50">
                      <div className="flex flex-col items-center gap-2">
                        <span className="text-3xl opacity-50">📥</span>
                        <p>Nenhuma imagem na esteira de processamento no momento.</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  jobs.map(job => (
                    <tr key={job.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-4 border-b border-slate-700/50 font-medium text-slate-200 text-sm">{job.nomeArquivo}</td>
                      <td className="p-4 border-b border-slate-700/50 font-mono text-xs opacity-75 text-slate-200">{job.id.substring(0,8)}...</td>
                      <td className="p-4 border-b border-slate-700/50 text-slate-200 text-sm">
                        {job.status === 'ENVIANDO' && <span className="badge-status pendente"><span className="spinner-status"></span> Enviando...</span>}
                        {job.status === 'PENDENTE' && <span className="badge-status pendente">⏳ Pendente</span>}
                        {job.status === 'PROCESSANDO' && <span className="badge-status processando"><span className="spinner-status"></span> Otimizando...</span>}
                        {job.status === 'CONCLUIDO' && <span className="badge-status concluido">✅ Concluído</span>}
                        {job.status === 'FALHOU' && <span className="badge-status falhou">❌ Falhou</span>}
                      </td>
                      <td className="p-4 border-b border-slate-700/50 text-slate-200 text-sm">
                        {job.status === 'PROCESSANDO' && <span className="text-xs opacity-60">Convertendo para WebP...</span>}
                        {job.status === 'FALHOU' && <span className="text-xs text-rose-400 truncate block max-w-xs" title={job.erro}>{job.erro}</span>}
                        {job.status === 'CONCLUIDO' && (
                          <div className="flex gap-2">
                            <a href={`/assets/${ID_VENDEDOR_PADRAO}/${job.id}/miniatura.webp`} target="_blank" className="flex items-center gap-1 text-xs bg-slate-700/50 hover:bg-slate-600 px-2 py-1 rounded text-slate-300 hover:text-white transition-colors" title="Ver Miniatura (150x150)">🖼️ Mini</a>
                            <a href={`/assets/${ID_VENDEDOR_PADRAO}/${job.id}/media.webp`} target="_blank" className="flex items-center gap-1 text-xs bg-slate-700/50 hover:bg-slate-600 px-2 py-1 rounded text-slate-300 hover:text-white transition-colors" title="Ver Média (640x640)">🖼️ Média</a>
                            <a href={`/assets/${ID_VENDEDOR_PADRAO}/${job.id}/grande.webp`} target="_blank" className="flex items-center gap-1 text-xs bg-slate-700/50 hover:bg-slate-600 px-2 py-1 rounded text-slate-300 hover:text-white transition-colors" title="Ver Alta (1920x1920)">🖼️ Alta</a>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </>
  );
}

export default App;
