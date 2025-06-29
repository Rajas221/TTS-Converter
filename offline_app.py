import streamlit as st
import asyncio
import edge_tts
import uuid
import os
import simpleaudio as sa
from pydub import AudioSegment

# ------------ Globals ------------
if "play_obj" not in st.session_state:
    st.session_state.play_obj = None

# ------------ Page Config ------------
st.set_page_config(page_title="Deep Male Voice TTS", layout="centered")
st.title("Text To Speech Converter")
st.markdown("Paste your story and choose to either **narrate or download** it with a deep male voice.")

# ------------ UI ------------
text_input = st.text_area("✍️ Enter your story or text", height=300, placeholder="Paste your story here...")

voice_option = st.selectbox(
    "🧑‍🎤 Choose a Male Voice",
    ["en-US-GuyNeural", "en-GB-RyanNeural", "en-IN-PrabhatNeural"]
)

col1, col2, col3 = st.columns(3)

# ------------ TTS with Edge ------------
async def edge_tts_to_file(text, voice_id):
    filename = f"output_{uuid.uuid4().hex}.mp3"
    communicate = edge_tts.Communicate(text, voice=voice_id)
    await communicate.save(filename)
    return filename

def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.replace(".mp3", ".wav")
    sound = AudioSegment.from_mp3(mp3_path)
    sound.export(wav_path, format="wav")
    return wav_path

def play_audio(wav_path):
    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()
    st.session_state.play_obj = play_obj
    play_obj.wait_done()
    st.session_state.play_obj = None

def stop_audio():
    if st.session_state.play_obj is not None and st.session_state.play_obj.is_playing():
        st.session_state.play_obj.stop()
        st.session_state.play_obj = None

# ------------ Narrate Button ------------
if col1.button("🎙️ Narrate"):
    if not text_input.strip():
        st.warning("Please enter text.")
    else:
        with st.spinner("🔊 Generating narration..."):
            mp3_file = asyncio.run(edge_tts_to_file(text_input, voice_option))
            wav_file = convert_mp3_to_wav(mp3_file)
            st.audio(mp3_file, format="audio/mp3")
            st.success("✅ Narration ready! Playing...")
            play_audio(wav_file)
            os.remove(mp3_file)
            os.remove(wav_file)

# ------------ Stop Narration Button ------------
if col2.button("🛑 Stop Narration"):
    stop_audio()
    st.info("Narration stopped.")

# ------------ Save as MP3 Button ------------
if col3.button("💾 Save as MP3"):
    if not text_input.strip():
        st.warning("Please enter text.")
    else:
        with st.spinner("🎧 Converting to MP3..."):
            output_file = asyncio.run(edge_tts_to_file(text_input, voice_option))
            st.audio(output_file, format="audio/mp3")
            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download MP3", f, file_name="deep_voice_story.mp3", mime="audio/mp3")
            st.success("✅ Conversion completed and mp3 saved.")
            os.remove(output_file)
