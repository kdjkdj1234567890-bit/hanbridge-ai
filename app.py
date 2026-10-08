"""HanBridge AI — Korean<->English business communication agent.

Runs on NVIDIA Nemotron models served via Nebius Token Factory
(OpenAI-compatible API). Set NEBIUS_API_KEY to use it.
"""

import streamlit as st

from hanbridge import config, llm, prompts

st.set_page_config(
    page_title="HanBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- sidebar ---
st.sidebar.title("🌉 HanBridge AI")
st.sidebar.caption("Korean ↔ English business communication agent")

api_key = st.sidebar.text_input(
    "Nebius Token Factory API key",
    type="password",
    value=config.NEBIUS_API_KEY,
    help="Get a free key at tokenfactory.nebius.com. New accounts include "
    "promotional credits; hackathon builders get extra credits via the "
    "Devpost resources page.",
)

if "model_id" not in st.session_state:
    st.session_state.model_id = config.NEBIUS_MODEL

if st.sidebar.button("🔄 Load available models"):
    try:
        ids = llm.list_models(api_key)
        nvidia = [m for m in ids if any(h in m.lower() for h in config.NVIDIA_HINTS)]
        st.session_state.all_models = ids
        st.session_state.nvidia_models = nvidia
        st.session_state.model_id = llm.pick_nvidia_model(nvidia or ids)
        st.sidebar.success(f"Found {len(ids)} models ({len(nvidia)} NVIDIA).")
    except llm.MissingApiKeyError as e:
        st.sidebar.error(str(e))
    except Exception as e:  # noqa: BLE001 - surface API errors honestly
        st.sidebar.error(f"Could not list models: {e}")

model_options = st.session_state.get(
    "nvidia_models", [st.session_state.model_id] if st.session_state.model_id else []
)
if model_options and model_options != [""]:
    st.session_state.model_id = st.sidebar.selectbox(
        "Model (NVIDIA Nemotron via Nebius)",
        options=model_options,
        index=0,
    )
else:
    st.sidebar.text_input(
        "Model ID (from Token Factory console)",
        value=st.session_state.model_id,
        key="manual_model",
        help="Find exact IDs at tokenfactory.nebius.com → Models.",
    )
    st.session_state.model_id = st.session_state.manual_model

st.sidebar.divider()
st.sidebar.markdown(
    "**How it works**\n"
    "1. Paste a business message\n"
    "2. HanBridge translates it **and** adapts the tone for the target "
    "business culture\n"
    "3. Learn from the tone & culture notes"
)
st.sidebar.caption("Built for the Nebius × NVIDIA Global AI Hackathon.")

# ------------------------------------------------------------- helpers ---
def ready() -> bool:
    """Check credentials and show setup guidance if missing."""
    if not (api_key or "").strip():
        st.warning(
            "👈 Enter your **Nebius Token Factory API key** in the sidebar to "
            "start. Get one free at https://tokenfactory.nebius.com/"
        )
        return False
    if not (st.session_state.model_id or "").strip():
        st.warning(
            "👈 Click **Load available models** in the sidebar (or paste a "
            "model ID) to choose an NVIDIA Nemotron model."
        )
        return False
    return True


def call_json(system_prompt: str, user_text: str) -> dict | None:
    try:
        client = llm.get_client(api_key)
        return llm.translate_json(
            client, st.session_state.model_id, system_prompt, user_text
        )
    except llm.MissingApiKeyError as e:
        st.error(str(e))
    except Exception as e:  # noqa: BLE001
        st.error(f"Translation failed: {e}")
    return None


def render_notes(title: str, items: list[str], icon: str):
    if items:
        st.subheader(f"{icon} {title}")
        for it in items:
            st.markdown(f"- {it}")


# ------------------------------------------------------------------ tabs ---
tab1, tab2, tab3 = st.tabs(
    ["🇰🇷 → 🇺🇸 Korean → English", "🇺🇸 → 🇰🇷 English → Korean", "💬 Live Chat"]
)

# ------------------------------------------------- Tab 1: KR -> EN ---
with tab1:
    st.header("Korean → English, Western business tone")
    kr_text = st.text_area(
        "Korean business text",
        height=180,
        placeholder="예: 안녕하세요 김부장님, 지난번에 말씀드린 견적서 관련하여 혹시 검토해 보셨을지 여쭙고자 연락드렸습니다...",
    )
    tone = st.slider(
        "Tone adaptation strength",
        1, 5, 3,
        help="1 = preserve original tone, 5 = rewrite like a native executive",
    )
    if st.button("Translate →", key="kr_en_go", type="primary"):
        if not kr_text.strip():
            st.warning("Please paste some Korean text first.")
        elif ready():
            with st.spinner("Nemotron is translating…"):
                result = call_json(
                    prompts.KR_TO_EN_SYSTEM.format(
                        tone_guidance=prompts.TONE_GUIDANCE[tone]
                    ),
                    kr_text,
                )
            if result:
                if result.get("subject_line"):
                    st.info(f"**Suggested subject:** {result['subject_line']}")
                st.subheader("✉️ Translation")
                st.markdown(result.get("translation", ""))
                col_a, col_b = st.columns(2)
                with col_a:
                    render_notes(
                        "Tone adjustments",
                        result.get("tone_adjustments", []),
                        "🎯",
                    )
                with col_b:
                    render_notes(
                        "Cultural notes",
                        result.get("cultural_notes", []),
                        "🌏",
                    )

# ------------------------------------------------- Tab 2: EN -> KR ---
with tab2:
    st.header("English → Korean, with business etiquette")
    en_text = st.text_area(
        "English business text",
        height=180,
        placeholder="e.g. Hi team, please review the attached proposal and get back to me by Friday…",
    )
    formality = st.selectbox(
        "Speech level",
        ["Auto (recommended)", "합니다체 — formal", "해요체 — polite"],
    )
    if st.button("→ Translate", key="en_kr_go", type="primary"):
        if not en_text.strip():
            st.warning("Please paste some English text first.")
        elif ready():
            with st.spinner("Nemotron is translating…"):
                result = call_json(
                    prompts.EN_TO_KR_SYSTEM.format(formality=formality),
                    en_text,
                )
            if result:
                st.subheader("✉️ 번역 결과")
                st.markdown(result.get("translation", ""))
                col_a, col_b = st.columns(2)
                with col_a:
                    render_notes(
                        "Honorific choices",
                        result.get("honorific_notes", []),
                        "🙇",
                    )
                with col_b:
                    render_notes(
                        "Cultural notes",
                        result.get("cultural_notes", []),
                        "🌏",
                    )

# ---------------------------------------------------- Tab 3: chat ---
with tab3:
    st.header("Live bilingual chat")
    st.caption(
        "Type in Korean or English — each message is translated instantly, "
        "Slack/Teams style."
    )
    if "chat" not in st.session_state:
        st.session_state.chat = []
    col1, col2 = st.columns(2)
    with col1:
        chat_direction = st.radio(
            "I write in…", ["Korean → English", "English → Korean"],
            horizontal=True,
        )
    with col2:
        chat_tone = st.select_slider(
            "Chat tone", options=[1, 2, 3, 4, 5], value=3,
            help="1 = literal, 5 = fully natural business tone",
        )

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["original"])
            st.caption(f"🌐 {msg['translated']}")

    if user_msg := st.chat_input("Type your message…"):
        if ready():
            target = "English" if chat_direction.startswith("Korean") else "Korean"
            with st.spinner("Translating…"):
                try:
                    client = llm.get_client(api_key)
                    translated = llm.translate_text(
                        client,
                        st.session_state.model_id,
                        prompts.CHAT_SYSTEM.format(
                            target_language=target,
                            tone_guidance=prompts.TONE_GUIDANCE[chat_tone],
                        ),
                        user_msg,
                    )
                except Exception as e:  # noqa: BLE001
                    st.error(f"Translation failed: {e}")
                    translated = None
            if translated:
                st.session_state.chat.append(
                    {"role": "user", "original": user_msg, "translated": translated}
                )
                st.rerun()

    if st.session_state.chat and st.button("Clear chat"):
        st.session_state.chat = []
        st.rerun()
