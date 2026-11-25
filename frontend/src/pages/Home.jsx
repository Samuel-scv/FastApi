import { Caixa, Arco } from '../components/Caixa'
import FitaCard from '../components/FitaCard'

export default function Home({ dados, ir, alugarFita }) {
  const novos = [...dados.produtos].sort((a, b) => (b.ano || 0) - (a.ano || 0)).slice(0, 3)
  return (
    <>
      <div className="mb-3 border-[3px] border-double border-[#990000] bg-[#ffffcc] p-2 font-sans text-xs font-bold text-[#990000]">
        ATENCAO SOCIO: a fita deve ser devolvida REBOBINADA. Multa de R$ 1,00 por fita nao rebobinada.
      </div>
      <Caixa titulo="Bem vindo a nossa homepage!!!">
        <p className="leading-relaxed">
          Ola visitante! Voce acaba de entrar na pagina oficial da <b>VIDEO LOCADORA GALAXIA</b>, sua locadora de confianca desde 1991. Aqui voce confere nosso{' '}
          <a className="cursor-pointer text-neon underline" onClick={() => ir('catalogo')}>catalogo completo</a>, reserva sua fita pela internet e ainda assina o{' '}
          <a className="cursor-pointer text-neon underline" onClick={() => ir('clube')}>clube de socios</a>.
        </p>
        <p className="leading-relaxed"><span className="pisca font-bold text-red-600">*** NOVIDADE ***</span> Agora voce pode alugar sem sair de casa! Preencha a ficha em <a className="cursor-pointer text-neon underline" onClick={() => ir('alugar')}>ALUGUE AQUI</a> e passe na loja para retirar.</p>
      </Caixa>
      <Arco />
      <Caixa titulo="Lancamentos da semana">
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
          {novos.map((p) => (
            <FitaCard key={p.id} p={p} onAlugar={alugarFita} />
          ))}
        </div>
      </Caixa>
    </>
  )
}
