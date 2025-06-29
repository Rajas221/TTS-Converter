import streamlit as st
import pyttsx3
import threading
from gtts import gTTS
from pydub import AudioSegment
import os
import uuid

# ✅ Use a global stop flag (not session_state inside thread)
stop_flag = False

# Setup pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'male' in voice.name.lower() or 'david' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)

def split_text(text, max_chars=10000):
    parts = []
    while len(text) > max_chars:
        split_at = text.rfind('.', 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        parts.append(text[:split_at + 1])
        text = text[split_at + 1:].strip()
    parts.append(text)
    return parts

# 🧠 Updated speak_chunks
def speak_chunks(text):
    global stop_flag
    chunks = split_text(text)
    for chunk in chunks:
        if stop_flag:
            break
        engine.say(chunk)
        engine.runAndWait()

# Streamlit UI
st.title("🧔 Deep Voice Storyteller - Narrate & Save")
text_input = st.text_area("Your Story", height=300)

col1, col2, col3 = st.columns(3)

if col1.button("🎙 Narrate"):
    if not text_input.strip():
        st.warning("Please enter text.")
    else:
        stop_flag = False
        threading.Thread(target=speak_chunks, args=(text_input,), daemon=True).start()
        st.success("Narration started...")

if col2.button("🛑 Stop Narration"):
    stop_flag = True
    engine.stop()
    st.info("Narration stopped.")

if col3.button("💾 Save as MP3"):
    if not text_input.strip():
        st.warning("Please enter text.")
    else:
        try:
            st.info("Converting to MP3...")
            tts = gTTS(text=text_input, lang='en')
            filename = f"tts_output_{uuid.uuid4().hex}.mp3"
            tts.save(filename)
            audio = AudioSegment.from_mp3(filename)
            st.audio(filename, format='audio/mp3')
            with open(filename, "rb") as file:
                st.download_button("⬇️ Download MP3", file, file_name="story_output.mp3", mime="audio/mp3")
            os.remove(filename)
        except Exception as e:
            st.error(f"Failed to save MP3: {e}")
