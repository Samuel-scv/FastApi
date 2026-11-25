import { Secao } from './Secao'

export default function AvisoEquipe({ usuario, ir, admin = false }) {
  const texto = usuario
    ? admin ? 'Sua conta nao e de administrador.' : 'Sua conta e de cliente. Esta area e restrita a equipe da loja.'
    : admin ? 'Area restrita a administradores. Entre com uma conta de administrador.' : 'Area restrita a equipe da loja. Entre com uma conta de vendedor.'
  return (
    <Secao titulo="Acesso restrito">
      <p>{texto}</p>
      {!usuario && <p className="mt-3"><button className="s-bt" onClick={() => ir('entrar')}>Entrar</button></p>}
    </Secao>
  )
}
