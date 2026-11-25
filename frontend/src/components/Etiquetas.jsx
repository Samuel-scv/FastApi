import { dinheiro } from '../lib/formatar'

export const Preco = ({ v }) => <span className="font-mono text-[17px] font-bold text-[#00ff00]">{dinheiro(v)}</span>
export const Estoque = ({ n, curto }) =>
  n > 0 ? <span className="font-bold text-verde">{n} {curto ? 'disp.' : 'fita(s) na prateleira'}</span> : <span className="font-bold text-[#ff6666]">{curto ? 'ALUGADA' : 'TODAS ALUGADAS'}</span>
export const Novo = () => <span className="border border-red-600 bg-yellow-300 px-1 font-sans text-[10px] font-bold text-red-600">NOVO!</span>
