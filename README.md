# 🖋️ InkMind

**Immersive AI Narrative Roleplay · Multilingual**

An AI Game Master for text-based roleplay. Write your scenario, and InkMind narrates the world, the NPCs, and the consequences — never playing your character for you.

---

## ✨ Features

- **Free Scenario** — paste any plot, universe, or fanfiction and start immediately
- **Guided Setup** — answer a few questions and let InkMind build your world
- **Fully multilingual** — writes in your language automatically
- **Streaming narration** with automatic post-correction
- **Light / Dark mode**
- **Memory compression** — handles long sessions without losing the story

---

## 🚀 Try it

👉 [Live on Hugging Face Spaces](#) *(replace with your Space URL)*

---

## 🛠️ Run locally

```bash
git clone https://github.com/YOURNAME/inkmind.git
cd inkmind
pip install -r requirements.txt
```

Set your Groq API key:
```bash
export GROQ_API_KEY=gsk_...
```

Then:
```bash
python app.py
```

---

## 🔑 API Key

InkMind uses the [Groq API](https://console.groq.com) (free tier available).  
On Hugging Face Spaces, add your key as a **Secret** named `GROQ_API_KEY`.  
Locally, paste it in the interface or set the environment variable.

---

## 📁 Structure

```
app.py            main application
requirements.txt
README.md
.gitignore
```

---

## ⚠️ Content

Designed for narrative storytelling — drama, romance, thriller, fantasy, sci-fi.  
The underlying model (Llama 4 Maverick via Groq) applies standard content filters.

---

## 📄 License

MIT — free to use, modify, and share.

