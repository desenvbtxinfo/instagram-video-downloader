# Site de download de vídeos do Instagram — GitHub Pages + Render

Este repositório separa a interface estática do serviço Python:
- `frontend/`: página publicada no GitHub Pages.
- `backend/`: API Flask com `yt-dlp`, que precisa ser hospedada em um serviço Python como Render.

Use somente em vídeos que você publicou ou tem autorização para baixar. O projeto não remove marcas-d'água já incorporadas ao arquivo. O Instagram pode bloquear downloads, mudar seus mecanismos ou exigir autenticação.

## 1. Criar o repositório no GitHub
1. Entre em https://github.com/new
2. Crie um repositório público chamado `instagram-video-downloader`.
3. Envie os arquivos desta pasta para o repositório. Você pode usar **Add file → Upload files** no site do GitHub.
4. Para publicar a página, vá a **Settings → Pages**.
5. Em **Build and deployment**, escolha **Deploy from a branch**; selecione `main` e a pasta `/frontend`; salve.

A URL da página será parecida com `https://SEU-USUARIO.github.io/instagram-video-downloader/`.

## 2. Publicar o backend no Render
1. Entre em https://render.com/ e conecte sua conta GitHub.
2. Escolha **New → Blueprint** e selecione o repositório. O Render usará `render.yaml`.
   Se Blueprint não estiver disponível, crie um Web Service apontando para a pasta `backend`, com:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. Após publicar, copie a URL gerada pelo Render, por exemplo `https://instagram-video-backend.onrender.com`.
4. Edite `frontend/index.html` no GitHub e substitua:
   `const API_BASE_URL = "COLOQUE_A_URL_DO_BACKEND_AQUI";`
   pela URL real do Render, sem barra no final.
5. Em `backend` → Environment no Render, defina `FRONTEND_ORIGIN` como a URL real do GitHub Pages, incluindo o caminho de projeto se necessário, por exemplo `https://SEU-USUARIO.github.io`. Salve e faça redeploy. Se usar domínio próprio, use a origem desse domínio.

## Limitações importantes
- GitHub Pages não executa Python; só hospeda a interface.
- A camada gratuita do Render pode suspender o serviço após inatividade e o primeiro acesso pode demorar.
- Antes de abrir ao público, adicione rate limiting, limites de tamanho/duração, autenticação/controles contra abuso e monitore custos. Não exponha cookies ou credenciais do Instagram.
- Downloads podem falhar para conteúdo privado ou restrito. Não publique um serviço que viole direitos autorais ou os termos aplicáveis.
