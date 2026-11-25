import { PAGS } from '../lib/paginas'

export default function Navbar({ pag, ir, usuario }) {
  return (
    <>
      <header className="border-b-[3px] border-double border-ouro bg-azul p-3.5 text-center">
        <div className="font-['Comic_Sans_MS',cursive] text-[40px] font-bold tracking-wide text-[#ffdd00] [text-shadow:2px_2px_0_#ff00aa,4px_4px_0_#00ffff]">Video Locadora Galaxia</div>
        <p className="mt-1.5 text-[15px] text-[#00ff00]">&gt;&gt;&gt; A MAIOR VIDEO LOCADORA DA INTERNET BRASILEIRA &lt;&lt;&lt;</p>
      </header>
      <div className="faixa overflow-hidden border-y-2 border-white bg-red-600 py-1 text-[15px] font-bold text-yellow-300"><span>*** PROMOCAO RELAMPAGO: ALUGUE 2 FITAS E LEVE A 3a POR 1 REAL !!! *** DEVOLVA A FITA REBOBINADA, POR FAVOR !!! *** ABERTO ATE AS 23H TODOS OS DIAS ***</span></div>
      <nav className="border-b-[3px] border-double border-ouro bg-[#333399] p-2 text-center">
        {PAGS.map(([id, nome]) => (
          <a key={id} onClick={() => ir(id)} className={`mx-1.5 inline-block cursor-pointer py-0.5 font-sans text-[13px] font-bold underline hover:bg-rosa hover:text-neon ${pag === id ? 'text-[#00ff00]' : 'text-yellow-300'}`}>[{id === 'entrar' && usuario ? `CONTA: ${usuario.nome.split(' ')[0].toUpperCase()}` : nome}]</a>
        ))}
      </nav>
    </>
  )
}
