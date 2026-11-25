export const Caixa = ({ titulo, children }) => (
  <section className="outset mb-4 border-[3px] border-[#ccc] bg-caixa p-3">
    {titulo && <h2 className="mb-2 border-b-2 border-dotted border-ouro pb-1 font-['Comic_Sans_MS',cursive] text-2xl text-neon">{titulo}</h2>}
    {children}
  </section>
)

export const Arco = () => <hr className="my-3.5 h-[5px] border-0 bg-gradient-to-r from-red-600 via-yellow-300 via-green-400 via-cyan-300 via-blue-600 to-fuchsia-500" />
