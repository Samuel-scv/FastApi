export const dinheiro = (v) => 'R$ ' + Number(v).toFixed(2).replace('.', ',')
export const dataBR = (s) => (s ? s.split('-').reverse().join('/') : '-')
export const hojeISO = () => new Date().toLocaleDateString('sv-SE')
export const idade = (p) => (p.classificacao === 'L' ? 'Livre' : `${p.classificacao} anos`)
