import { useEffect, useState } from 'react'
import { Aviso, Secao } from '../components/Secao'
import { api } from '../lib/api'
import { dataHora } from '../lib/formatar'

export default function Perguntas({ dados, usuario, ir }) {
  const [produtoId, setProdutoId] = useState('')
  const [publicas, setPublicas] = useState([])
  const [minhas, setMinhas] = useState([])
  const [texto, setTexto] = useState('')
  const [aviso, setAviso] = useState({ texto: '', erro: false })

  const falhar = (e) => setAviso({ texto: e.message, erro: true })

  const carregarPublicas = async () => {
    if (!produtoId) return setPublicas([])
    try { setPublicas(await api('GET', `/perguntas/produto/${produtoId}`)) } catch (e) { falhar(e) }
  }
  const carregarMinhas = async () => {
    if (!usuario) return setMinhas([])
    try { setMinhas(await api('GET', '/perguntas/minhas')) } catch (e) { falhar(e) }
  }

  useEffect(() => { carregarPublicas() }, [produtoId])
  useEffect(() => { carregarMinhas() }, [usuario])

  const perguntar = async () => {
    if (!produtoId) return setAviso({ texto: 'Escolha o titulo.', erro: true })
    if (texto.trim().length < 5) return setAviso({ texto: 'A pergunta precisa ter pelo menos 5 caracteres.', erro: true })
    try {
      await api('POST', `/perguntas/produto/${produtoId}`, { texto: texto.trim() })
      setTexto('')
      setAviso({ texto: 'Pergunta enviada. Ela aparece no titulo depois que um vendedor responder.', erro: false })
      await carregarMinhas()
    } catch (e) { falhar(e) }
  }
  const apagar = async (p) => {
    if (!confirm('Apagar esta pergunta?')) return
    try { await api('DELETE', `/perguntas/${p.id}`); setAviso({ texto: 'Pergunta apagada.', erro: false }); await carregarMinhas() } catch (e) { falhar(e) }
  }

  return (
    <>
      <Secao titulo="Perguntas sobre os titulos">
        <label className="s-rotulo">Titulo</label>
        <select className="s-campo" value={produtoId} onChange={(e) => { setProdutoId(e.target.value); setAviso({ texto: '', erro: false }) }}>
          <option value="">escolha</option>
          {dados.produtos.map((p) => <option key={p.id} value={p.id}>{p.titulo}</option>)}
        </select>
        {produtoId && (
          <div className="mt-3">
            {publicas.length === 0 ? <p>Nenhuma pergunta respondida para este titulo.</p> : publicas.map((p) => (
              <div key={p.id} className="mb-3 border-b border-[#444] pb-2">
                <p>{p.autor}, {dataHora(p.criada_em)}: {p.texto}</p>
                <p className="text-[#aaa]">Resposta ({p.vendedor}, {dataHora(p.respondida_em)}): {p.resposta}</p>
              </div>
            ))}
          </div>
        )}
      </Secao>

      <Secao titulo="Fazer uma pergunta">
        {usuario ? (
          <>
            <label className="s-rotulo">Pergunta (5 a 500 caracteres)</label>
            <textarea className="s-campo" rows={3} maxLength={500} value={texto} onChange={(e) => setTexto(e.target.value)} />
            <p className="mt-3"><button className="s-bt" onClick={perguntar}>Enviar</button></p>
          </>
        ) : (
          <p>Para perguntar e preciso entrar. <button className="s-bt" onClick={() => ir('entrar')}>Entrar</button></p>
        )}
        <Aviso aviso={aviso} />
      </Secao>

      {usuario && (
        <Secao titulo="Minhas perguntas">
          {minhas.length === 0 ? <p>Voce ainda nao fez perguntas.</p> : minhas.map((p) => (
            <div key={p.id} className="mb-3 border-b border-[#444] pb-2">
              <p>{p.titulo} ({dataHora(p.criada_em)}), {p.status}: {p.texto}</p>
              {p.resposta && <p className="text-[#aaa]">Resposta ({p.vendedor}): {p.resposta}</p>}
              {p.status === 'pendente' && <p className="mt-1"><button className="s-bt" onClick={() => apagar(p)}>Apagar</button></p>}
            </div>
          ))}
        </Secao>
      )}
    </>
  )
}
