import { Caixa } from '../components/Caixa'

export default function Sobre({ dados }) {
  return (
  <Caixa titulo="Quem somos">
    <p className="leading-relaxed">A <b>Video Locadora Galaxia</b> abriu as portas em marco de 1991 com 82 fitas e uma televisao de 14 polegadas no balcao. Hoje somos {dados.produtos.length} titulos no catalogo e {dados.clientes.length} clientes cadastrados.</p>
    <p className="leading-relaxed"><b>Horario:</b> segunda a sabado das 10h as 23h. Domingo das 14h as 22h.<br /><b>Endereco:</b> Rua das Fitas, 42 &mdash; ao lado da padaria.<br /><b>Fone/Fax:</b> (018) 622-1998<br /><b>E-mail:</b> galaxia@provedor.com.br</p>
  </Caixa>
)
}
