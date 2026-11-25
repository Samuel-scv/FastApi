import { Caixa } from './Caixa'

export default function AvisoEquipe({ usuario, ir }) {
  return (
    <Caixa titulo="Area da equipe">
      <p className="leading-relaxed">
        {usuario
          ? 'Sua conta e de cliente. Registrar aluguel e assinatura e feito no balcao por um vendedor.'
          : 'O balcao e so para a equipe da loja. Entre com a sua conta de vendedor para continuar.'}
      </p>
      {!usuario && <p className="mt-2.5 text-center"><button className="bt bt-grande" onClick={() => ir('entrar')}>ENTRAR &gt;&gt;&gt;</button></p>}
    </Caixa>
  )
}
