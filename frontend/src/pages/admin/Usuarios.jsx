import { useEffect, useState } from 'react'
import AvisoEquipe from '../../components/AvisoEquipe'
import { Aviso, Secao } from '../../components/Secao'
import { api } from '../../lib/api'

const CAMPOS = [['vendedor', 'Vendedor'], ['admin', 'Admin'], ['ativo', 'Ativo']]

export default function Usuarios({ usuario, ir }) {
  const [lista, setLista] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [aviso, setAviso] = useState({ texto: '', erro: false })
  const admin = !!usuario?.admin

  const carregar = async () => {
    try { setLista(await api('GET', '/usuarios')) } catch (e) { setAviso({ texto: e.message, erro: true }) }
  }
  useEffect(() => { if (admin) carregar() }, [admin])

  if (!admin) return <AvisoEquipe usuario={usuario} ir={ir} admin />

  const alternar = async (u, campo) => {
    setOcupado(true)
    try {
      await api('PATCH', `/usuarios/${u.id}`, { [campo]: !u[campo] })
      setAviso({ texto: `${u.nome}: ${campo} alterado.`, erro: false })
      await carregar()
    } catch (e) { setAviso({ texto: e.message, erro: true }) }
    setOcupado(false)
  }

  return (
    <Secao titulo="Usuarios">
      <p className="mb-2">Quem se cadastra pelo site entra como cliente. Aqui se define vendedor, administrador e se a conta esta ativa.</p>
      <Aviso aviso={aviso} />
      <div className="overflow-x-auto">
        <table className="s-tabela">
          <thead><tr>{['Nome', 'E-mail', ...CAMPOS.map(([, r]) => r)].map((h) => <th key={h} className="s-th">{h}</th>)}</tr></thead>
          <tbody>
            {(lista || []).map((u) => (
              <tr key={u.id}>
                <td className="s-td">{u.nome}{u.id === usuario.id ? ' (voce)' : ''}</td>
                <td className="s-td">{u.email}</td>
                {CAMPOS.map(([campo]) => (
                  <td key={campo} className="s-td">
                    {u[campo] ? 'sim' : 'nao'}{' '}
                    <button className="s-bt !px-2 !py-0" disabled={ocupado} onClick={() => alternar(u, campo)}>alterar</button>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Secao>
  )
}
