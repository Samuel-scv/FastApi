import { useState } from 'react'
import { Caixa, Arco } from '../components/Caixa'
import { salvarLocal } from '../lib/local'

export default function Recados({ local, setLocal }) {
  const [r, setR] = useState({ nome: '', cidade: '', txt: '' })
  const assinarLivro = () => {
    if (!r.nome.trim() || !r.txt.trim()) return alert('Escreva pelo menos o nome e o recado!')
    const novo = { ...local, recados: [{ nome: r.nome.trim(), cidade: r.cidade.trim() || 'internet', txt: r.txt.trim() }, ...local.recados] }
    salvarLocal(novo); setLocal(novo); setR({ nome: '', cidade: '', txt: '' })
    alert('Recado assinado! Obrigado pela visita :)')
  }
  return (
    <Caixa titulo="Livro de visitas">
      <p>Deixe seu recado! Nao vale palavrao, o seu Jorge le tudo.</p>
      <div className="grid gap-3.5 sm:grid-cols-2">
        <div><label className="rotulo">SEU NOME OU APELIDO</label><input className="campo" value={r.nome} onChange={(e) => setR({ ...r, nome: e.target.value })} /></div>
        <div><label className="rotulo">SUA CIDADE</label><input className="campo" value={r.cidade} onChange={(e) => setR({ ...r, cidade: e.target.value })} /></div>
      </div>
      <label className="rotulo">RECADO</label><textarea className="campo" rows={3} value={r.txt} onChange={(e) => setR({ ...r, txt: e.target.value })} />
      <p className="mt-2.5 text-center"><button className="bt bt-grande" onClick={assinarLivro}>ASSINAR O LIVRO</button></p>
      <Arco />
      {local.recados.map((x, i) => (
        <div key={i} className="mb-2 border-l-[5px] border-rosa bg-[#110022] p-2 text-sm"><b className="text-ouro">{x.nome}</b> <span className="text-xs text-[#99ccff]">({x.cidade})</span><br />{x.txt}</div>
      ))}
    </Caixa>
  )
}
