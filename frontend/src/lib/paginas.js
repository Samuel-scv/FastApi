/* [id, rotulo, acesso] acesso: 'todos' | 'equipe' (vendedor ou admin) | 'admin' */
export const PAGS = [
  ['inicio', 'HOME', 'todos'],
  ['catalogo', 'CATALOGO', 'todos'],
  ['perguntas', 'PERGUNTAS', 'todos'],
  ['alugar', 'ALUGUE AQUI', 'todos'],
  ['clube', 'CLUBE DE SOCIOS', 'todos'],
  ['recados', 'LIVRO DE VISITAS', 'todos'],
  ['sobre', 'QUEM SOMOS', 'todos'],
  ['estoque', 'ESTOQUE', 'equipe'],
  ['perguntas-vendedor', 'CAIXA DE PERGUNTAS', 'equipe'],
  ['usuarios', 'USUARIOS', 'admin'],
  ['entrar', 'ENTRAR', 'todos'],
]

export const ehEquipe = (usuario) =>
  !!(
    usuario &&
    (usuario.vendedor ||
      usuario.admin ||
      usuario.tipo === 'vendedor' ||
      usuario.role === 'vendedor')
  )

export const podeVer = (acesso, usuario) =>
  acesso === 'todos' ||
  (acesso === 'equipe' && ehEquipe(usuario)) ||
  (acesso === 'admin' && !!usuario?.admin)

export const paginaDaUrl = () => {
  const caminho = window.location.pathname.replace(/^\/+|\/+$/g, '')
  return PAGS.some(([id]) => id === caminho) ? caminho : 'inicio'
}