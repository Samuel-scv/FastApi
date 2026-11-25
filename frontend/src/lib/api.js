import axios from 'axios'
import { lerRefresh, lerToken, limparSessao, salvarAcesso, salvarSessao, temSessao } from './sessao'

const http = axios.create({
  baseURL: localStorage.getItem('galaxia90_api') || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
})

export const getBase = () => http.defaults.baseURL
export const setBase = (url) => {
  const base = url.trim().replace(/\/+$/, '')
  http.defaults.baseURL = base
  localStorage.setItem('galaxia90_api', base)
}

http.interceptors.request.use((cfg) => {
  const t = lerToken()
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

/* 401 em rota protegida: tenta renovar o access token uma vez com o refresh token */
let renovando = null
http.interceptors.response.use(
  (r) => r,
  async (e) => {
    const cfg = e.config
    const refresh = lerRefresh()
    const ehAuth = cfg?.url?.startsWith('/auth/')
    if (e.response?.status === 401 && cfg && !cfg._tentou && !ehAuth && refresh) {
      cfg._tentou = true
      try {
        renovando ||= http.post('/auth/refresh', { refresh_token: refresh }).finally(() => { renovando = null })
        const r = await renovando
        salvarAcesso(r.data.access_token)
        cfg.headers.Authorization = `Bearer ${r.data.access_token}`
        return http.request(cfg)
      } catch { /* refresh vencido: cai para o logout abaixo */ }
    }
    if (e.response?.status === 401 && !ehAuth && temSessao()) {
      limparSessao()
      window.dispatchEvent(new Event('galaxia:sessao-expirou'))
    }
    return Promise.reject(e)
  },
)

const msg = (d) =>
  typeof d?.detail === 'string'
    ? d.detail
    : Array.isArray(d?.detail)
      ? d.detail.map((x) => `${(x.loc || []).slice(1).join('.')}: ${x.msg}`).join('\n')
      : 'Erro inesperado na API.'

export async function api(metodo, caminho, corpo) {
  try {
    const r = await http.request({ method: metodo, url: caminho, data: corpo })
    return r.status === 204 ? null : r.data
  } catch (e) {
    if (e.response) throw new Error(msg(e.response.data)) // a API respondeu com erro (401, 403, 404, 409, 422...)
    throw new Error(`Servidor fora do ar! Confira se a API esta rodando em ${getBase()}`)
  }
}

export async function entrar(email, senha) {
  salvarSessao(await api('POST', '/auth/login', { email, senha }))
  return api('GET', '/auth/me')
}

export const registrar = (nome, email, senha) => api('POST', '/auth/registrar', { nome, email, senha })
export const eu = () => api('GET', '/auth/me')

/* as listagens paginadas devolvem {itens, total, pagina, por_pagina, paginas}; junta todas as paginas */
export async function listarTudo(caminho, params = {}) {
  const itens = []
  let pagina = 1
  for (;;) {
    const qs = new URLSearchParams({ ...params, pagina, por_pagina: 100 }).toString()
    const r = await api('GET', `${caminho}?${qs}`)
    itens.push(...r.itens)
    if (pagina >= r.paginas) return itens
    pagina += 1
  }
}

/* acha o cliente por nome + telefone; se nao existir, cadastra (rotas de vendedor) */
export async function acharOuCriar(nome, fone, cidade = '') {
  const tel = fone.replace(/\D/g, '')
  const lista = await listarTudo('/clientes', { q: nome })
  return (
    lista.find((c) => (c.telefone || '').replace(/\D/g, '') === tel && c.nome.toLowerCase() === nome.toLowerCase()) ||
    api('POST', '/clientes', { nome, telefone: fone, endereco: cidade })
  )
}

/* monta ?a=1&b=2 ignorando valores vazios */
export function query(params) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => { if (v !== '' && v != null) q.set(k, v) })
  const txt = q.toString()
  return txt ? `?${txt}` : ''
}
