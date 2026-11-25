import { useState } from 'react'
import { Caixa } from '../components/Caixa'
import { entrar, registrar } from '../lib/api'

export default function Auth({ usuario, aoEntrar, aoSair, ir }) {
  const [modo, setModo] = useState('login')
  const [f, setF] = useState({ nome: '', email: '', senha: '', tipo: 'cliente', codigo: '' })
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const vendedor = f.tipo === 'vendedor'

  const enviar = async () => {
    if (!f.email.trim() || !f.senha) return alert('Preencha e-mail e senha!')
    try {
      if (modo === 'registro') {
        if (!f.nome.trim()) return alert('Preencha o seu nome!')
        if (f.senha.length < 8) return alert('A senha precisa ter pelo menos 8 caracteres.')
        if (vendedor && !f.codigo.trim()) return alert('Informe o codigo da equipe para criar uma conta de vendedor.')
        await registrar(f.nome.trim(), f.email.trim(), f.senha, f.tipo, vendedor ? f.codigo.trim() : undefined)
      }
      aoEntrar(await entrar(f.email.trim(), f.senha))
      ir('inicio')
    } catch (e) { alert(`NAO FOI POSSIVEL ENTRAR:\n${e.message}`) }
  }

  if (usuario) {
    return (
      <Caixa titulo="Sua conta">
        <p>Logado como <b>{usuario.nome}</b> ({usuario.email}) &mdash; {usuario.admin ? 'ADMIN' : usuario.vendedor ? 'VENDEDOR' : 'CLIENTE'}</p>
        <p className="mt-2.5 text-center"><button className="bt bt-grande" onClick={aoSair}>SAIR</button></p>
      </Caixa>
    )
  }

  return (
    <Caixa titulo={modo === 'login' ? 'Entrar' : 'Criar conta'}>
      {modo === 'login' ? (
        <p>Entre com o seu e-mail e senha. Ainda nao tem conta? Clique em CRIAR CONTA.</p>
      ) : (
        <p>Escolha o tipo de conta. Cliente aluga fitas e acompanha os pedidos. Vendedor atende no balcao e precisa do codigo da equipe.</p>
      )}

      {modo === 'registro' && (
        <>
          <label className="rotulo">TIPO DE CONTA</label>
          <p className="mb-1">
            <label className="mr-4 cursor-pointer">
              <input type="radio" name="tipo" value="cliente" checked={!vendedor} onChange={set('tipo')} /> Cliente
            </label>
            <label className="cursor-pointer">
              <input type="radio" name="tipo" value="vendedor" checked={vendedor} onChange={set('tipo')} /> Vendedor
            </label>
          </p>
          <label className="rotulo">SEU NOME</label>
          <input className="campo" value={f.nome} onChange={set('nome')} />
        </>
      )}

      <label className="rotulo">E-MAIL</label>
      <input className="campo" type="email" value={f.email} onChange={set('email')} />
      <label className="rotulo">SENHA (minimo 8 caracteres)</label>
      <input className="campo" type="password" value={f.senha} onChange={set('senha')} onKeyDown={(e) => e.key === 'Enter' && enviar()} />

      {modo === 'registro' && vendedor && (
        <>
          <label className="rotulo">CODIGO DA EQUIPE</label>
          <input className="campo" type="password" value={f.codigo} onChange={set('codigo')} onKeyDown={(e) => e.key === 'Enter' && enviar()} />
        </>
      )}

      <p className="mt-3.5 text-center">
        <button className="bt bt-grande" onClick={enviar}>{modo === 'login' ? 'ENTRAR' : 'CADASTRAR'} &gt;&gt;&gt;</button>{' '}
        <button className="bt" onClick={() => setModo(modo === 'login' ? 'registro' : 'login')}>{modo === 'login' ? 'CRIAR CONTA' : 'JA TENHO CONTA'}</button>
      </p>
    </Caixa>
  )
}