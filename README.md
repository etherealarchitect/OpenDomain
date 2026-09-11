<div align="center">

# 🌐 OpenDomain

### The open-source domain registrar with an AI agent built in.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-purple.svg)]()

Manage your entire domain fleet — search, register, configure DNS, monitor uptime,
and trade on the marketplace — all from a single agentic terminal powered by Claude.

</div>

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🤖 **AI Agent** | Natural-language control of your whole account via Claude tool-use (21 tools). Register domains, edit DNS, check uptime, list on the marketplace — just ask. |
| 🌐 **Domains** | Search across 1,000+ TLDs with full ICANN lifecycle support — registration, transfer, renewal, locking, WHOIS privacy, and DNSSEC. |
| 🗂️ **DNS Management** | Full zone & record management with one-click templates for GitHub Pages, Vercel, Netlify, Google Workspace and more. BIND import/export. |
| 📈 **Monitoring** | Uptime checks, SSL certificate expiry tracking, domain availability watchlists, and configurable alert rules. |
| 🏪 **Marketplace** | Browse listings, list your own domains for sale, receive and negotiate offers, and complete transfers. |
| 💳 **Billing** | Account balance, payment methods, invoice history, and quick admin access to API keys, webhooks, and email forwarding. |
| ⚙️ **Settings** | API keys, webhooks, email forwarding, SSL management, bulk operations, and a first-class CLI. |

## 🎨 Design

- **Light theme** with a muted **purple → violet** accent palette.
- Terminal-inspired monospace touches (JetBrains Mono) paired with clean Inter typography.
- Fully responsive — desktop, tablet, and mobile.

## 🛠️ Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS, shadcn/ui, Recharts, React Query, React Router
- **Icons:** lucide-react
- **AI:** Claude (tool-use) via the Base44 Core integration
- **Platform:** Base44 (auth, database, integrations, hosting)

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/etherealarchitect/opendomain.git
cd opendomain

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Then open the printed local URL in your browser.

## 📁 Project Structure

```
src/
├── pages/            # Route views (Home, Agent, Domains, DNS, ...)
├── components/       # Layout, UI primitives, shared components
├── lib/              # Utils, query client, auth context
└── index.css         # Design tokens (purple theme)
```

## 🤖 The Agent

The AI agent is the heart of OpenDomain. Instead of clicking through menus, just tell it what you need:

> *"Register opendomain.dev for 1 year with privacy on"*
> *"Add GitHub Pages DNS to agent.sh"*
> *"List powerdns.app on the marketplace for $2,500"*
> *"Show me domains expiring this month"*

The agent parses your intent, selects the right tool, validates parameters against your account, executes the action, and confirms the result.

## 📜 License

MIT © OpenDomain contributors

<div align="center">

**Built with ❤️ on [Base44](https://base44.com)**

</div>