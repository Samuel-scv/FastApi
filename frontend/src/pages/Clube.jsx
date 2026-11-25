import { Caixa } from '../components/Caixa'
import { Preco } from '../components/Etiquetas'
import { acharOuCriar, api } from '../lib/api'
import { dataBR, dinheiro } from '../lib/formatar'

export default function Clube({ dados, recarregar }) {
  const assinar = async (p) => {
    const nome = (prompt('Seu nome completo:') || '').trim(); if (!nome) return
    const fone = (prompt('Seu telefone:') || '').trim(); if (!fone) return
    try {
      let c = await acharOuCriar(nome, fone)
      c = await api('PUT', `/clientes/${c.id}`, { plano_id: p.id })
      await recarregar()
      alert(`Bem vindo novo membro!\n\n${c.nome} agora e socio do ${p.nome}.\nCarteirinha valida ate ${dataBR(c.plano_vencimento)}.\nA mensalidade de ${dinheiro(p.preco_mensal)} e paga no balcao.`)
    } catch (e) { alert(`NAO FOI POSSIVEL ASSINAR:\n${e.message}`) }
  }
  const cores = ['#999999', '#ffcc00', '#66ffff']
  return (
    <>
      <Caixa titulo="Clube de socios Galaxia">
        <p>Vire socio e tenha mais prazo e menos multa! A carteirinha e feita na hora, e gratis.</p>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
          {dados.planos.map((p, i) => (
            <div key={p.id} className="ridge border-[3px] bg-[#111144] p-2 text-center" style={{ borderColor: cores[i % 3] }}>
              <div className="flex h-[110px] items-center justify-center border-2 border-black font-sans text-[15px] font-bold" style={{ color: cores[i % 3], background: `linear-gradient(180deg,#333,${cores[i % 3]}44 50%,#333)` }}>{p.nome}</div>
              <p><Preco v={p.preco_mensal} /><br /><span className="text-xs">por mes</span></p>
              <p className="text-[13px]">{p.beneficios}</p>
              <p><b>{p.limite_mensal}</b> fitas inclusas no mes</p>
              <button className="bt" onClick={() => assinar(p)}>ASSINAR AGORA</button>
            </div>
          ))}
        </div>
      </Caixa>
      <Caixa titulo="Perguntas mais frequentes">
        <p className="mb-2"><b>P: E se eu atrasar a devolucao?</b><br />R: Cobramos multa por dia e por fita. Enquanto houver fita atrasada, a conta fica bloqueada para novas locacoes.</p>
        <p className="mb-2"><b>P: Posso comprar a fita em vez de alugar?</b><br />R: Pode! Fale com o seu Jorge no balcao. A fita sai do estoque na hora.</p>
        <p><b>P: Voces tem DVD?</b><br />R: Estamos estudando. Por enquanto so VHS e algumas fitas em Betamax no fundo da loja.</p>
      </Caixa>
    </>
  )
}