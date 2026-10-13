import hashlib
import streamlit as st
from agent import new_chat, ask

st.set_page_config(page_title="SkyAssist", page_icon="✈️")
st.title("✈️ SkyAssist – Airline Support")

if "chat" not in st.session_state:
    st.session_state.chat = new_chat()
    st.session_state.history = []
    st.session_state.seen = set()  # hashes of attachments already sent

with st.sidebar:
    st.header("Attach")
    img = st.file_uploader("Image (boarding pass, baggage photo…)", type=["png", "jpg", "jpeg"])
    voice = st.audio_input("Or record a voice message")
    if st.button("New conversation"):
        st.session_state.clear()
        st.rerun()
    st.caption("Try PNRs: ABC123, XYZ789")


def render(m):
    with st.chat_message(m["role"]):
        st.markdown(m["text"])
        if m.get("image"):
            st.image(m["image"], width=250)
        if m.get("audio"):
            st.audio(m["audio"], format="audio/wav")
        for c in m.get("calls", []):
            st.caption(f"🔧 {c['name']}({c['args']})")


def new_bytes(widget):
    """Return the widget's bytes only if they have not been sent before."""
    if not widget:
        return None
    data = widget.getvalue()
    if hashlib.md5(data).hexdigest() in st.session_state.seen:
        return None
    return data


def mark_seen(*blobs):
    for b in blobs:
        if b:
            st.session_state.seen.add(hashlib.md5(b).hexdigest())


for m in st.session_state.history:
    render(m)

prompt = st.chat_input("How can I help?")
img_bytes = new_bytes(img)
voice_bytes = new_bytes(voice)

if prompt or voice_bytes or img_bytes:
    files = []
    if img_bytes:
        files.append((img_bytes, img.type))
    if voice_bytes:
        files.append((voice_bytes, "audio/wav"))

    user_msg = {
        "role": "user",
        "text": prompt or ("🎤 (voice message)" if voice_bytes else "📷 (image)"),
        "image": img_bytes,
        "audio": voice_bytes,
    }
    st.session_state.history.append(user_msg)
    render(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply, calls = ask(st.session_state.chat, prompt, files)
                mark_seen(img_bytes, voice_bytes)  # only after a successful send
            except Exception as e:
                reply, calls = f"Error: {e}", []
        st.markdown(reply)
        for c in calls:
            st.caption(f"🔧 {c['name']}({c['args']})")
    st.session_state.history.append({"role": "assistant", "text": reply, "calls": calls})
