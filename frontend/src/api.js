import axios from 'axios'

const http = axios.create({
  baseURL: localStorage.getItem('galaxia90_api') || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
})

export const getBase = () => http.defaults.baseURL
export const setBase = (url) => {
  const base = url.trim().replace(/\/+$/, '')
  http.defaults.baseURL = base
  localStorage.setItem('galaxia90_api', base)
}

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
    if (e.response) throw new Error(msg(e.response.data)) // a API respondeu com erro (404, 409, 422...)
    throw new Error(`Servidor fora do ar! Confira se a API esta rodando em ${getBase()}`)
  }
}

/* acha o cliente por nome + telefone; se nao existir, cadastra */
export async function acharOuCriar(nome, fone, cidade = '') {
  const tel = fone.replace(/\D/g, '')
  const lista = await api('GET', '/clientes')
  return (
    lista.find((c) => c.telefone.replace(/\D/g, '') === tel && c.nome.toLowerCase() === nome.toLowerCase()) ||
    api('POST', '/clientes', { nome, telefone: fone, endereco: cidade })
  )
}
