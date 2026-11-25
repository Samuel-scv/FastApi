import { useCallback, useEffect, useState } from 'react'
import AvisoEquipe from '../components/AvisoEquipe'
import { Aviso, Secao } from '../components/Secao'
import { api, query } from '../lib/api'
import { dataHora } from '../lib/formatar'

const TIPOS_MOVIMENTO = ['inicial', 'entrada', 'aluguel', 'devolucao', 'venda', 'perda', 'ajuste']
const OPERACOES = {
  entrada: { rotulo: 'Entrada', numero: 'Quantidade', motivoObrigatorio: false, admin: false },
  perda: { rotulo: 'Perda', numero: 'Quantidade', motivoObrigatorio: true, admin: true },
  ajuste: { rotulo: 'Ajuste de inventario', numero: 'Saldo contado', motivoObrigatorio: true, admin: true },
}

export default function Estoque({ equipe, usuario, ir, recarregar }) {
  const [filtro, setFiltro] = useState({ tipo: '', situacao: '' })
  const [resumo, setResumo] = useState(null)
  const [movFiltro, setMovFiltro] = useState({ produto_id: '', tipo: '', pagina: 1 })
  const [mov, setMov] = useState(null)
  const [op, setOp] = useState({ operacao: 'entrada', produto_id: '', numero: '', motivo: '' })
  const [aviso, setAviso] = useState({ texto: '', erro: false })
  const [enviando, setEnviando] = useState(false)

  const falhar = useCallback((e) => {
    setAviso({ texto: e?.message || 'Erro inesperado.', erro: true })
  }, [])

  const carregarResumo = useCallback(async () => {
    try {
      const dados = await api('GET', `/estoque${query(filtro)}`)
      setResumo(dados)
    } catch (e) {
      falhar(e)
    }
  }, [filtro, falhar])

  const carregarMovimentos = useCallback(async () => {
    try {
      const dados = await api('GET', `/estoque/movimentos${query({ ...movFiltro, por_pagina: 20 })}`)
      setMov(dados)
    } catch (e) {
      falhar(e)
    }
  }, [movFiltro, falhar])

  useEffect(() => {
    if (equipe) carregarResumo()
  }, [equipe, carregarResumo])

  useEffect(() => {
    if (equipe) carregarMovimentos()
  }, [equipe, carregarMovimentos])

  if (!equipe) return <AvisoEquipe usuario={usuario} ir={ir} />

  const ehAdmin = Boolean(usuario?.admin)
  const operacoes = Object.entries(OPERACOES).filter(([, o]) => !o.admin || ehAdmin)
  const def = OPERACOES[op.operacao] || OPERACOES.entrada
  const setO = (k) => (e) => setOp((prev) => ({ ...prev, [k]: e.target.value }))

  const registrar = async () => {
    if (enviando) return
    const n = Number(op.numero)
    const minimo = op.operacao === 'ajuste' ? 0 : 1
    if (!op.produto_id) return setAviso({ texto: 'Escolha o titulo.', erro: true })
    if (op.numero === '' || !Number.isInteger(n) || n < minimo) {
      return setAviso({ texto: `${def.numero} deve ser um inteiro maior ou igual a ${minimo}.`, erro: true })
    }
    if (def.motivoObrigatorio && !op.motivo.trim()) {
      return setAviso({ texto: 'Informe o motivo.', erro: true })
    }

    const corpo =
      op.operacao === 'ajuste'
        ? { saldo: n, motivo: op.motivo.trim() }
        : { quantidade: n, motivo: op.motivo.trim() }

    setEnviando(true)
    try {
      const r = await api('POST', `/estoque/${op.produto_id}/${op.operacao}`, corpo)
      setAviso({ texto: `${def.rotulo} registrada. Saldo apos: ${r.saldo_apos}.`, erro: false })
      setOp((prev) => ({ ...prev, numero: '', motivo: '' }))
      await Promise.all([
        carregarResumo(),
        carregarMovimentos(),
        typeof recarregar === 'function' ? recarregar() : Promise.resolve(),
      ])
    } catch (e) {
      falhar(e)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <>
      <Secao titulo="Estoque">
        {resumo && (
          <p className="mb-2">
            {resumo.titulos} titulos, {resumo.copias_disponiveis} copias na prateleira, {resumo.copias_alugadas} alugadas, {resumo.titulos_baixos} com estoque baixo, {resumo.titulos_zerados} zerados.
          </p>
        )}
        <div className="mb-2 flex flex-wrap gap-3">
          <label>
            Tipo{' '}
            <select
              className="s-campo !w-auto"
              value={filtro.tipo}
              onChange={(e) => setFiltro((prev) => ({ ...prev, tipo: e.target.value }))}
            >
              <option value="">todos</option>
              <option value="filme">filme</option>
              <option value="serie">serie</option>
            </select>
          </label>
          <label>
            Situacao{' '}
            <select
              className="s-campo !w-auto"
              value={filtro.situacao}
              onChange={(e) => setFiltro((prev) => ({ ...prev, situacao: e.target.value }))}
            >
              <option value="">todas</option>
              <option value="ok">ok</option>
              <option value="baixo">baixo</option>
              <option value="zerado">zerado</option>
            </select>
          </label>
        </div>
        <div className="overflow-x-auto">
          <table className="s-tabela">
            <thead>
              <tr>
                {['Titulo', 'Tipo', 'Disponivel', 'Alugadas', 'Total', 'Minimo', 'Situacao'].map((h) => (
                  <th key={h} className="s-th">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(resumo?.itens || []).map((i) => (
                <tr key={i.produto_id}>
                  <td className="s-td">{i.titulo}</td>
                  <td className="s-td">{i.tipo}</td>
                  <td className="s-td">{i.disponivel}</td>
                  <td className="s-td">{i.alugadas}</td>
                  <td className="s-td">{i.total_acervo}</td>
                  <td className="s-td">{i.estoque_minimo}</td>
                  <td className="s-td">{i.situacao}{i.todas_alugadas ? ' (todas alugadas)' : ''}</td>
                </tr>
              ))}
              {resumo && resumo.itens.length === 0 && (
                <tr><td className="s-td" colSpan={7}>Nenhum titulo para este filtro.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Secao>

      <Secao titulo="Registrar movimento">
        <div className="grid gap-x-3 sm:grid-cols-2">
          <div>
            <label className="s-rotulo">Operacao</label>
            <select className="s-campo" value={op.operacao} onChange={setO('operacao')}>
              {operacoes.map(([id, o]) => (
                <option key={id} value={id}>{o.rotulo}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="s-rotulo">Titulo</label>
            <select className="s-campo" value={op.produto_id} onChange={setO('produto_id')}>
              <option value="">escolha</option>
              {(resumo?.itens || []).map((i) => (
                <option key={i.produto_id} value={i.produto_id}>{i.titulo}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="s-rotulo">{def.numero}</label>
            <input className="s-campo" type="number" min="0" value={op.numero} onChange={setO('numero')} />
          </div>
          <div>
            <label className="s-rotulo">Motivo{def.motivoObrigatorio ? '' : ' (opcional)'}</label>
            <input className="s-campo" value={op.motivo} onChange={setO('motivo')} />
          </div>
        </div>
        <p className="mt-3">
          <button className="s-bt" disabled={enviando} onClick={registrar}>
            {enviando ? 'Registrando...' : 'Registrar'}
          </button>
        </p>
        {!ehAdmin && <p className="mt-2 text-xs text-[#aaa]">Perda e ajuste de inventario so para administradores.</p>}
        <Aviso aviso={aviso} />
      </Secao>

      <Secao titulo="Historico de movimentos">
        <div className="mb-2 flex flex-wrap gap-3">
          <label>
            Titulo{' '}
            <select
              className="s-campo !w-auto"
              value={movFiltro.produto_id}
              onChange={(e) => setMovFiltro((prev) => ({ ...prev, produto_id: e.target.value, pagina: 1 }))}
            >
              <option value="">todos</option>
              {(resumo?.itens || []).map((i) => (
                <option key={i.produto_id} value={i.produto_id}>{i.titulo}</option>
              ))}
            </select>
          </label>
          <label>
            Tipo{' '}
            <select
              className="s-campo !w-auto"
              value={movFiltro.tipo}
              onChange={(e) => setMovFiltro((prev) => ({ ...prev, tipo: e.target.value, pagina: 1 }))}
            >
              <option value="">todos</option>
              {TIPOS_MOVIMENTO.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="overflow-x-auto">
          <table className="s-tabela">
            <thead>
              <tr>
                {['Data', 'Titulo', 'Tipo', 'Qtd', 'Saldo apos', 'Motivo'].map((h) => (
                  <th key={h} className="s-th">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(mov?.itens || []).map((m) => (
                <tr key={m.id}>
                  <td className="s-td">{dataHora(m.criado_em)}</td>
                  <td className="s-td">{m.titulo}</td>
                  <td className="s-td">{m.tipo}</td>
                  <td className="s-td">{m.quantidade}</td>
                  <td className="s-td">{m.saldo_apos}</td>
                  <td className="s-td">{m.motivo || '-'}</td>
                </tr>
              ))}
              {mov && mov.itens.length === 0 && (
                <tr><td className="s-td" colSpan={6}>Nenhum movimento.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {mov && (
          <p className="mt-2 flex items-center gap-3">
            <button
              className="s-bt"
              disabled={mov.pagina <= 1}
              onClick={() => setMovFiltro((prev) => ({ ...prev, pagina: prev.pagina - 1 }))}
            >
              Anterior
            </button>
            <span>Pagina {mov.pagina} de {mov.paginas} ({mov.total} movimentos)</span>
            <button
              className="s-bt"
              disabled={mov.pagina >= mov.paginas}
              onClick={() => setMovFiltro((prev) => ({ ...prev, pagina: prev.pagina + 1 }))}
            >
              Proxima
            </button>
          </p>
        )}
      </Secao>
    </>
  )
}