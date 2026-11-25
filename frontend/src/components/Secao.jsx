export const Secao = ({ titulo, children }) => (
  <section className="mb-6 font-sans text-sm text-[#ddd]">
    <h2 className="mb-2 border-b border-[#555] pb-1 text-base text-white">{titulo}</h2>
    {children}
  </section>
)

export const Aviso = ({ aviso }) =>
  aviso?.texto ? <p className={`my-2 font-sans text-sm ${aviso.erro ? 'text-[#ff8888]' : 'text-[#aaa]'}`}>{aviso.texto}</p> : null
