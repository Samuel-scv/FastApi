const RECADOS = [
  { nome: 'Ricardinho', cidade: 'Aracatuba-SP', txt: 'Melhor locadora do bairro!! alugo aqui desde 96. abracos pro seu Jorge do balcao' },
  { nome: 'Fabi_Girl', cidade: 'Birigui', txt: 'adorei a homepage de voces!!! poe mais filme de romance por favor :):):)' },
  { nome: 'MASTER_DO_VHS', cidade: 'internet', txt: 'quem quiser trocar link comigo manda email. tenho pagina de dinossauros' },
]

const CHAVE = 'galaxia90'

/* livro de visitas e contador de visitantes ficam so no navegador */
export function lerLocal() {
  let l = {}
  try { l = JSON.parse(localStorage.getItem(CHAVE)) || {} } catch { /* ignora */ }
  l.recados ||= RECADOS
  l.visitas = (l.visitas || 104872) + 1
  localStorage.setItem(CHAVE, JSON.stringify(l))
  return l
}

export const salvarLocal = (l) => localStorage.setItem(CHAVE, JSON.stringify(l))
