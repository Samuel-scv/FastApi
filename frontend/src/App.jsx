import { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import Rodape from './components/Rodape'
import Home from './pages/Home'
import Catalogo from './pages/Catalogo'
import Alugar from './pages/Alugar'
import Clube from './pages/Clube'
import Recados from './pages/Recados'
import Sobre from './pages/Sobre'
import Auth from './pages/Auth'
import { api, eu, getBase, listarTudo, setBase } from './lib/api'
import { lerLocal } from './lib/local'
import { paginaDaUrl } from './lib/paginas'
import { limparSessao, temSessao } from './lib/sessao'

export default function App() {
  const [pag, setPag] = useState(paginaDaUrl)
  const [fitaSel, setFitaSel] = useState('')
  const [dados, setDados] = useState({ produtos: [], planos: [], alugueis: [], clientes: [] })
  const [erro, setErro] = useState('')
  const [local, setLocal] = useState(lerLocal)
  const [usuario, setUsuario] = useState(null)
  const equipe = !!(usuario && (usuario.vendedor || usuario.admin))

  /* catalogo e planos sao publicos; clientes e alugueis exigem vendedor */
  const carregar = async (u = usuario) => {
    const pub = [listarTudo('/produtos'), api('GET', '/planos')]
    const priv = u && (u.vendedor || u.admin) ? [api('GET', '/alugueis?status=ativo'), listarTudo('/clientes')] : [Promise.resolve([]), Promise.resolve([])]
    const [produtos, planos, alugueis, clientes] = await Promise.allSettled([...pub, ...priv])
    const v = (r) => (r.status === 'fulfilled' ? r.value : [])
    setDados({ produtos: v(produtos), planos: v(planos), alugueis: v(alugueis), clientes: v(clientes) })
    const falha = [produtos, planos, alugueis, clientes].find((r) => r.status === 'rejected')
    setErro(falha ? falha.reason.message : '')
  }

  const ir = (p) => {
    setPag(p)
    const url = p === 'inicio' ? '/' : `/${p}`
    if (window.location.pathname !== url) window.history.pushState({ pagina: p }, '', url)
    window.scrollTo(0, 0)
  }
  const alugarFita = (id) => { setFitaSel(String(id)); ir('alugar') }
  const configApi = () => { const u = prompt('Endereco da API:', getBase()); if (u) { setBase(u); carregar() } }

  const aoEntrar = (u) => { setUsuario(u); carregar(u) }
  const aoSair = () => { limparSessao(); setUsuario(null); carregar(null); ir('inicio') }

  useEffect(() => {
    (async () => {
      let u = null
      if (temSessao()) { try { u = await eu() } catch { limparSessao() } }
      setUsuario(u); carregar(u)
    })()
    const expirou = () => { setUsuario(null); carregar(null); setErro('Sessao expirada. Entre novamente.') }
    window.addEventListener('galaxia:sessao-expirou', expirou)
    return () => window.removeEventListener('galaxia:sessao-expirou', expirou)
  }, [])

  useEffect(() => {
    const aoNavegar = () => setPag(paginaDaUrl())
    window.addEventListener('popstate', aoNavegar)
    return () => window.removeEventListener('popstate', aoNavegar)
  }, [])

  return (
    <div className="ridge mx-auto my-3.5 w-[96%] max-w-[820px] border-4 border-ouro bg-black">
      <Navbar pag={pag} ir={ir} usuario={usuario} />
      <main className="p-3.5">
        {erro && (
          <div className="mb-3 border-[3px] border-double border-[#990000] bg-[#ffffcc] p-2 font-sans text-xs font-bold text-[#990000]">
            {erro}<br /><br /><button className="bt" onClick={() => carregar()}>TENTAR DE NOVO</button> <button className="bt" onClick={configApi}>MUDAR ENDERECO DA API</button>
          </div>
        )}
        {pag === 'inicio' && <Home dados={dados} ir={ir} alugarFita={alugarFita} />}
        {pag === 'catalogo' && <Catalogo dados={dados} alugarFita={alugarFita} />}
        {pag === 'alugar' && <Alugar dados={dados} recarregar={carregar} fitaInicial={fitaSel} equipe={equipe} usuario={usuario} ir={ir} />}
        {pag === 'clube' && <Clube dados={dados} recarregar={carregar} equipe={equipe} usuario={usuario} />}
        {pag === 'recados' && <Recados local={local} setLocal={setLocal} />}
        {pag === 'sobre' && <Sobre dados={dados} />}
        {pag === 'entrar' && <Auth usuario={usuario} aoEntrar={aoEntrar} aoSair={aoSair} ir={ir} />}
      </main>
      <Rodape visitas={local.visitas} onConfigApi={configApi} />
    </div>
  )
}
