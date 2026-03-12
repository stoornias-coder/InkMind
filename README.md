# ✦ InkMind

> **AI-powered interactive roleplay — private, free, and runs entirely in your browser.**

No account. No server. No data collection. Just you, your story, and the AI.

[![Live Demo](https://img.shields.io/badge/▶%20Live%20Demo-Play%20Now-gold?style=for-the-badge)](https://stoornias-coder.github.io/InkMind/)
[![Download APK](https://img.shields.io/badge/📱%20Android-Download%20APK-brightgreen?style=for-the-badge)](https://github.com/stoornias-coder/InkMind/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

![InkMind Screenshot](screenshot.png)

---

## What is InkMind?

InkMind is a **single-file HTML roleplay app** that lets you chat with AI characters in an immersive, narrative-driven experience. Think Character.AI — but fully private, open source, and running entirely on your device.

Your stories never leave your browser. No account required. No ads. Ever.

---

## ✦ Features

- **🎭 Rich character system** — Create characters with backstory, personality traits, voice style, and a custom opening message
- **🌍 World builder** — Build entire universes with lore, atmosphere, and multiple characters
- **✦ Focus mode** — One-on-one sessions with a single character from a world
- **🔀 Multi-model rotation** — Automatically switches between Groq (Llama) and Google Gemini when rate limits hit
- **🌐 EN / FR** — Full English and French interface. More languages coming.
- **📱 Mobile-friendly** — Designed for both desktop and mobile
- **🔒 100% private** — Everything stays in your browser's localStorage. Nothing is ever sent to our servers (we don't have any)
- **📦 Single file** — The entire app is one `.html` file. Download it. Open it. Play.

---

## 🚀 Getting Started

### Option 1 — Play instantly
Visit **[stoornias-coder.github.io/InkMind](https://stoornias-coder.github.io/InkMind/)** — no install needed.

### Option 2 — Run locally
```bash
git clone https://github.com/stoornias-coder/InkMind.git
# Then just open index.html in your browser
```

### Get your free API key
InkMind uses the **Groq API** — which has a generous free tier.

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Create a free account
3. Generate an API key
4. Paste it in InkMind's **⚙ Settings**

> Optionally add a **Google Gemini key** from [aistudio.google.com](https://aistudio.google.com/app/apikey) for automatic fallback when Groq rate limits hit.

---

## 🎭 Ready-to-play characters

InkMind ships with **20+ fan-made characters** across popular universes:

| Universe | Characters |
|---|---|
| ⚡ Harry Potter | Draco Malfoy, Tom Riddle, Sirius Black, Fred Weasley |
| 🐉 Game of Thrones | Jon Snow, Jaime Lannister, Daenerys, Tyrion, Arya |
| 🌙 Twilight | Edward Cullen, Jacob Black, Jasper Hale, Emmett |
| ⚔️ Solo characters | Itachi, Levi, Sebastian Michaelis, Kakashi, Zoro... |

> All characters are **fan-made and unofficial**. Not affiliated with any IP holder.

---

## 🛠 Tech stack

- **Vanilla HTML / CSS / JavaScript** — zero dependencies, zero build step
- **Groq API** — Llama 3.3 70B, Llama 4 Scout
- **Google Gemini API** — Gemini 2.0 Flash, Gemini 1.5 Flash-8B
- **localStorage** — all data stored client-side

---

## 🗺 Roadmap

- [ ] More languages (Spanish, Portuguese, German...)
- [ ] Character image generation
- [ ] Export conversations as PDF
- [ ] Community character sharing
- [x] Android app — [Download APK](https://github.com/stoornias-coder/InkMind/releases/latest)

---

## 🤝 Contributing

Want to add a character or universe? PRs are welcome.

1. Fork the repo
2. Add your character via the in-app creator
3. Export it as JSON
4. Open a PR with the JSON in `/characters`

---

## ⚠️ Disclaimer

InkMind is an independent fan project. All fictional characters belong to their respective creators. This project is not affiliated with, endorsed by, or connected to any official IP holder.

---

## 📄 License

MIT — do whatever you want, just keep the credit.

---

<p align="center">Made with 🖤 by <a href="https://github.com/stoornias-coder">stoornias-coder</a></p>
<p align="center"><em>Your stories. Your device. Your rules.</em></p>

