import { useState } from 'react'
import { Caixa, Arco } from '../components/Caixa'
import { acharOuCriar, api } from '../lib/api'
import { dataBR, dinheiro, hojeISO } from '../lib/formatar'

export default function Alugar({ dados, recarregar, fitaInicial, equipe }) {
  const [f, setF] = useState({ nome: '', fone: '', cidade: '', fita: fitaInicial || '', dias: 2 })
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const nomeC = (id) => dados.clientes.find((c) => c.id === id)?.nome ?? `#${id}`
  const titulo = (id) => dados.produtos.find((p) => p.id === id)?.titulo ?? `#${id}`

  const enviar = async () => {
    if (!f.nome.trim()) return alert('PREENCHA O SEU NOME!!!')
    if (!f.fone.trim()) return alert('Precisamos do telefone para avisar do vencimento.')
    if (!f.fita) return alert('Escolha uma fita!')
    try {
      const c = await acharOuCriar(f.nome.trim(), f.fone.trim(), f.cidade.trim())
      const a = await api('POST', '/alugueis', { cliente_id: c.id, produto_id: Number(f.fita), dias: Number(f.dias) })
      await recarregar()
      alert(`FICHA REGISTRADA COM SUCESSO!!!\n\nFita: ${titulo(a.produto_id)}\nValor: ${dinheiro(a.valor)}\nDevolver ate: ${dataBR(a.data_prevista)}\n\nPasse na loja para retirar. E nao esqueca de rebobinar!`)
    } catch (e) { alert(`NAO FOI POSSIVEL ALUGAR:\n${e.message}`) }
  }

  const devolver = async (a) => {
    if (!equipe) return
    const m = a.multa_estimada
    if (!confirm(`Receber de volta "${titulo(a.produto_id)}"?` + (m ? `\n\nMULTA DE ${dinheiro(m)} POR ${a.dias_atraso} DIA(S) DE ATRASO.` : ''))) return
    try {
      const r = await api('POST', `/alugueis/${a.id}/devolucao`, {})
      await recarregar()
      alert(r.multa_paga ? `Fita recebida. Cobrar ${dinheiro(r.multa_paga)} de multa no caixa.` : 'Fita recebida e de volta na prateleira. Obrigado!')
    } catch (e) { alert(`NAO FOI POSSIVEL DEVOLVER:\n${e.message}`) }
  }

  return (
    <>
      <Caixa titulo="Ficha de locacao">
        <p>Preencha seus dados abaixo. Sua fita fica reservada no balcao por 24 horas.</p>
        <div className="grid gap-3.5 sm:grid-cols-2">
          <div>
            <label className="rotulo">SEU NOME COMPLETO</label><input className="campo" value={f.nome} onChange={set('nome')} />
            <label className="rotulo">TELEFONE</label><input className="campo" value={f.fone} onChange={set('fone')} placeholder="(018) 000-0000" />
            <label className="rotulo">CIDADE</label><input className="campo" value={f.cidade} onChange={set('cidade')} placeholder="Aracatuba-SP" />
          </div>
          <div>
            <label className="rotulo">ESCOLHA A FITA</label>
            <select className="campo" value={f.fita} onChange={set('fita')}>
              <option value="">-- escolha --</option>
              {dados.produtos.map((p) => <option key={p.id} value={p.id} disabled={p.estoque < 1}>{p.titulo} - {dinheiro(p.preco_aluguel)}{p.estoque < 1 ? ' (ALUGADA)' : ''}</option>)}
            </select>
            <label className="rotulo">QUANTOS DIAS</label>
            <select className="campo" value={f.dias} onChange={set('dias')}>{[1, 2, 3, 5, 7].map((d) => <option key={d}>{d}</option>)}</select>
          </div>
        </div>
        <p className="mt-3.5 text-center"><button className="bt bt-grande" onClick={enviar}>ENVIAR FICHA &gt;&gt;&gt;</button></p>
        <p className="text-xs text-[#ccc]">Atrasou? A multa e cobrada por dia, por fita, e a conta fica bloqueada ate a devolucao. Socio do clube pode ganhar dias extras de prazo.</p>
      </Caixa>

      {equipe && (
        <>
          <Arco />
          <Caixa titulo="Fitas que estao na rua">
            {dados.alugueis.length === 0 ? <p>Nenhuma fita fora da loja no momento. Todas na prateleira!</p> : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse bg-[#000055] text-sm">
                  <thead><tr>{['CLIENTE', 'FITA', 'RETIRADA', 'DEVOLVER ATE', 'SITUACAO', ''].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
                  <tbody>
                    {dados.alugueis.map((a) => (
                      <tr key={a.id}>
                        <td className="td">{nomeC(a.cliente_id)}</td><td className="td">{titulo(a.produto_id)}</td>
                        <td className="td">{dataBR(a.data_retirada)}</td><td className="td">{dataBR(a.data_prevista)}</td>
                        <td className="td">
                          {a.dias_atraso > 0 ? <span className="pisca font-bold text-[#ff6666]">ATRASADA {a.dias_atraso} DIA(S) - MULTA {dinheiro(a.multa_estimada)}</span>
                            : a.data_prevista === hojeISO() ? <span className="text-ouro">VENCE HOJE</span> : <span className="font-bold text-verde">EM DIA</span>}
                        </td>
                        <td className="td"><button className="bt" onClick={() => devolver(a)}>DEVOLVER</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Caixa>
        </>
      )}
    </>
  )
}