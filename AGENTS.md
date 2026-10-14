# Regras do repositório

- O backend é FastAPI em `backend/` (porta 8000) e o frontend é React/Vite em `frontend/` (porta 5173); não presumir diretórios `api/` ou `web/`.
- Para desenvolvimento local com containers, usar `compose.yaml` na raiz e os targets `dev` dos respectivos Dockerfiles.
- Manter o SQLite em `/app/data`, montado pelo volume nomeado `api_data`; não gravar dados persistentes na camada da imagem.
- Ler as variáveis da API de `backend/.env`; nunca adicionar `.env` a imagens ou ao controle de versão.
- `VITE_API_URL` é público e incorporado ao bundle durante o build; não colocar segredos em variáveis `VITE_*`.
- Preservar CORS para `http://localhost:5173` e o polling do Vite para compatibilidade com bind mounts em Windows/macOS.
