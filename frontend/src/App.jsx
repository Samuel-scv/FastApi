import { useEffect, useState } from 'react'
import { api, acharOuCriar, getBase, setBase } from './api'

const PAGS = [['inicio', 'HOME'], ['catalogo', 'CATALOGO'], ['alugar', 'ALUGUE AQUI'], ['clube', 'CLUBE DE SOCIOS'], ['recados', 'LIVRO DE VISITAS'], ['sobre', 'QUEM SOMOS']]
const RECADOS = [
  { nome: 'Ricardinho', cidade: 'Aracatuba-SP', txt: 'Melhor locadora do bairro!! alugo aqui desde 96. abracos pro seu Jorge do balcao' },
  { nome: 'Fabi_Girl', cidade: 'Birigui', txt: 'adorei a homepage de voces!!! poe mais filme de romance por favor :):):)' },
  { nome: 'MASTER_DO_VHS', cidade: 'internet', txt: 'quem quiser trocar link comigo manda email. tenho pagina de dinossauros' },
]
const dinheiro = (v) => 'R$ ' + Number(v).toFixed(2).replace('.', ',')
const dataBR = (s) => (s ? s.split('-').reverse().join('/') : '-')
const hojeISO = () => new Date().toLocaleDateString('sv-SE')

function lerLocal() {
  let l = {}
  try { l = JSON.parse(localStorage.getItem('galaxia90')) || {} } catch { /* ignora */ }
  l.recados ||= RECADOS
  l.visitas = (l.visitas || 104872) + 1
  localStorage.setItem('galaxia90', JSON.stringify(l))
  return l
}

/* ---------- pecas ---------- */
const Caixa = ({ titulo, children }) => (
  <section className="outset mb-4 border-[3px] border-[#ccc] bg-caixa p-3">
    {titulo && <h2 className="mb-2 border-b-2 border-dotted border-ouro pb-1 font-['Comic_Sans_MS',cursive] text-2xl text-neon">{titulo}</h2>}
    {children}
  </section>
)
const Arco = () => <hr className="my-3.5 h-[5px] border-0 bg-gradient-to-r from-red-600 via-yellow-300 via-green-400 via-cyan-300 via-blue-600 to-fuchsia-500" />
const Preco = ({ v }) => <span className="font-mono text-[17px] font-bold text-[#00ff00]">{dinheiro(v)}</span>
const Estoque = ({ n, curto }) =>
  n > 0 ? <span className="font-bold text-verde">{n} {curto ? 'disp.' : 'fita(s) na prateleira'}</span> : <span className="font-bold text-[#ff6666]">{curto ? 'ALUGADA' : 'TODAS ALUGADAS'}</span>
const Novo = () => <span className="border border-red-600 bg-yellow-300 px-1 font-sans text-[10px] font-bold text-red-600">NOVO!</span>
const Idade = (p) => (p.classificacao === 'L' ? 'Livre' : `${p.classificacao} anos`)

/* ---------- paginas ---------- */
function Inicio({ dados, ir, alugarFita }) {
  const novos = [...dados.produtos].sort((a, b) => (b.ano || 0) - (a.ano || 0)).slice(0, 3)
  return (
    <>
      <div className="mb-3 border-[3px] border-double border-[#990000] bg-[#ffffcc] p-2 font-sans text-xs font-bold text-[#990000]">
        ATENCAO SOCIO: a fita deve ser devolvida REBOBINADA. Multa de R$ 1,00 por fita nao rebobinada.
      </div>
      <Caixa titulo="Bem vindo a nossa homepage!!!">
        <p className="leading-relaxed">
          Ola visitante! Voce acaba de entrar na pagina oficial da <b>VIDEO LOCADORA GALAXIA</b>, sua locadora de confianca desde 1991. Aqui voce confere nosso{' '}
          <a className="cursor-pointer text-neon underline" onClick={() => ir('catalogo')}>catalogo completo</a>, reserva sua fita pela internet e ainda assina o{' '}
          <a className="cursor-pointer text-neon underline" onClick={() => ir('clube')}>clube de socios</a>.
        </p>
        <p className="leading-relaxed"><span className="pisca font-bold text-red-600">*** NOVIDADE ***</span> Agora voce pode alugar sem sair de casa! Preencha a ficha em <a className="cursor-pointer text-neon underline" onClick={() => ir('alugar')}>ALUGUE AQUI</a> e passe na loja para retirar.</p>
      </Caixa>
      <Arco />
      <Caixa titulo="Lancamentos da semana">
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
          {novos.map((p) => (
            <div key={p.id} className="ridge border-[3px] border-[#aa7700] bg-[#111144] p-2 text-center">
              <div className="flex h-[110px] items-center justify-center border-2 border-black bg-gradient-to-b from-[#222] via-[#555] to-[#222] p-1.5 font-sans text-[13px] font-bold">{p.titulo}</div>
              <p className="leading-relaxed"><Novo /><br /><b>{p.genero}</b> &middot; {p.ano || '-'}<br /><Preco v={p.preco_aluguel} /><br /><Estoque n={p.estoque} /></p>
              <button className="bt" onClick={() => alugarFita(p.id)}>QUERO ESSA!</button>
            </div>
          ))}
        </div>
      </Caixa>
    </>
  )
}

function Catalogo({ dados, alugarFita }) {
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
                <td className="td">{p.genero}</td><td className="td">{p.ano || '-'}</td><td className="td">{Idade(p)}</td>
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

function Alugar({ dados, recarregar, fitaInicial }) {
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
  )
}

function Clube({ dados, recarregar }) {
  const assinar = async (p) => {
    const nome = (prompt('Seu nome completo:') || '').trim(); if (!nome) return
    const fone = (prompt('Seu telefone:') || '').trim(); if (!fone) return
    try {
      let c = await acharOuCriar(nome, fone)
      c = await api('PUT', `/clientes/${c.id}`, { plano_id: p.id })
      await recarregar()
      alert(`OBA! ${c.nome} agora e socio do ${p.nome}.\n\nCarteirinha valida ate ${dataBR(c.plano_vencimento)}.\nA mensalidade de ${dinheiro(p.preco_mensal)} e paga no balcao.`)
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

function Recados({ local, setLocal }) {
  const [r, setR] = useState({ nome: '', cidade: '', txt: '' })
  const assinarLivro = () => {
    if (!r.nome.trim() || !r.txt.trim()) return alert('Escreva pelo menos o nome e o recado!')
    const novo = { ...local, recados: [{ nome: r.nome.trim(), cidade: r.cidade.trim() || 'internet', txt: r.txt.trim() }, ...local.recados] }
    localStorage.setItem('galaxia90', JSON.stringify(novo)); setLocal(novo); setR({ nome: '', cidade: '', txt: '' })
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

const Sobre = ({ dados }) => (
  <Caixa titulo="Quem somos">
    <p className="leading-relaxed">A <b>Video Locadora Galaxia</b> abriu as portas em marco de 1991 com 82 fitas e uma televisao de 14 polegadas no balcao. Hoje somos {dados.produtos.length} titulos no catalogo e {dados.clientes.length} clientes cadastrados.</p>
    <p className="leading-relaxed"><b>Horario:</b> segunda a sabado das 10h as 23h. Domingo das 14h as 22h.<br /><b>Endereco:</b> Rua das Fitas, 42 &mdash; ao lado da padaria.<br /><b>Fone/Fax:</b> (018) 622-1998<br /><b>E-mail:</b> galaxia@provedor.com.br</p>
  </Caixa>
)

/* ---------- app ---------- */
export default function App() {
  const [pag, setPag] = useState('inicio')
  const [fitaSel, setFitaSel] = useState('')
  const [dados, setDados] = useState({ produtos: [], planos: [], alugueis: [], clientes: [] })
  const [erro, setErro] = useState('')
  const [local, setLocal] = useState(lerLocal)

  const carregar = async () => {
    try {
      const [produtos, planos, alugueis, clientes] = await Promise.all([api('GET', '/produtos'), api('GET', '/planos'), api('GET', '/alugueis?status=ativo'), api('GET', '/clientes')])
      setDados({ produtos, planos, alugueis, clientes }); setErro('')
    } catch (e) { setErro(e.message) }
  }
  useEffect(() => { carregar() }, [])

  const ir = (p) => { setPag(p); window.scrollTo(0, 0) }
  const alugarFita = (id) => { setFitaSel(String(id)); ir('alugar') }
  const configApi = () => { const u = prompt('Endereco da API:', getBase()); if (u) { setBase(u); carregar() } }

  return (
    <div className="ridge mx-auto my-3.5 w-[96%] max-w-[820px] border-4 border-ouro bg-black">
      <header className="border-b-[3px] border-double border-ouro bg-azul p-3.5 text-center">
        <div className="font-['Comic_Sans_MS',cursive] text-[40px] font-bold tracking-wide text-[#ffdd00] [text-shadow:2px_2px_0_#ff00aa,4px_4px_0_#00ffff]">Video Locadora Galaxia</div>
        <p className="mt-1.5 text-[15px] text-[#00ff00]">&gt;&gt;&gt; A MAIOR VIDEO LOCADORA DA INTERNET BRASILEIRA &lt;&lt;&lt;</p>
      </header>
      <div className="faixa overflow-hidden border-y-2 border-white bg-red-600 py-1 text-[15px] font-bold text-yellow-300"><span>*** PROMOCAO RELAMPAGO: ALUGUE 2 FITAS E LEVE A 3a POR 1 REAL !!! *** DEVOLVA A FITA REBOBINADA, POR FAVOR !!! *** ABERTO ATE AS 23H TODOS OS DIAS ***</span></div>
      <nav className="border-b-[3px] border-double border-ouro bg-[#333399] p-2 text-center">
        {PAGS.map(([id, nome]) => (
          <a key={id} onClick={() => ir(id)} className={`mx-1.5 inline-block cursor-pointer py-0.5 font-sans text-[13px] font-bold underline hover:bg-rosa hover:text-neon ${pag === id ? 'text-[#00ff00]' : 'text-yellow-300'}`}>[{nome}]</a>
        ))}
      </nav>
      <main className="p-3.5">
        {erro && (
          <div className="mb-3 border-[3px] border-double border-[#990000] bg-[#ffffcc] p-2 font-sans text-xs font-bold text-[#990000]">
            {erro}<br /><br /><button className="bt" onClick={carregar}>TENTAR DE NOVO</button> <button className="bt" onClick={configApi}>MUDAR ENDERECO DA API</button>
          </div>
        )}
        {pag === 'inicio' && <Inicio dados={dados} ir={ir} alugarFita={alugarFita} />}
        {pag === 'catalogo' && <Catalogo dados={dados} alugarFita={alugarFita} />}
        {pag === 'alugar' && <Alugar dados={dados} recarregar={carregar} fitaInicial={fitaSel} />}
        {pag === 'clube' && <Clube dados={dados} recarregar={carregar} />}
        {pag === 'recados' && <Recados local={local} setLocal={setLocal} />}
        {pag === 'sobre' && <Sobre dados={dados} />}
      </main>
      <footer className="border-t-[3px] border-double border-ouro bg-azul p-3 text-center font-sans text-xs text-[#ccc]">
        Voce e o visitante numero <span className="inset border-[3px] border-[#888] bg-black px-2 py-1 font-mono text-[19px] tracking-[4px] text-[#00ff00]">{String(local.visitas).padStart(6, '0')}</span>
        <p>(C) 1998 Video Locadora Galaxia &mdash; Rua das Fitas, 42 &mdash; Fone: (018) 622-1998</p>
        <a className="cursor-pointer text-neon underline" onClick={configApi}>[config da API]</a>
      </footer>
    </div>
  )
}
