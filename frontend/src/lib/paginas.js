export const PAGS = [['inicio', 'HOME'], ['catalogo', 'CATALOGO'], ['alugar', 'ALUGUE AQUI'], ['clube', 'CLUBE DE SOCIOS'], ['recados', 'LIVRO DE VISITAS'], ['sobre', 'QUEM SOMOS'], ['entrar', 'ENTRAR']]

export const paginaDaUrl = () => {
  const caminho = window.location.pathname.replace(/^\/+|\/+$/g, '')
  return PAGS.some(([id]) => id === caminho) ? caminho : 'inicio'
}
