import { useEffect, useState } from 'react'
import AvisoEquipe from '../components/AvisoEquipe'
import { Aviso, Secao } from '../components/Secao'
import { api, query } from '../lib/api'
import { dataHora } from '../lib/formatar'

export default function PerguntasVendedor({ equipe, usuario, ir }) {
  const [status, setStatus] = useState('pendente')
  const [lista, setLista] = useState(null)
  const [respostas, setRespostas] = useState({})
  const [aviso, setAviso] = useState({ texto: '', erro: false })

  const falhar = (e) => setAviso({ texto: e.message, erro: true })
  const carregar = async () => {
    try { setLista(await api('GET', `/perguntas${query({ status })}`)) } catch (e) { falhar(e) }
  }
  useEffect(() => { if (equipe) carregar() }, [equipe, status])

  if (!equipe) return <AvisoEquipe usuario={usuario} ir={ir} />

  const responder = async (p) => {
    const t = (respostas[p.id] || '').trim()
    if (!t) return setAviso({ texto: 'Escreva a resposta.', erro: true })
    try {
      await api('POST', `/perguntas/${p.id}/resposta`, { texto: t })
      setRespostas({ ...respostas, [p.id]: '' })
      setAviso({ texto: 'Resposta registrada.', erro: false })
      await carregar()
    } catch (e) { falhar(e) }
  }
  const apagar = async (p) => {
    if (!confirm('Apagar esta pergunta?')) return
    try { await api('DELETE', `/perguntas/${p.id}`); setAviso({ texto: 'Pergunta apagada.', erro: false }); await carregar() } catch (e) { falhar(e) }
  }

  return (
    <Secao titulo="Caixa de perguntas">
      <label>Situacao{' '}
        <select className="s-campo !w-auto" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="pendente">pendentes</option><option value="respondida">respondidas</option><option value="">todas</option>
        </select>
      </label>
      <Aviso aviso={aviso} />
      <div className="mt-3">
        {lista && lista.length === 0 && <p>Nenhuma pergunta.</p>}
        {(lista || []).map((p) => (
          <div key={p.id} className="mb-4 border-b border-[#444] pb-3">
            <p>{p.titulo} - {p.autor}, {dataHora(p.criada_em)} ({p.status})</p>
            <p>{p.texto}</p>
            {p.status === 'respondida' ? (
              <p className="text-[#aaa]">Resposta ({p.vendedor}, {dataHora(p.respondida_em)}): {p.resposta}</p>
            ) : (
              <>
                <textarea className="s-campo mt-2" rows={2} maxLength={1000} placeholder="Resposta" value={respostas[p.id] || ''} onChange={(e) => setRespostas({ ...respostas, [p.id]: e.target.value })} />
                <p className="mt-2"><button className="s-bt" onClick={() => responder(p)}>Responder</button> <button className="s-bt" onClick={() => apagar(p)}>Apagar</button></p>
              </>
            )}
            {p.status === 'respondida' && <p className="mt-1"><button className="s-bt" onClick={() => apagar(p)}>Apagar</button></p>}
          </div>
        ))}
      </div>
    </Secao>
  )
}
