// Tokens do login (JWT) ficam no localStorage e valem nos proximos acessos.
const ACESSO = 'galaxia90_token'
const REFRESH = 'galaxia90_refresh'

export const lerToken = () => localStorage.getItem(ACESSO)
export const lerRefresh = () => localStorage.getItem(REFRESH)
export const temSessao = () => !!lerToken()

export function salvarSessao(tokens) {
  localStorage.setItem(ACESSO, tokens.access_token)
  if (tokens.refresh_token) localStorage.setItem(REFRESH, tokens.refresh_token)
}

export const salvarAcesso = (token) => localStorage.setItem(ACESSO, token)

export function limparSessao() {
  localStorage.removeItem(ACESSO)
  localStorage.removeItem(REFRESH)
}
