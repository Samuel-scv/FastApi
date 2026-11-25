export default function Rodape({ visitas, onConfigApi }) {
  return (
    <footer className="border-t-[3px] border-double border-ouro bg-azul p-3 text-center font-sans text-xs text-[#ccc]">
      Voce e o visitante numero <span className="inset border-[3px] border-[#888] bg-black px-2 py-1 font-mono text-[19px] tracking-[4px] text-[#00ff00]">{String(visitas).padStart(6, '0')}</span>
      <p>(C) 1998 Video Locadora Galaxia &mdash; Rua das Fitas, 42 &mdash; Fone: (018) 622-1998</p>
      <a className="cursor-pointer text-neon underline" onClick={onConfigApi}>[config da API]</a>
    </footer>
  )
}
