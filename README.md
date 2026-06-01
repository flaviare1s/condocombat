# 🏢 CondoCombat

**ERP satírico para gerenciar fofocas, rixas e tretas de condomínio.**

Transforme o caos do seu prédio em dados acionáveis. Ocorrências em tempo real, ranking de rivalidades entre apartamentos, e um dashboard que todo síndico merece — mas nenhum está preparado.

```
🏗️  Landing (Astro) → 🖥️  App (Next.js) → ⚙️  API (FastAPI)
```

---

> ⚠️ **Aviso**: Esta aplicação é **exclusivamente para fins pedagógicos e didáticos**. É uma brincadeira, um exercício de desenvolvimento de software. Não deve ser levada a sério nem utilizada em condomínios reais. **Não incentivamos brigas, fofocas ou rivalidades entre vizinhos** — a sátira é apenas uma ferramenta criativa para tornar o aprendizado mais divertido. Respeito e boa convivência sempre em primeiro lugar. 🏡❤️

---

## ✨ Features

- 📝 **Ocorrências** — Registre barulho, festa, vazamento, fofoca, briga, animal solto
- ⚔️ **Rivalidades** — Rastreie conflitos entre apartamentos (níveis: leve → moderado → intenso → bélico)
- 📡 **Feed ao vivo** — WebSocket broadcast de ocorrências em tempo real
- 📊 **Rankings** — Top rivalidades, apartamentos mais problemáticos
- 🔐 **Autenticação JWT** — Morador, síndico, ou anônimo (sim, anônimo pode fofocar)
- 😈 **Tom satírico** — Design profissional, conteúdo picante

## 🧱 Stack

| Camada | Tecnologia | Testes |
|--------|-----------|-------|
| Landing Page | [Astro](https://astro.build) + TailwindCSS | 39 |
| Frontend App | [Next.js](https://nextjs.org) App Router + shadcn/ui + TailwindCSS | 79 |
| Backend API | [FastAPI](https://fastapi.tiangolo.com) + SQLAlchemy Async + Pydantic v2 + WebSockets | 216 |
| **Total** | | **334** |

## 🚀 Começando

### Pré-requisitos

- Python 3.12+
- Node.js 20+
- `uv` (gerenciador de projetos Python)

### Backend

```bash
cd backend
uv sync
cp .env.example .env   # Preencha SECRET_KEY (veja abaixo)
uv run uvicorn app.main:app --reload
```

> **SECRET_KEY**: Gere uma com `python -c 'import secrets; print(secrets.token_urlsafe(32))'`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Landing Page

```bash
cd landing
npm install
npm run dev
```

### Seed Data (dados satíricos)

```bash
cd backend
uv run python -m scripts.seed
```

Cria 3 condomínios, 16 apartamentos, 13 moradores, 12 ocorrências e 5 rivalidades.

## 🧪 Testes

```bash
# Backend (216 testes)
cd backend && uv run pytest -q

# Frontend (79 testes)
cd frontend && npm run test

# Landing (39 testes)
cd landing && npm run test
```

## 📂 Estrutura

```
condocombat/
├── landing/                     # Astro — página pública
│   └── src/
│       ├── components/
│       └── layouts/
├── frontend/                    # Next.js — app logado
│   └── src/app/(app)/
│       ├── ocorrencias/
│       ├── rivalidades/
│       └── dashboard/
├── backend/                     # FastAPI — API REST + WS
│   ├── app/
│   │   ├── routers/             # Endpoints HTTP
│   │   ├── services/            # Regras de negócio
│   │   ├── repositories/        # Acesso a dados
│   │   ├── models/              # ORM (SQLAlchemy)
│   │   ├── schemas/             # Pydantic v2
│   │   └── config/              # Settings
│   └── scripts/                 # Seed data
└── .opencode/                   # Config OpenAgents
```

## 🔌 API

### REST

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/condominios` | Lista condomínios |
| `POST` | `/condominios` | Cria condomínio |
| `GET` | `/ocorrencias` | Lista ocorrências |
| `GET` | `/ocorrencias/recentes` | Últimas 20 |
| `POST` | `/ocorrencias` | Cria ocorrência |
| `GET` | `/rivalidades` | Lista rivalidades |
| `GET` | `/rivalidades/top` | Top 10 por nível |
| `POST` | `/rivalidades/{id}/escalar` | Escala nível |
| `POST` | `/auth/login` | Login JWT |

### WebSocket

```
ws://host/ws/ocorrencias
```

Broadcast de ocorrências com heartbeat PING/PONG a cada 30s.

## 🧠 Arquitetura

```
Router → Service → Repository → ORM → DB
   │
   └── WebSocket Broadcast
```

Camadas isoladas com injeção de dependência — cada uma testável com mock da anterior.

## ☑️ Status do Projeto

✅ **28/28 subtasks** — implementação completa das 3 camadas. Código revisado, 334 testes passando.

---

<p align="center">
  <sub>Feito com 💀 por desenvolvedores que já moraram em condomínio.</sub>
</p>
