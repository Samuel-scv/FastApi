import { useState } from 'react'
import { Caixa } from '../components/Caixa'
import { Estoque, Preco } from '../components/Etiquetas'
import { idade } from '../lib/formatar'

export default function Catalogo({ dados, alugarFita }) {
  const [aberto, setAberto] = useState(null)
  return (
    <Caixa titulo="Catalogo completo">
      <p className="mb-2">Total de <b>{dados.produtos.length}</b> titulos cadastrados. Clique no titulo para ver a sinopse.</p>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse bg-[#000055] text-sm">
          <thead><tr>{['TITULO', 'GENERO', 'ANO', 'IDADE', 'PRECO', 'SITUACAO', ''].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>
            {dados.produtos.map((p) => (
              <tr key={p.id} className="hover:bg-[#001188]">
                <td className="td">
                  <a className="cursor-pointer font-bold text-neon underline" onClick={() => setAberto(aberto === p.id ? null : p.id)}>{p.titulo}</a>
                  {aberto === p.id && <div className="mt-1 text-[13px] text-[#ccc]">{p.sinopse || 'Sem sinopse.'}</div>}
                </td>
                <td className="td">{p.genero}</td><td className="td">{p.ano || '-'}</td><td className="td">{idade(p)}</td>
                <td className="td"><Preco v={p.preco_aluguel} /></td><td className="td"><Estoque n={p.estoque} curto /></td>
                <td className="td"><button className="bt" onClick={() => alugarFita(p.id)}>ALUGAR</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Caixa>
  )
}
