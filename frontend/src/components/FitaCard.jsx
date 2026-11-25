import { Novo, Preco, Estoque } from './Etiquetas'

export default function FitaCard({ p, onAlugar }) {
  return (
    <div className="ridge border-[3px] border-[#aa7700] bg-[#111144] p-2 text-center">
      <div className="flex h-[110px] items-center justify-center border-2 border-black bg-gradient-to-b from-[#222] via-[#555] to-[#222] p-1.5 font-sans text-[13px] font-bold">{p.titulo}</div>
      <p className="leading-relaxed"><Novo /><br /><b>{p.genero}</b> &middot; {p.ano || '-'}<br /><Preco v={p.preco_aluguel} /><br /><Estoque n={p.estoque} /></p>
      <button className="bt" onClick={() => onAlugar(p.id)}>QUERO ESSA!</button>
    </div>
  )
}
