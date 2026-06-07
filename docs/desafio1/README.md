# 🏗️ Desafio 1 — CI/CD da Landing Page (CondoCombat)

## 🎯 Objetivo

Criar uma pipeline de **Integração Contínua (CI)** e **Deploy Contínuo (CD)** para a **Landing Page** do CondoCombat, um site estático construído com [Astro](https://astro.build) + [TailwindCSS](https://tailwindcss.com).

A pipeline deve:

1. **Executar testes automatizados** (`vitest`)
2. **Fazer o build do projeto** (`astro build`)
3. **Fazer o deploy na Netlify** utilizando a **API oficial** da Netlify (ou CLI com token)

O aluno pode escolher entre **GitHub Actions** ou **GitLab CI/CD** — ou fazer ambos.

---

## 📦 Sobre o Projeto

### Landing Page (`landing/`)

| Item            | Detalhe                        |
|-----------------|--------------------------------|
| Framework       | Astro 5 + TailwindCSS 3        |
| Pasta de build  | `dist/`                        |
| Testes          | Vitest                         |
| Comando build   | `npm run build` → `astro build`|
| Comando teste   | `npm test` → `vitest run`      |
| Porta dev       | `localhost:4321`               |

```bash
# Instalar dependências
npm install

# Rodar testes
npm test

# Build local
npm run build

# Preview do build
npm run preview
```

---

## 📋 Pré-requisitos

- [ ] Conta na [Netlify](https://app.netlify.com/signup)
- [ ] Repositório no [GitHub](https://github.com) ou [GitLab](https://gitlab.com)
- [ ] Netlify CLI instalada (opcional, para testes locais):

```bash
npm install -g netlify-cli
```

---

## 🔐 Variáveis de Ambiente ( Secrets )

A pipeline precisa de duas variáveis de ambiente para fazer o deploy. Configure-as como **secrets** no repositório:

| Variável              | Descrição                                      | Onde conseguir                                  |
|-----------------------|------------------------------------------------|-------------------------------------------------|
| `NETLIFY_AUTH_TOKEN`  | Token de autenticação para a API da Netlify    | Netlify → User Settings → Personal access tokens |
| `NETLIFY_SITE_ID`     | ID do site criado na Netlify                   | Netlify → Site settings → General → Site ID      |
| `NETLIFY_SITE_NAME`   | Nome do site (slug) — usado no deploy via CLI  | Netlify → Site settings → General → Site name    |

### Como gerar o `NETLIFY_AUTH_TOKEN`

1. Acesse [app.netlify.com](https://app.netlify.com)
2. Vá em **User Settings** (foto do canto superior direito) → **Applications**
3. Em **Personal access tokens**, clique em **New access token**
4. Dê um nome (ex: `ci-cd-condocombat`) e copie o token gerado
5. Adicione como secret no repositório com o nome `NETLIFY_AUTH_TOKEN`

### Como obter o `NETLIFY_SITE_ID`

1. No Netlify, vá em **Sites** → selecione o site criado
2. Vá em **Site settings** → **General** → **Site details**
3. Copie o **Site ID** (é um UUID, ex: `12345678-9abc-def0-1234-56789abcdef0`)
4. Adicione como secret no repositório com o nome `NETLIFY_SITE_ID`

> 💡 **Dica**: Você pode criar o site manualmente pelo dashboard da Netlify ou via CLI com `netlify sites:create`.

---

## 🌐 Configuração `netlify.toml`

Crie o arquivo `netlify.toml` na raiz da landing page (`landing/netlify.toml`):

```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

> ℹ️ Este arquivo informa à Netlify qual comando executar e qual pasta publicar. Não é estritamente necessário para o deploy via API (a pipeline pode passar esses parâmetros), mas ajuda na consistência.

---

## 🚀 Deploy via API da Netlify (dentro da pipeline)

A pipeline usará a **API REST oficial da Netlify** para fazer o upload dos arquivos do build. O fluxo é:

1. Build do projeto → `dist/`
2. Criar um **deploy** via API → obtém um `deploy_id`
3. Fazer upload de cada arquivo do diretório `dist/` para o deploy
4. Finalizar o deploy informando que ele está pronto para produção

### Endpoints utilizados

| Passo | Método | Endpoint                                                    |
|-------|--------|-------------------------------------------------------------|
| 1     | `POST` | `https://api.netlify.com/api/v1/sites/{site_id}/deploys`    |
| 2     | `PUT`  | `https://api.netlify.com/api/v1/deploys/{deploy_id}/files/{path}` |
| 3     | `POST` | `https://api.netlify.com/api/v1/deploys/{deploy_id}/lock`   |

### Passo a passo manual (para entender)

```bash
# 1. Criar o deploy (informa os hashes dos arquivos)
#    Primeiro gere os SHA1 de cada arquivo e monte o JSON.

# 2. Upload de cada arquivo
curl -X PUT "https://api.netlify.com/api/v1/deploys/DEPLOY_ID/files/index.html" \
  -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @./dist/index.html

# 3. Finalizar como produção (opcional — pode usar --prod na CLI)
```

> ⚠️ **Importante**: A implementação real na pipeline pode usar a **Netlify CLI** (que encapsula toda essa lógica) ou chamar a API diretamente com `curl`. Ambas as abordagens são válidas. A CLI é mais simples; a API direta demonstra maior domínio técnico.

---

## 🤖 Pipeline com Netlify CLI (abordagem simplificada)

A maneira mais direta é usar a `netlify-cli` dentro da pipeline:

```bash
npm install -g netlify-cli
netlify deploy --dir=dist --prod --auth=$NETLIFY_AUTH_TOKEN --site=$NETLIFY_SITE_ID
```

| Flag      | Significado                                        |
|-----------|----------------------------------------------------|
| `--dir`   | Diretório com os arquivos do build (`dist`)        |
| `--prod`  | Deploy direto para produção (sem draft)            |
| `--auth`  | Token de autenticação                              |
| `--site`  | ID do site na Netlify                              |

---

## 🐙 GitHub Actions

Crie o diretório `.github/workflows/` na **raiz do repositório** (não dentro de `landing/`) e adicione o arquivo:

### `deploy-landing.yml`

```yaml
name: Deploy Landing Page

on:
  push:
    branches: [main, master]
    paths:
      - 'landing/**'
      - '.github/workflows/deploy-landing.yml'
  workflow_dispatch:

env:
  NODE_VERSION: '20'

jobs:
  ci:
    name: CI — Test & Build
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./landing

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: ./landing/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: landing-dist
          path: landing/dist/

  cd:
    name: CD — Deploy to Netlify
    needs: ci
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: landing-dist
          path: landing/dist/

      - name: Install Netlify CLI
        run: npm install -g netlify-cli

      - name: Deploy to Netlify
        run: |
          netlify deploy \
            --dir=landing/dist \
            --prod \
            --auth=${{ secrets.NETLIFY_AUTH_TOKEN }} \
            --site=${{ secrets.NETLIFY_SITE_ID }}
```

### Explicação

| Job   | Responsabilidade                                           |
|-------|------------------------------------------------------------|
| `ci`  | Instalar deps → rodar testes → build → salvar artefato     |
| `cd`  | Baixar artefato do build → instalar CLI → deploy na Netlify |

O job `cd` só executa se o `ci` passar (`needs: ci`).

### Gatilhos (`on.push.paths`)

A pipeline é acionada apenas quando há mudanças em:

- `landing/**` — qualquer arquivo da landing page
- `.github/workflows/deploy-landing.yml` — o próprio workflow

Isso evita rodar a pipeline quando outras partes do monorepo (backend, frontend) são alteradas.

---

## 🦊 GitLab CI/CD

Crie o arquivo `.gitlab-ci.yml` na **raiz do repositório**:

### `.gitlab-ci.yml`

```yaml
image: node:20

variables:
  NODE_VERSION: "20"

cache:
  key:
    files:
      - landing/package-lock.json
  paths:
    - landing/node_modules/

stages:
  - test
  - build
  - deploy

test-landing:
  stage: test
  script:
    - cd landing
    - npm ci
    - npm test
  artifacts:
    expire_in: 1 hour
    paths:
      - landing/node_modules/

build-landing:
  stage: build
  script:
    - cd landing
    - npm ci
    - npm run build
  artifacts:
    expire_in: 1 hour
    paths:
      - landing/dist/
  needs:
    - test-landing

deploy-landing:
  stage: deploy
  image: node:20
  script:
    - npm install -g netlify-cli
    - netlify deploy --dir=landing/dist --prod --auth=$NETLIFY_AUTH_TOKEN --site=$NETLIFY_SITE_ID
  needs:
    - build-landing
  only:
    - main
    - master
  environment:
    name: production
    url: https://$NETLIFY_SITE_NAME.netlify.app
```

### Explicação dos stages

| Stage     | Descrição                                     |
|-----------|-----------------------------------------------|
| `test`    | Instala deps e executa os testes do Vitest    |
| `build`   | Faz o build com `astro build` → gera `dist/`  |
| `deploy`  | Instala Netlify CLI e faz deploy para produção |

O `needs` garante a ordem: test → build → deploy.

### Configuração de Environment no GitLab

Para adicionar variáveis no GitLab:

1. Vá em **Settings** → **CI/CD** → **Variables**
2. Adicione:
   - `NETLIFY_AUTH_TOKEN` — marcada como **Masked**
   - `NETLIFY_SITE_ID` — marcada como **Masked**
   - `NETLIFY_SITE_NAME` — nome do seu site (ex: `condocombat-landing`)

> 💡 **Dica**: Use o `environment.url` com `https://$NETLIFY_SITE_NAME.netlify.app` para que o GitLab mostre um link direto para o site nos pipelines.

---

## 📐 Abordagem alternativa: deploy com `curl` (API direta)

Para quem quiser demonstrar domínio da API REST da Netlify (ao invés de usar a CLI), aqui está um job que faz o deploy chamando a API diretamente:

### GitHub Actions (job CD alternativo)

```yaml
  cd-api:
    name: CD — Deploy via Netlify API
    needs: ci
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: landing-dist
          path: landing/dist/

      - name: Deploy to Netlify via API
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        run: |
          cd landing/dist

          # 1. Gerar SHA1 de cada arquivo e montar o JSON de files
          FILES_JSON="{"
          FIRST=true
          find . -type f | while read -r file; do
            [ "$FIRST" = true ] && FIRST=false || FILES_JSON+=","
            path="${file#./}"
            hash=$(sha1sum "$file" | awk '{print $1}')
            FILES_JSON+="\"$path\":\"$hash\""
          done
          FILES_JSON+="}"

          # 2. Criar o deploy
          echo "Criando deploy..."
          DEPLOY_RESPONSE=$(curl -s -X POST \
            "https://api.netlify.com/api/v1/sites/$NETLIFY_SITE_ID/deploys" \
            -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"files\":$FILES_JSON}")

          DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
          echo "Deploy ID: $DEPLOY_ID"

          # 3. Upload de cada arquivo
          echo "Fazendo upload dos arquivos..."
          find . -type f | while read -r file; do
            path="${file#./}"
            echo "  Uploading: $path"
            curl -s -X PUT \
              "https://api.netlify.com/api/v1/deploys/$DEPLOY_ID/files/$path" \
              -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
              -H "Content-Type: application/octet-stream" \
              --data-binary "@$file" > /dev/null
          done

          echo "✅ Deploy concluído com sucesso!"
          echo "Deploy ID: $DEPLOY_ID"
```

### GitLab CI (job deploy alternativo)

```yaml
deploy-landing-api:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - cd landing/dist

    # 1. Gerar JSON de files com SHA1
    - |
      FILES_JSON="{"
      FIRST=true
      find . -type f | while read -r file; do
        [ "$FIRST" = true ] && FIRST=false || FILES_JSON+=","
        path="${file#./}"
        hash=$(sha1sum "$file" | awk '{print $1}')
        FILES_JSON+="\"$path\":\"$hash\""
      done
      FILES_JSON+="}"

    # 2. Criar deploy
    - |
      DEPLOY_RESPONSE=$(curl -s -X POST \
        "https://api.netlify.com/api/v1/sites/$NETLIFY_SITE_ID/deploys" \
        -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$FILES_JSON")
      DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
      echo "Deploy ID: $DEPLOY_ID"

    # 3. Upload de cada arquivo
    - |
      find . -type f | while read -r file; do
        path="${file#./}"
        echo "Uploading: $path"
        curl -s -X PUT \
          "https://api.netlify.com/api/v1/deploys/$DEPLOY_ID/files/$path" \
          -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
          -H "Content-Type: application/octet-stream" \
          --data-binary "@$file" > /dev/null
      done

    - echo "✅ Deploy realizado com sucesso! Deploy ID: $DEPLOY_ID"
  needs:
    - build-landing
  only:
    - main
    - master
  variables:
    NETLIFY_AUTH_TOKEN: $NETLIFY_AUTH_TOKEN
    NETLIFY_SITE_ID: $NETLIFY_SITE_ID
```

> ⚠️ A abordagem com `curl` é mais complexa, mas demonstra entendimento do fluxo real da API. Em produção, a CLI é recomendada por ser mais robusta e tratar edge cases.

---

## 🧪 Validação local antes de subir

Antes de commitar, teste tudo localmente:

```bash
# 1. Testes
cd landing && npm test

# 2. Build
npm run build

# 3. Testar deploy (draft) localmente com a CLI
netlify deploy --dir=dist --auth=$NETLIFY_AUTH_TOKEN --site=$NETLIFY_SITE_ID

# 4. Se o draft estiver OK, faça o deploy para produção
netlify deploy --dir=dist --prod --auth=$NETLIFY_AUTH_TOKEN --site=$NETLIFY_SITE_ID
```

---

## ✅ Critérios de Avaliação

| Critério                           | Peso | Descrição                                          |
|------------------------------------|------|----------------------------------------------------|
| Testes passando na pipeline        | 25%  | `vitest run` executa sem erros                     |
| Build concluído com sucesso        | 20%  | `astro build` gera a pasta `dist/`                 |
| Deploy publicado na Netlify        | 30%  | Site acessível via URL pública                     |
| Pipeline automatizada (CI/CD)      | 15%  | Pipeline roda sozinha no push para `main`          |
| Organização e clareza do código    | 10%  | YAML limpo, boas práticas, secrets bem configurados|

---

## 📚 Referências

- [Netlify CLI — Comando deploy](https://github.com/netlify/cli/blob/main/docs/commands/deploy.md)
- [Netlify API — Deploy endpoint](https://docs.netlify.com/api/get-started/#deploys)
- [GitHub Actions — Documentação](https://docs.github.com/en/actions)
- [GitLab CI/CD — Documentação](https://docs.gitlab.com/ee/ci/)
- [Astro — Guia de deploy na Netlify](https://docs.astro.build/en/guides/deploy/netlify/)
- [CondoCombat — Landing Page](../landing/)

---

## 💡 Dicas

1. **Monorepo**: O projeto CondoCombat é um monorepo com `landing/`, `frontend/` e `backend/`. A pipeline deve focar **apenas** na landing page. Use `paths` (GitHub) ou `only:changes` (GitLab) para evitar execuções desnecessárias.
2. **Netlify CLI**: Instale como dependência de desenvolvimento (`npm install -D netlify-cli`) para ter versão fixa no `package.json`.
3. **URL do site**: Após o deploy, o site estará disponível em `https://{site-name}.netlify.app`. Você pode configurar domínio personalizado depois.
4. **Teste em draft primeiro**: Faça o primeiro deploy sem `--prod` para verificar se está tudo certo antes de publicar.
5. **Logs**: Se o deploy falhar, verifique os logs da pipeline e da Netlify (Netlify → Deploys → clicar no deploy com problema).
