import gradio as gr
from groq import Groq
import json
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
HF_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
SUMMARY_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 900
SUMMARY_EVERY = 6

SYSTEM_PROMPT = """You are an immersive AI Game Master for narrative roleplay.

━━━ PLAYER ROLE — CRITICAL ━━━
At the start of every response, silently confirm: who is the player character?
The player character is whoever "tu/you" refers to in the scenario.
All other named characters are NPCs — even if they are the player's spouse, parent, or enemy.

If you realize mid-story you misidentified a character → correct silently next response. Never continue an error.

━━━ PLAYER BOUNDARY ━━━
NEVER invent actions, words, gestures, tone, or emotions for the player.
You MAY reflect what the player wrote — seen through an NPC's reaction.

FORBIDDEN: "Tu ris", "Ta voix résonne", "Tu te retournes", "Ton regard défiant"
ALLOWED: "Il observe tes mains", "Son regard suit tes mouvements"

━━━ NPC BEHAVIOR ━━━
Every response must end with an NPC speaking or acting — never waiting or watching.
When multiple NPCs are present, always name who speaks. No ambiguous dialogue.

━━━ NARRATIVE ━━━
Present tense. 120–180 words. Short paragraphs. Sensory detail.
Show emotions through behavior — never state them.
End with forward tension: an NPC action or unanswered question.

━━━ LANGUAGE ━━━
Detect the player's language from message 1. Write 100% in that language. Zero foreign words.
Informal register for player character (tu/toi/tes in French, tú in Spanish, du in German).

━━━ OUTPUT SAFETY ━━━
If you feel uncertain or lose narrative coherence → stop, write a single short NPC line, and wait for the player.
Never generate garbled text, code fragments, or broken sentences. A short clean response is always better than a long broken one.

━━━ BANNED (all languages) ━━━
Similarity connectors: "comme"/"as if"/"como"/"wie" and equivalents → FORBIDDEN. Always rewrite.
Single-use words: "soudain/suddenly", "finalement/finally", "légèrement/slightly", "imperceptiblement/imperceptibly" → forbidden.
Atmosphere filler: "la tension est palpable", "l'atmosphère est lourde", "la pièce semble rétrécir" → forbidden. Use NPC action instead.
Repetition: same noun or adjective twice in one paragraph → use a synonym.

━━━ GRAMMAR (all languages) ━━━
Adjectives agree in gender and number. Tenses consistent within paragraph. Accents always correct.

━━━ PER RESPONSE CHECK ━━━
1. Who is the player? Confirmed.
2. Did I invent anything the player didn't write? → Delete.
3. Any banned word or filler? → Rewrite.
4. Does my response end with an NPC acting or speaking? → Fix if not.
5. Is every dialogue line attributed to a named character? → Fix if not.
6. Is the text clean and coherent? → If unsure, shorten drastically.
"""

GUIDED_QUESTIONS = """Welcome to **InkMind**.

Before we begin, tell me about the story you want to live.

**Answer these questions** *(all at once, in free text)*:

1. **Genre** — romance, fantasy, sci-fi, horror, slice of life, historical, thriller, post-apocalyptic...
2. **Your character** — gender, species or nature *(human, vampire, android, elf...)*
3. **Universe & Era** — contemporary, medieval, futuristic, alternate history...
4. **Tone** — dark & gritty, slow-burn, light & adventurous, mature, action-packed...
5. **NPCs** — any character types you want? *(love interest, rival, mentor, monster...)*
6. **Language** — what language should I narrate in?

*I'll handle the rest.*"""


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def append_msg(history, role, content):
    history.append({"role": role, "content": content})
    return history

def compress_history(client, raw_history):
    if not raw_history:
        return ""
    text = "\n".join([f"{r}: {m}" for r, m in raw_history])
    try:
        resp = client.chat.completions.create(
            model=SUMMARY_MODEL, max_tokens=200,
            messages=[
                {"role": "system", "content": "Summarize this roleplay history in 3-5 sentences. Keep key plot points, character names, decisions. Be concise."},
                {"role": "user", "content": text}
            ]
        )
        return resp.choices[0].message.content
    except:
        return ""

CORRECTION_PROMPT = """You are a silent text corrector. Return ONLY the corrected text. No comments.

FIX IN ORDER:
1. Any sentence describing the player character's uninvented actions, tone, or words → DELETE it.
2. "comme"/"as if"/"como"/"wie" or any similarity connector → rewrite without it.
3. Atmosphere filler ("la tension est palpable", "l'atmosphère est lourde", "la pièce semble") → delete or replace with a concrete NPC action.
4. Any foreign word mid-sentence → replace with correct word.
5. "vous/votre" for player character → replace with "tu/toi/te/ton/ta/tes".
6. Same noun or adjective repeated in one paragraph → synonym for 2nd occurrence.
7. Adjective agreement errors or missing accents → fix.
8. Response ending with NPC waiting/watching in silence → replace with NPC speaking or acting.

Start with the first word of the corrected text. Nothing else."""

def post_correct(client, raw_text):
    """Une seule passe propre avec le bon modèle."""
    if not raw_text or not raw_text.strip():
        return raw_text
    # Si le texte brut contient déjà des signes de hallucination → on ne corrige pas
    import re as _re
    glitch_signs = ['Page web', 'WebPage', 'scalablytyped', 'XPERIA', '.cmo', 'OnCollision']
    if any(sign in raw_text for sign in glitch_signs):
        return "..."  # Réponse vide plutôt que texte corrompu
    try:
        resp = client.chat.completions.create(
            model=SUMMARY_MODEL,
            max_tokens=1400,
            messages=[
                {"role": "system", "content": CORRECTION_PROMPT},
                {"role": "user", "content": raw_text}
            ]
        )
        result = resp.choices[0].message.content.strip()
        # Vérification anti-hallucination sur le résultat aussi
        if any(sign in result for sign in glitch_signs):
            return raw_text
        if len(result) > len(raw_text) * 0.4:
            return result
        return raw_text
    except:
        return raw_text
    try:
        resp = client.chat.completions.create(
            model=SUMMARY_MODEL,
            max_tokens=1400,
            messages=[
                {"role": "system", "content": CORRECTION_PROMPT},
                {"role": "user", "content": raw_text}
            ]
        )
        result = resp.choices[0].message.content.strip()
        if len(result) > len(raw_text) * 0.4:
            return result
        return raw_text
    except:
        return raw_text


def parse_guided_answers(client, user_input):
    try:
        resp = client.chat.completions.create(
            model=SUMMARY_MODEL, max_tokens=250,
            messages=[
                {"role": "system", "content": "Extract roleplay profile from user input. Return ONLY valid JSON (no markdown, no backticks) with keys: genre, character_gender, character_species, universe, era, tone, npc_types, language. Use null for anything not mentioned."},
                {"role": "user", "content": user_input}
            ]
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except:
        return {}

def build_system(profile, summary):
    """SYSTEM_PROMPT always comes first and is never truncated by context."""
    ctx = {}
    if profile:
        ctx["player_profile"] = profile
    if summary:
        ctx["story_so_far"] = summary
    # Always start with full system prompt — context is appended, never replaces
    system = SYSTEM_PROMPT
    if ctx:
        system += f"\n\n--- CURRENT STORY CONTEXT ---\n{json.dumps(ctx, ensure_ascii=False)}\n--- END CONTEXT ---"
    return system


# ─────────────────────────────────────────────
# MAIN CHAT
# ─────────────────────────────────────────────
def chat(user_message, history, mode, api_key, state):
    key = HF_API_KEY or (api_key.strip() if api_key else "")

    if state is None:
        state = {"profile": {}, "summary": "", "turn_count": 1, "setup_done": False, "raw_history": []}

    if not key:
        history = append_msg(history, "assistant", "Please enter your Groq API key in the settings panel.")
        yield history, state, ""
        return

    client = Groq(api_key=key)

    # MODE GUIDÉ — parse + démarrage streamé
    if mode == "guided" and not state["setup_done"]:
        profile = parse_guided_answers(client, user_message)
        state["profile"] = profile
        state["setup_done"] = True
        history = append_msg(history, "user", user_message)
        lang = profile.get("language") or "English"
        starter = (
            f"Player profile: {json.dumps(profile, ensure_ascii=False)}\n\n"
            f"Write the opening scene in {lang}. "
            "Set atmosphere immediately. Ground the scene in a specific moment, place, and sensory detail. "
            "Introduce the world and hint at the first tension through action and environment — not exposition. "
            "No greeting. Start directly with the first word of the narrative."
        )
        history = append_msg(history, "assistant", "")
        reply = ""
        stream = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=[
            {"role": "system", "content": build_system(state["profile"], state["summary"])},
            {"role": "user", "content": starter}
        ], stream=True)
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            reply += delta
            history[-1]["content"] = reply
            yield history, state, ""
        state["raw_history"] += [("user", starter), ("assistant", reply)]
        state["turn_count"] += 1
        return

    # MODE LIBRE — étape 2 : scénario reçu → démarrage streamé
    if mode == "free" and not state["setup_done"]:
        state["setup_done"] = True
        history = append_msg(history, "user", user_message)
        starter = (
            "The player has written the opening scene below. "
            "Read it carefully. Do NOT rewrite or summarize it. Continue the story from exactly where it ends.\n\n"
            f"PLAYER SCENE:\n{user_message}\n\n"
            "Continue as Game Master in the same language and style. "
            "No greeting. No summary. Write only the next beat of the scene."
        )
        history = append_msg(history, "assistant", "")
        reply = ""
        stream = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": starter}
        ], stream=True)
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            reply += delta
            history[-1]["content"] = reply
            yield history, state, ""
        state["raw_history"] += [("user", starter), ("assistant", reply)]
        state["turn_count"] += 1
        return

    # NARRATION EN COURS
    state["turn_count"] += 1
    history = append_msg(history, "user", user_message)

    if state["turn_count"] % SUMMARY_EVERY == 0 and len(state["raw_history"]) > 10:
        state["summary"] = compress_history(client, state["raw_history"][:-6])
        state["raw_history"] = state["raw_history"][-6:]

    messages = [{"role": "system", "content": build_system(state["profile"], state["summary"])}]
    for role_str, content in state["raw_history"][-8:]:
        messages.append({"role": "user" if role_str == "user" else "assistant", "content": content})
    messages.append({"role": "user", "content": user_message})

    # Indicateur pendant la génération
    history = append_msg(history, "assistant", "...")
    yield history, state, ""

    # Génération complète sans streaming
    resp = client.chat.completions.create(
        model=MODEL, max_tokens=MAX_TOKENS, messages=messages
    )
    raw_reply = resp.choices[0].message.content.strip()

    # Post-correction automatique
    history[-1]["content"] = "relecture..."
    yield history, state, ""

    corrected = post_correct(client, raw_reply)
    history[-1]["content"] = corrected
    yield history, state, ""
    state["raw_history"] += [("user", user_message), ("assistant", corrected)]


# ─────────────────────────────────────────────
# CSS — dark/light via classe sur body
# ─────────────────────────────────────────────
# Variables CSS uniquement — toggle ne swape QUE ces ~15 lignes
VARS_DARK = """:root{--gold:#c9b99a;--gold-dim:#7a6a52;--bg:#0e0e0e;--bg2:#141414;--bg3:#1c1c1c;--border:#252525;--border2:#2e2e2e;--text:#f0ece4;--text-dim:#555;--text-muted:#2a2a2a;--user-text:#666;--user-border:#2a2a2a;}"""
VARS_LIGHT = """:root{--gold:#8a6e3a;--gold-dim:#a07840;--bg:#f4f1ec;--bg2:#eceae4;--bg3:#e2dfd8;--border:#d5cfc5;--border2:#c8c2b8;--text:#1a1714;--text-dim:#888;--text-muted:#bbb;--user-text:#888;--user-border:#ccc;}"""

CSS_LIGHT = VARS_LIGHT  # compat
CSS_DARK = VARS_DARK    # compat

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400&display=swap');
html, body, .gradio-container, .main, .wrap, .gap,
.block, .form, .container, .panel, [class*="svelte-"] {
    background: var(--bg) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    box-shadow: none !important;
    font-family: 'Inter', sans-serif !important;
}

.ink-header {
    text-align: center;
    padding: 1.8rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.4rem;
}
.ink-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2.5rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.2em;
    color: var(--gold) !important;
    margin: 0 !important;
}
.ink-sub {
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.28em;
    text-transform: uppercase;
    margin-top: 0.35rem;
}

.landing-card {
    max-width: 680px;
    margin: 1rem auto;
    padding: 2rem 2.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg2) !important;
}
.landing-card h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    font-weight: 300;
    color: var(--gold);
    margin: 0 0 0.3rem 0;
}
.landing-card p { color: var(--text-dim); font-size: 0.82rem; margin: 0 0 1.5rem 0; line-height: 1.6; }

.mode-btn {
    width: 100%;
    padding: 0.9rem 1.1rem !important;
    margin-bottom: 0.7rem !important;
    background: var(--bg) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
    text-align: left !important;
    transition: all 0.2s !important;
}
.mode-btn:hover {
    border-color: var(--gold-dim) !important;
    background: var(--bg3) !important;
    color: var(--gold) !important;
}

/* CHATBOT */
#ink-chatbot,
#ink-chatbot > div,
#ink-chatbot > div > div {
    background: var(--bg) !important;
    background-color: var(--bg) !important;
    border-color: var(--border) !important;
    box-shadow: none !important;
}
#ink-chatbot {
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* Supprime avatars */
#ink-chatbot [class*="avatar"],
#ink-chatbot [class*="icon"],
#ink-chatbot img { display: none !important; }

/* Wrappers rows */
#ink-chatbot [class*="message-row"],
#ink-chatbot [class*="bubble"],
#ink-chatbot [class*="wrap"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* MESSAGE USER — rectangle simple */
#ink-chatbot .message {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#ink-chatbot .user {
    display: flex !important;
    justify-content: flex-end !important;
    background: transparent !important;
    padding: 0.2rem 0.5rem !important;
}
#ink-chatbot .user .message,
#ink-chatbot [data-testid="user"] .message {
    background: transparent !important;
    border: 1px solid var(--user-border) !important;
    border-radius: 3px !important;
    color: var(--user-text) !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 0.8rem !important;
    max-width: 80% !important;
    box-shadow: none !important;
    display: inline-block !important;
}

/* MESSAGE BOT */
#ink-chatbot .bot,
#ink-chatbot [data-testid="bot"] {
    background: transparent !important;
    padding: 0.2rem 0.5rem !important;
}
#ink-chatbot .bot .message,
#ink-chatbot [data-testid="bot"] .message {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid var(--gold-dim) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.08rem !important;
    line-height: 1.9 !important;
    padding: 0.5rem 0.8rem 0.5rem 1rem !important;
    max-width: 100% !important;
    box-shadow: none !important;
}

/* INPUT fusionné */
.input-row {
    display: flex !important;
    align-items: stretch !important;
    gap: 0 !important;
    margin-top: 0.6rem;
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important;
    overflow: hidden;
}
.input-row > * { background: transparent !important; border: none !important; box-shadow: none !important; }
.input-row textarea {
    flex: 1 !important;
    min-height: 50px !important;
    max-height: 160px !important;
    resize: none !important;
    border: none !important;
    background: transparent !important;
    color: var(--text) !important;
    padding: 0.75rem 0.9rem !important;
    font-size: 0.92rem !important;
}
.input-row textarea:focus { outline: none !important; box-shadow: none !important; border: none !important; }
.input-row textarea::placeholder { color: var(--text-dim) !important; }

.send-btn, .send-btn > button {
    min-width: 50px !important;
    background: var(--bg3) !important;
    border: none !important;
    border-left: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    color: var(--gold) !important;
    font-size: 1.1rem !important;
    cursor: pointer;
    padding: 0 0.9rem !important;
    transition: background 0.2s !important;
    align-self: stretch !important;
}
.send-btn:hover > button,
.send-btn > button:hover { background: var(--bg2) !important; }

/* TOP BAR */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.8rem;
}
.top-bar-title {
    font-family: 'Cormorant Garamond', serif;
    color: var(--gold);
    font-size: 1.1rem;
    font-weight: 300;
    letter-spacing: 0.1em;
}
.top-bar-mode { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.15em; }

.theme-btn {
    background: transparent;
    border: 1px solid var(--border2);
    color: var(--text-dim);
    border-radius: 3px;
    padding: 0.15rem 0.55rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
}
.theme-btn:hover { border-color: var(--gold-dim); color: var(--gold); }

button.secondary, button[variant="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-dim) !important;
    border-radius: 3px !important;
    font-size: 0.78rem !important;
    transition: all 0.2s !important;
}
button.secondary:hover { border-color: var(--gold-dim) !important; color: var(--gold) !important; }

label > span, fieldset > legend > span {
    color: var(--text-dim) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 0.85rem 0 !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }
"""

CSS = CSS_LIGHT + CSS_BASE


# ─────────────────────────────────────────────
# UI LOGIC
# ─────────────────────────────────────────────
def init_state(mode_val):
    state = {"profile": {}, "summary": "", "turn_count": 1, "setup_done": False, "raw_history": []}
    history = []
    if mode_val == "guided":
        history = append_msg(history, "assistant", GUIDED_QUESTIONS)
    else:
        history = append_msg(history, "assistant", "Write or paste the scenario you want to play.\n\nA plot, a setting, a universe, a fanfiction — anything. As long or short as you like. I'll take it from there.")
    return history, state

def go_to_play(mode_val):
    history, new_state = init_state(mode_val)
    mode_label = "Guided Setup" if mode_val == "guided" else "Free Scenario"
    top_html = f'<div class="top-bar"><span class="top-bar-title">InkMind</span><span class="top-bar-mode">{mode_label}</span></div>'
    return gr.update(visible=False), gr.update(visible=True), history, new_state, top_html

def clear_and_go_home():
    return gr.update(visible=True), gr.update(visible=False), [], None, ""

def send_message(msg, history, mode_val, key, state):
    if not msg or not msg.strip():
        yield history, state, ""
        return
    for val in chat(msg, history, mode_val, key, state):
        yield val

def toggle_theme(current):
    new_theme = "light" if current == "dark" else "dark"
    new_vars = VARS_LIGHT if new_theme == "light" else VARS_DARK
    # On swape UNIQUEMENT les variables CSS, pas tout le CSS_BASE
    return new_theme, gr.update(value=f"<style>{new_vars}</style>")


# ─────────────────────────────────────────────
# JS — Enter = nouvelle ligne (injecté inline)
# ─────────────────────────────────────────────
ENTER_JS = """
<script>
(function() {
    function hookTextarea() {
        document.querySelectorAll('.input-row textarea').forEach(function(ta) {
            if (ta._inkHooked) return;
            ta._inkHooked = true;
            ta.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    var start = this.selectionStart;
                    var end = this.selectionEnd;
                    var val = this.value;
                    this.value = val.slice(0, start) + '\\n' + val.slice(end);
                    this.selectionStart = this.selectionEnd = start + 1;
                    this.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }, true);
        });
    }
    // Observer pour attraper le textarea quand il apparaît
    var obs = new MutationObserver(hookTextarea);
    obs.observe(document.body, {childList: true, subtree: true});
    setInterval(hookTextarea, 500);
})();
</script>
"""


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
with gr.Blocks(title="InkMind") as demo:

    state       = gr.State(None)
    current_mode = gr.State("guided")
    theme_state  = gr.State("light")

    # CSS dynamique (light/dark swap)
    dynamic_css = gr.HTML(f"<style>{VARS_LIGHT}{CSS_BASE}</style>")

    gr.HTML("""
    <div class="ink-header">
        <h1 class="ink-title">InkMind</h1>
        <p class="ink-sub">Immersive AI Narrative Roleplay &nbsp;·&nbsp; Multilingual</p>
    </div>
    """)

    # ── LAYER 1 : LANDING ──
    with gr.Column(visible=True) as landing_col:
        with gr.Column(elem_classes=["landing-card"]):
            gr.HTML("""
            <h2>Choose your experience</h2>
            <p>An immersive AI Game Master, ready for any universe. Multilingual. Narrative-first.</p>
            """)

            api_key = gr.Textbox(
                label="Groq API Key",
                placeholder="gsk_...  (leave empty if provided by host)",
                type="password",
                lines=1,
                visible=not bool(HF_API_KEY)
            )

            gr.HTML("<hr>")
            gr.HTML("<p style='color:var(--text-dim);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.7rem'>Select a mode</p>")

            btn_guided = gr.Button("📖  Guided Setup  —  Answer a few questions, I build your world  →", elem_classes=["mode-btn"])
            btn_free   = gr.Button("✍️  Free Scenario  —  Write or paste your scenario and dive in  →", elem_classes=["mode-btn"])

            gr.HTML("<hr>")

            theme_btn_landing = gr.Button("◑  Toggle Light / Dark", elem_classes=["mode-btn"])

    # ── LAYER 2 : PLAY ──
    with gr.Column(visible=False) as play_col:

        top_bar_html = gr.HTML("")

        chatbot = gr.Chatbot(
            label="",
            height=520,
            elem_id="ink-chatbot",
            elem_classes=["chatbot-wrap"],
            show_label=False,
            render_markdown=True,
        )

        with gr.Row(elem_classes=["input-row"]):
            user_input = gr.Textbox(
                placeholder="Write here...  (Enter = new line  |  ➤ = send)",
                lines=2,
                max_lines=8,
                scale=10,
                container=False,
                show_label=False,
            )
            send_btn = gr.Button("➤", elem_classes=["send-btn"], scale=1)

        with gr.Row():
            back_btn    = gr.Button("← New story", variant="secondary", scale=2)
            theme_btn_play = gr.Button("◑", variant="secondary", scale=1)

    # ── EVENTS ──

    btn_guided.click(
        lambda: go_to_play("guided"),
        outputs=[landing_col, play_col, chatbot, state, top_bar_html]
    ).then(lambda: "guided", outputs=[current_mode])

    btn_free.click(
        lambda: go_to_play("free"),
        outputs=[landing_col, play_col, chatbot, state, top_bar_html]
    ).then(lambda: "free", outputs=[current_mode])

    send_btn.click(
        send_message,
        inputs=[user_input, chatbot, current_mode, api_key, state],
        outputs=[chatbot, state, user_input],
    )

    back_btn.click(
        clear_and_go_home,
        outputs=[landing_col, play_col, chatbot, state, user_input]
    )

    # Light/dark toggle
    theme_btn_landing.click(toggle_theme, inputs=[theme_state], outputs=[theme_state, dynamic_css])
    theme_btn_play.click(toggle_theme, inputs=[theme_state], outputs=[theme_state, dynamic_css])

if __name__ == "__main__":
    demo.queue()
    demo.launch(css=VARS_LIGHT + CSS_BASE)

