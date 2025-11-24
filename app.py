# # # # # # # import streamlit as st
# # # # # # # import nltk
# # # # # # # from transformers import pipeline
# # # # # # # from nltk.corpus import stopwords
# # # # # # # from nltk.tokenize import word_tokenize


# # # # # # # chatbot = pipeline("text-generation", model="distilgpt2")

# # # # # # # def healthcare_chatbot(user_input):
# # # # # # #     if "symptoms" in user_input:
# # # # # # #         return "Please consult a Doctor for accurate advice"
# # # # # # #     elif "appointment" in user_input:
# # # # # # #         return "would you like to schedule an appointment with the doctor"
# # # # # # #     elif "medication" in user_input:
# # # # # # #         return "it's a important to take prescribe medicines regulary. If you have any concerns please consult a doctor "
# # # # # # #     else:
# # # # # # #         response = chatbot(user_input,max_length = 500, num_return_sequences=1)
# # # # # # #     return response[0]['generated_text']
    
    
# # # # # # # def main():
# # # # # # #     st.set_page_config(page_title="Healthcare Chatbot", page_icon="💊")
# # # # # # #     st.title("Healthcare Assistant Chatbot")
# # # # # # #     user_input = st.text_input("How can I assist you today?")
# # # # # # #     print(user_input)
# # # # # # #     if st.button("submit"):
# # # # # # #         if user_input:
# # # # # # #             st.write("👩 user : ",user_input)
# # # # # # #             with st.spinner("Processing your query,Please wait...."):
# # # # # # #                 response = healthcare_chatbot(user_input)
# # # # # # #             st.write("🌸 Healthcare Assistant :",response)
# # # # # # #             print(response)
# # # # # # #         else:
# # # # # # #             st.write("Please enter a message to get a response")

# # # # # # # main()










# # # # # # app.py
# # # # # import os
# # # # # import streamlit as st
# # # # # import random
# # # # # import datetime
# # # # # import tempfile
# # # # # import base64
# # # # # from io import BytesIO
# # # # # from reportlab.lib.pagesizes import letter
# # # # # from reportlab.pdfgen import canvas

# # # # # # Optional voice deps (only used if installed)
# # # # # try:
# # # # #     import speech_recognition as sr
# # # # #     from gtts import gTTS
# # # # #     VOICE_AVAILABLE = True
# # # # # except Exception:
# # # # #     VOICE_AVAILABLE = False

# # # # # # -----------------------
# # # # # # Config & small helpers
# # # # # # -----------------------
# # # # # os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # quieter logs

# # # # # st.set_page_config(page_title="AI Healthcare Assistant", page_icon="💊", layout="centered")

# # # # # # Small utility to safely play mp3 bytes in Streamlit
# # # # # def play_audio_bytes(audio_bytes):
# # # # #     b64 = base64.b64encode(audio_bytes).decode()
# # # # #     audio_html = f'<audio controls autoplay style="width:100%;">' \
# # # # #                  f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
# # # # #     st.markdown(audio_html, unsafe_allow_html=True)

# # # # # # -----------------------
# # # # # # Knowledge base
# # # # # # -----------------------
# # # # # # Expanded symptom knowledge with causes, remedies, red flags, followups
# # # # # SYMPTOM_DB = {
# # # # #     "dizziness": {
# # # # #         "aliases": ["dizzy", "lightheaded", "feeling faint", "vertigo"],
# # # # #         "causes": ["low blood pressure", "dehydration", "low blood sugar", "inner ear issues", "anemia"],
# # # # #         "remedies": [
# # # # #             "Sit or lie down immediately until the feeling passes.",
# # # # #             "Drink some water or an oral rehydration drink slowly.",
# # # # #             "Avoid sudden standing or head movements; stand up slowly."
# # # # #         ],
# # # # #         "red_flags": ["loss of consciousness", "chest pain", "severe headache", "sudden weakness"],
# # # # #         "follow_up": "When did the dizziness start and does anything make it better or worse?"
# # # # #     },
# # # # #     "headache": {
# # # # #         "aliases": ["head pain", "migraine", "pressure in head"],
# # # # #         "causes": ["dehydration", "stress", "eye strain", "lack of sleep", "sinus issues"],
# # # # #         "remedies": [
# # # # #             "Drink water, rest in a quiet/dark room, apply a cool compress.",
# # # # #             "Limit screen time and try gentle neck stretches."
# # # # #         ],
# # # # #         "red_flags": ["very sudden severe headache", "vision changes", "confusion", "stiff neck"],
# # # # #         "follow_up": "Is the pain on one side or both, and how would you rate intensity 1–10?"
# # # # #     },
# # # # #     "fever": {
# # # # #         "aliases": ["temperature", "hot", "feverish"],
# # # # #         "causes": ["infection (viral/bacterial)", "inflammatory condition"],
# # # # #         "remedies": [
# # # # #             "Stay hydrated, rest, use a cool compress.",
# # # # #             "Paracetamol/acetaminophen can be used according to instructions if needed."
# # # # #         ],
# # # # #         "red_flags": ["very high fever > 39°C (102°F)", "difficulty breathing", "confusion", "persistent vomiting"],
# # # # #         "follow_up": "Do you have measured temperature and for how long have you had fever?"
# # # # #     },
# # # # #     "cough": {
# # # # #         "aliases": ["coughing", "sore throat", "throat pain"],
# # # # #         "causes": ["common cold", "allergy", "throat irritation"],
# # # # #         "remedies": [
# # # # #             "Stay hydrated and try warm honey drink (if not diabetic and older than 1 year).",
# # # # #             "Steam inhalation and throat lozenges may help."
# # # # #         ],
# # # # #         "red_flags": ["blood in sputum", "breathlessness", "high fever", "worsening over days"],
# # # # #         "follow_up": "Is the cough dry or productive (with phlegm)? Any fever or breathlessness?"
# # # # #     },
# # # # #     "stomach pain": {
# # # # #         "aliases": ["stomachache", "abdomen pain", "belly pain", "gas", "indigestion"],
# # # # #         "causes": ["indigestion", "gas", "food poisoning"],
# # # # #         "remedies": [
# # # # #             "Drink warm water, avoid solid food for a few hours if vomiting, try ginger tea.",
# # # # #             "Eat light, bland food and avoid oily/spicy meals."
# # # # #         ],
# # # # #         "red_flags": ["severe constant pain", "blood in stool", "high fever", "inability to pass stool"],
# # # # #         "follow_up": "Where exactly is the pain and did you have any recent food or travel?"
# # # # #     },
# # # # #     "fatigue": {
# # # # #         "aliases": ["tired", "exhausted", "low energy", "sleepy"],
# # # # #         "causes": ["lack of sleep", "stress", "poor diet", "anemia"],
# # # # #         "remedies": [
# # # # #             "Try to get regular sleep, balanced meals, short walks and light exercise.",
# # # # #             "Consider checking iron levels if persistent."
# # # # #         ],
# # # # #         "red_flags": ["sudden severe fatigue", "shortness of breath", "chest pain"],
# # # # #         "follow_up": "How long have you felt fatigued and how is your sleep/diet lately?"
# # # # #     },
# # # # #     "nausea": {
# # # # #         "aliases": ["nauseous", "want to vomit", "queasy"],
# # # # #         "causes": ["stomach bug", "motion sickness", "medication side effect"],
# # # # #         "remedies": [
# # # # #             "Sip clear fluids, try ginger or peppermint, avoid strong smells and heavy foods.",
# # # # #             "Rest and breathe slowly until it eases."
# # # # #         ],
# # # # #         "red_flags": ["persistent vomiting", "blood in vomit", "severe dehydration"],
# # # # #         "follow_up": "Have you vomited? Any recent travel or new medications?"
# # # # #     },
# # # # # }

# # # # # # Generic fallback tips and safe reply templates
# # # # # GENERIC_TEMPLATES = [
# # # # #     "Thanks for telling me — based on what you said, here are some likely causes and steps you can try right now.",
# # # # #     "I understand — below are possible causes and simple steps you can safely try at home."
# # # # # ]

# # # # # # -----------------------
# # # # # # Symptom detection
# # # # # # -----------------------
# # # # # def detect_symptoms(text):
# # # # #     text_low = text.lower()
# # # # #     matches = []
# # # # #     for symptom, data in SYMPTOM_DB.items():
# # # # #         # check primary name and aliases
# # # # #         keywords = [symptom] + data.get("aliases", [])
# # # # #         if any(k in text_low for k in keywords):
# # # # #             matches.append(symptom)
# # # # #     return matches

# # # # # # -----------------------
# # # # # # Build response
# # # # # # -----------------------
# # # # # def build_response(user_text):
# # # # #     symptoms = detect_symptoms(user_text)
# # # # #     if symptoms:
# # # # #         # If multiple symptoms, handle first one prominently
# # # # #         primary = symptoms[0]
# # # # #         info = SYMPTOM_DB[primary]
# # # # #         cause = random.choice(info["causes"])
# # # # #         remedy_suggestions = info["remedies"]
# # # # #         remedy = random.choice(remedy_suggestions)
# # # # #         red_flags = info["red_flags"]
# # # # #         follow = info["follow_up"]

# # # # #         reply = []
# # # # #         reply.append(f"{random.choice(GENERIC_TEMPLATES)}")
# # # # #         reply.append(f"\n**Likely issue:** {primary.capitalize()}")
# # # # #         reply.append(f"\n**Possible cause (example):** {cause}")
# # # # #         reply.append(f"\n**Immediate self-care / remedies:**\n- {remedy}")
# # # # #         # add 1-2 more quick tips if available
# # # # #         for extra in remedy_suggestions:
# # # # #             if extra != remedy:
# # # # #                 reply.append(f"- {extra}")
# # # # #                 break
# # # # #         reply.append("\n**When to seek urgent care (red flags):**")
# # # # #         for rf in red_flags:
# # # # #             reply.append(f"- {rf}")
# # # # #         reply.append(f"\n**Quick question:** {follow}")
# # # # #         reply.append("\n(If your symptoms are severe or worsening, please contact a medical professional or emergency services.)")
# # # # #         return "\n".join(reply)
# # # # #     else:
# # # # #         # If nothing matched — be conversational and try to elicit more info
# # # # #         prompts = [
# # # # #             "I didn't catch a specific symptom. Could you describe how you're feeling in one or two sentences? (e.g., 'I have a throbbing headache' or 'I feel dizzy and shaky')",
# # # # #             "Can you tell me where it hurts or what sensation you feel? Examples: 'stomach pain', 'dizzy', 'sharp pain in chest' (if chest pain — seek emergency care)."
# # # # #         ]
# # # # #         return "I want to help — " + random.choice(prompts)

# # # # # # -----------------------
# # # # # # Voice helpers (optional)
# # # # # # -----------------------
# # # # # def voice_input():
# # # # #     if not VOICE_AVAILABLE:
# # # # #         st.warning("Voice features are not available because dependencies are missing. To enable, `pip install SpeechRecognition gTTS pyaudio` (Windows: use pipwin for pyaudio).")
# # # # #         return None
# # # # #     r = sr.Recognizer()
# # # # #     with sr.Microphone() as source:
# # # # #         st.info("Listening... please speak clearly (will timeout after ~6 seconds).")
# # # # #         try:
# # # # #             audio = r.listen(source, timeout=6)
# # # # #             text = r.recognize_google(audio)
# # # # #             return text
# # # # #         except sr.WaitTimeoutError:
# # # # #             st.warning("No speech detected (timeout).")
# # # # #         except sr.UnknownValueError:
# # # # #             st.error("Could not understand audio.")
# # # # #         except Exception as e:
# # # # #             st.error(f"Voice capture error: {e}")
# # # # #     return None

# # # # # def speak_text(text):
# # # # #     if not VOICE_AVAILABLE:
# # # # #         return
# # # # #     try:
# # # # #         tts = gTTS(text=text, lang="en")
# # # # #         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
# # # # #             tts.save(f.name)
# # # # #             audio_bytes = open(f.name, "rb").read()
# # # # #         play_audio_bytes(audio_bytes)
# # # # #     except Exception as e:
# # # # #         st.error(f"Audio playback error: {e}")

# # # # # # -----------------------
# # # # # # PDF export helper
# # # # # # -----------------------
# # # # # def create_chat_pdf(messages):
# # # # #     buffer = BytesIO()
# # # # #     c = canvas.Canvas(buffer, pagesize=letter)
# # # # #     text_obj = c.beginText(40, 750)
# # # # #     text_obj.setFont("Helvetica", 11)
# # # # #     for m in messages:
# # # # #         role = "You" if m["role"] == "user" else "Assistant"
# # # # #         lines = (f"{role}: {m['content']}").split("\n")
# # # # #         for line in lines:
# # # # #             # wrap manually at ~90 chars
# # # # #             for i in range(0, len(line), 90):
# # # # #                 text_obj.textLine(line[i:i+90])
# # # # #         text_obj.textLine("")
# # # # #     c.drawText(text_obj)
# # # # #     c.save()
# # # # #     pdf_bytes = buffer.getvalue()
# # # # #     buffer.close()
# # # # #     return pdf_bytes

# # # # # # -----------------------
# # # # # # UI: main app
# # # # # # -----------------------
# # # # # def main():
# # # # #     st.title("💊 AI Healthcare Assistant — Friendly, safe suggestions")
# # # # #     st.markdown("**Tell me how you're feeling.** I will try to identify likely issues, suggest safe home care, and tell you when to seek medical help.")
# # # # #     st.markdown("---")

# # # # #     # Health tip of the day
# # # # #     tips = [
# # # # #         "Drink at least 8 glasses of water daily.",
# # # # #         "Take short breaks every hour to stand and stretch when working.",
# # # # #         "Aim for 7–8 hours of sleep for better recovery and immunity.",
# # # # #         "Wash hands frequently to reduce infection risk.",
# # # # #         "Include fruits & vegetables for vitamins and minerals."
# # # # #     ]
# # # # #     tip = tips[datetime.datetime.now().day % len(tips)]
# # # # #     st.info(f"💡 Health Tip of the Day — {tip}")

# # # # #     # initialize session state
# # # # #     if "messages" not in st.session_state:
# # # # #         st.session_state.messages = []

# # # # #     # left column chat display
# # # # #     for msg in st.session_state.messages:
# # # # #         if msg["role"] == "user":
# # # # #             st.chat_message("user").write(msg["content"])
# # # # #         else:
# # # # #             st.chat_message("assistant").write(msg["content"])

# # # # #     # input area
# # # # #     col_txt, col_voice, col_pdf = st.columns([6,1,1])
# # # # #     with col_txt:
# # # # #         user_text = st.chat_input("Describe your symptom or ask a health question (e.g., 'I feel dizzy and weak')")

# # # # #     with col_voice:
# # # # #         voice_btn = st.button("🎙️ Voice") if VOICE_AVAILABLE else st.button("🎙️ (voice disabled)")

# # # # #     with col_pdf:
# # # # #         if st.button("💾 Download Chat PDF"):
# # # # #             if st.session_state.messages:
# # # # #                 pdf_bytes = create_chat_pdf(st.session_state.messages)
# # # # #                 st.download_button("Download conversation (PDF)", data=pdf_bytes, file_name="health_chat.pdf", mime="application/pdf")
# # # # #             else:
# # # # #                 st.warning("No conversation to download yet.")

# # # # #     # handle voice
# # # # #     if voice_btn:
# # # # #         vtext = voice_input()
# # # # #         if vtext:
# # # # #             st.session_state.messages.append({"role": "user", "content": vtext})
# # # # #             st.chat_message("user").write(vtext)
# # # # #             with st.spinner("Analyzing..."):
# # # # #                 response = build_response(vtext)
# # # # #             st.session_state.messages.append({"role": "assistant", "content": response})
# # # # #             st.chat_message("assistant").write(response)
# # # # #             # speak out
# # # # #             speak_text(response)

# # # # #     # handle typed input
# # # # #     if user_text:
# # # # #         st.session_state.messages.append({"role": "user", "content": user_text})
# # # # #         st.chat_message("user").write(user_text)
# # # # #         with st.spinner("Analyzing symptoms and preparing suggestions..."):
# # # # #             response = build_response(user_text)
# # # # #         st.session_state.messages.append({"role": "assistant", "content": response})
# # # # #         st.chat_message("assistant").write(response)
# # # # #         # speak out
# # # # #         speak_text(response)

# # # # #     st.markdown("---")
# # # # #     st.caption("⚕️ *This assistant provides general information and first-aid style self-care suggestions only. It is not a substitute for professional medical advice, diagnosis, or treatment. If you have severe symptoms or are in doubt, contact a healthcare professional or emergency services.*")

# # # # # if __name__ == "__main__":
# # # # #     main()
























# # # # import os
# # # # import streamlit as st
# # # # import openai
# # # # import random
# # # # import datetime
# # # # import tempfile
# # # # import base64
# # # # import pandas as pd
# # # # from io import BytesIO
# # # # from reportlab.lib.pagesizes import letter
# # # # from reportlab.pdfgen import canvas

# # # # # Optional voice deps
# # # # try:
# # # #     import speech_recognition as sr
# # # #     from gtts import gTTS
# # # #     VOICE_AVAILABLE = True
# # # # except Exception:
# # # #     VOICE_AVAILABLE = False


# # # # # -------------------- CONFIG --------------------
# # # # st.set_page_config(page_title="AI Healthcare Assistant", page_icon="💊", layout="centered")

# # # # st.markdown("""
# # # #     <style>
# # # #     .stChatMessage {font-size: 17px;}
# # # #     .stTextInput>div>div>input {font-size: 16px;}
# # # #     .assistant {background-color: #e8f4fa; border-radius: 15px; padding: 10px;}
# # # #     .user {background-color: #fce4ec; border-radius: 15px; padding: 10px;}
# # # #     </style>
# # # # """, unsafe_allow_html=True)

# # # # # Add your API key (optional)
# # # # openai.api_key = os.getenv("OPENAI_API_KEY", None)

# # # # # -------------------- DATABASE --------------------
# # # # SYMPTOM_DB = {
# # # #     "dizziness": {
# # # #         "aliases": ["dizzy", "lightheaded"],
# # # #         "causes": ["low blood pressure", "dehydration", "anemia"],
# # # #         "remedies": ["Sit or lie down, drink water, avoid standing suddenly."],
# # # #         "red_flags": ["fainting", "chest pain", "blurred vision"],
# # # #     },
# # # #     "headache": {
# # # #         "aliases": ["migraine", "head pain"],
# # # #         "causes": ["stress", "eye strain", "dehydration"],
# # # #         "remedies": ["Rest in dark room, drink water, gentle neck stretches."],
# # # #         "red_flags": ["vision loss", "vomiting", "stiff neck"],
# # # #     },
# # # #     "fever": {
# # # #         "aliases": ["temperature", "feverish"],
# # # #         "causes": ["infection", "cold", "flu"],
# # # #         "remedies": ["Stay hydrated, rest, use paracetamol if needed."],
# # # #         "red_flags": [">102°F", "persistent over 3 days", "confusion"],
# # # #     },
# # # #     "cough": {
# # # #         "aliases": ["sore throat", "cold"],
# # # #         "causes": ["infection", "allergy"],
# # # #         "remedies": ["Drink warm fluids, honey water, use lozenges."],
# # # #         "red_flags": ["breathing trouble", "blood in sputum"],
# # # #     },
# # # # }

# # # # # -------------------- CORE LOGIC --------------------
# # # # def detect_symptoms(text):
# # # #     text_low = text.lower()
# # # #     matches = []
# # # #     for symptom, data in SYMPTOM_DB.items():
# # # #         if any(word in text_low for word in [symptom] + data["aliases"]):
# # # #             matches.append(symptom)
# # # #     return matches


# # # # def get_health_response(user_input):
# # # #     symptoms = detect_symptoms(user_input)
# # # #     if symptoms:
# # # #         s = symptoms[0]
# # # #         data = SYMPTOM_DB[s]
# # # #         msg = f"🩺 You mentioned **{s}**.\n\nPossible cause: {random.choice(data['causes'])}\nRemedy: {random.choice(data['remedies'])}\n\n⚠️ Seek urgent care if: {', '.join(data['red_flags'])}"
# # # #         return msg
# # # #     else:
# # # #         return "Could you describe your symptom in more detail (e.g., 'I feel dizzy', 'I have a fever')?"


# # # # def ai_response(prompt):
# # # #     """Try OpenAI if available, else fallback to rule-based"""
# # # #     if openai.api_key:
# # # #         try:
# # # #             completion = openai.ChatCompletion.create(
# # # #                 model="gpt-3.5-turbo",
# # # #                 messages=[
# # # #                     {"role": "system", "content": "You are a friendly medical assistant. Provide helpful, polite advice."},
# # # #                     {"role": "user", "content": prompt},
# # # #                 ],
# # # #             )
# # # #             return completion.choices[0].message["content"]
# # # #         except Exception:
# # # #             pass
# # # #     return get_health_response(prompt)

# # # # # -------------------- PDF Export --------------------
# # # # def export_pdf(history):
# # # #     buf = BytesIO()
# # # #     c = canvas.Canvas(buf, pagesize=letter)
# # # #     text_obj = c.beginText(40, 750)
# # # #     text_obj.setFont("Helvetica", 11)
# # # #     for msg in history:
# # # #         role = "👩 You" if msg["role"] == "user" else "💊 Assistant"
# # # #         text_obj.textLine(f"{role}: {msg['content']}")
# # # #         text_obj.textLine("")
# # # #     c.drawText(text_obj)
# # # #     c.save()
# # # #     return buf.getvalue()


# # # # # -------------------- VOICE SUPPORT --------------------
# # # # def listen_voice():
# # # #     if not VOICE_AVAILABLE:
# # # #         st.warning("Voice features unavailable.")
# # # #         return None
# # # #     r = sr.Recognizer()
# # # #     with sr.Microphone() as source:
# # # #         st.info("🎤 Listening... speak now")
# # # #         audio = r.listen(source, timeout=5)
# # # #     try:
# # # #         return r.recognize_google(audio)
# # # #     except:
# # # #         st.error("Could not recognize speech.")
# # # #         return None


# # # # def speak(text):
# # # #     if not VOICE_AVAILABLE:
# # # #         return
# # # #     tts = gTTS(text)
# # # #     tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
# # # #     tts.save(tmp.name)
# # # #     audio_bytes = open(tmp.name, "rb").read()
# # # #     b64 = base64.b64encode(audio_bytes).decode()
# # # #     st.markdown(f'<audio autoplay controls src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)


# # # # # -------------------- APP INTERFACE --------------------
# # # # def main():
# # # #     st.title("💊 AI Healthcare Assistant")
# # # #     st.caption("Your friendly, intelligent health companion 💬")

# # # #     tip = random.choice([
# # # #         "Drink plenty of water today.",
# # # #         "Take short screen breaks every hour.",
# # # #         "Eat a balanced diet for steady energy.",
# # # #         "Sleep 7–8 hours to boost immunity.",
# # # #         "Wash your hands regularly."
# # # #     ])
# # # #     st.info(f"💡 Health Tip: {tip}")

# # # #     if "history" not in st.session_state:
# # # #         st.session_state.history = []

# # # #     for msg in st.session_state.history:
# # # #         role_class = "user" if msg["role"] == "user" else "assistant"
# # # #         st.markdown(f"<div class='{role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# # # #     col1, col2 = st.columns([6,1])
# # # #     with col1:
# # # #         user_input = st.chat_input("Describe your symptom (e.g. 'I feel dizzy')")
# # # #     with col2:
# # # #         voice_btn = st.button("🎙️ Voice")

# # # #     if voice_btn:
# # # #         voice_text = listen_voice()
# # # #         if voice_text:
# # # #             st.session_state.history.append({"role": "user", "content": voice_text})
# # # #             response = ai_response(voice_text)
# # # #             st.session_state.history.append({"role": "assistant", "content": response})
# # # #             st.experimental_rerun()

# # # #     if user_input:
# # # #         st.session_state.history.append({"role": "user", "content": user_input})
# # # #         response = ai_response(user_input)
# # # #         st.session_state.history.append({"role": "assistant", "content": response})
# # # #         speak(response)
# # # #         st.rerun()

# # # #     if st.button("💾 Download Chat as PDF"):
# # # #         if st.session_state.history:
# # # #             pdf_data = export_pdf(st.session_state.history)
# # # #             st.download_button("Download PDF", pdf_data, "health_chat.pdf", "application/pdf")

# # # #     st.markdown("---")
# # # #     st.caption("⚕️ *This assistant provides educational information only. For emergencies or serious conditions, please contact a medical professional.*")


# # # # if __name__ == "__main__":
# # # #     main()






















# # # import streamlit as st
# # # import google.generativeai as genai
# # # import os
# # # import tempfile
# # # import time
# # # from gtts import gTTS
# # # from io import BytesIO
# # # import speech_recognition as sr
# # # from dotenv import load_dotenv

# # # # =============================
# # # # 🚀 CONFIGURATION
# # # # =============================

# # # load_dotenv()
# # # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # # if not GEMINI_API_KEY:
# # #     st.error("🚨 Please add your GEMINI_API_KEY to the .env file.")
# # # else:
# # #     genai.configure(api_key=GEMINI_API_KEY)

# # # # =============================
# # # # 🌟 STREAMLIT PAGE SETTINGS
# # # # =============================
# # # st.set_page_config(page_title="AI Healthcare Assistant", page_icon="💊", layout="centered")

# # # # =============================
# # # # 🎨 PAGE HEADER
# # # # =============================
# # # st.title("💊 AI Healthcare Assistant")
# # # st.markdown("### Your intelligent, caring virtual health companion 🩺")
# # # st.markdown("💡 *Tip of the Day:* Take short breaks and drink water regularly to stay healthy!*")

# # # # =============================
# # # # 🧠 CHAT HISTORY
# # # # =============================
# # # if "chat_history" not in st.session_state:
# # #     st.session_state.chat_history = []

# # # # =============================
# # # # 🔊 TEXT-TO-SPEECH FUNCTION
# # # # =============================
# # # def speak_text(text):
# # #     tts = gTTS(text)
# # #     audio_fp = BytesIO()
# # #     tts.write_to_fp(audio_fp)
# # #     st.audio(audio_fp.getvalue(), format="audio/mp3")

# # # # =============================
# # # # 🎤 VOICE INPUT FUNCTION
# # # # =============================
# # # def listen_to_user():
# # #     recognizer = sr.Recognizer()
# # #     with sr.Microphone() as source:
# # #         st.info("🎙️ Listening... Please speak clearly.")
# # #         audio = recognizer.listen(source, phrase_time_limit=6)
# # #     try:
# # #         text = recognizer.recognize_google(audio)
# # #         st.success(f"🗣️ You said: {text}")
# # #         return text
# # #     except sr.UnknownValueError:
# # #         st.error("❌ Could not understand audio. Please try again.")
# # #         return None
# # #     except sr.RequestError:
# # #         st.error("⚠️ Network error while recognizing speech.")
# # #         return None

# # # # =============================
# # # # 🤖 GEMINI RESPONSE FUNCTION
# # # # =============================
# # # def get_health_response(user_input):
# # #     model = genai.GenerativeModel("models/gemini-2.5-flash")

# # #     system_prompt = (
# # #         "You are MedAI — a compassionate, trustworthy AI health assistant. "
# # #         "Analyze symptoms briefly and provide possible common causes (not diagnoses). "
# # #         "Offer simple, safe home remedies or self-care advice. "
# # #         "Always advise to see a doctor if the problem persists. "
# # #         "Be empathetic, professional, and clear."
# # #     )

# # #     conversation = "\n".join(
# # #         [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:]]
# # #     )

# # #     prompt = f"{system_prompt}\n\n{conversation}\nUser: {user_input}\nAssistant:"

# # #     response = model.generate_content(prompt)
# # #     return response.text.strip()

# # # # =============================
# # # # 💬 CHAT UI
# # # # =============================
# # # st.markdown("---")
# # # st.subheader("💬 Chat with your AI Health Assistant")

# # # col1, col2 = st.columns([4, 1])
# # # with col1:
# # #     user_input = st.text_input(
# # #         "Describe your symptom (e.g., 'I feel dizzy', 'I have a headache')",
# # #         key="symptom_input",
# # #         placeholder="Type or use voice input below..."
# # #     )
# # # with col2:
# # #     if st.button("🎤 Speak"):
# # #         spoken_text = listen_to_user()
# # #         if spoken_text:
# # #             st.session_state.chat_history.append({"role": "user", "content": spoken_text})
# # #             with st.spinner("Analyzing your symptoms... 🧠"):
# # #                 ai_response = get_health_response(spoken_text)
# # #             st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
# # #             speak_text(ai_response)
# # #             st.rerun()

# # # if st.button("Send"):
# # #     if user_input:
# # #         st.session_state.chat_history.append({"role": "user", "content": user_input})
# # #         with st.spinner("Analyzing your symptoms... 🧠"):
# # #             ai_response = get_health_response(user_input)
# # #         st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
# # #         speak_text(ai_response)
# # #         st.rerun()
# # #     else:
# # #         st.warning("⚠️ Please type or speak your symptom first.")

# # # # =============================
# # # # 📜 DISPLAY CHAT HISTORY
# # # # =============================
# # # st.markdown("---")
# # # for msg in st.session_state.chat_history:
# # #     if msg["role"] == "user":
# # #         st.markdown(f"🧍‍♀️ **You:** {msg['content']}")
# # #     else:
# # #         st.markdown(f"🤖 **Assistant:** {msg['content']}")

# # # # =============================
# # # # 💾 DOWNLOAD CHAT
# # # # =============================
# # # if st.session_state.chat_history:
# # #     if st.button("📥 Download Chat as TXT"):
# # #         chat_text = "\n".join(
# # #             [f"You: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
# # #              for m in st.session_state.chat_history]
# # #         )
# # #         with open("health_chat.txt", "w", encoding="utf-8") as f:
# # #             f.write(chat_text)
# # #         st.success("✅ Chat saved as `health_chat.txt` in your project folder.")

# # # # =============================
# # # # ⚠️ DISCLAIMER
# # # # =============================
# # # st.markdown("---")
# # # st.info(
# # #     "⚠️ **Disclaimer:** This AI provides general health information only. "
# # #     "It does *not* replace medical diagnosis or treatment. "
# # #     "Always consult a licensed healthcare provider for professional medical advice."
# # # )

















# # import streamlit as st
# # import google.generativeai as genai
# # import os
# # from io import BytesIO
# # from gtts import gTTS
# # import speech_recognition as sr
# # from dotenv import load_dotenv

# # # =====================================
# # # 🚀 CONFIGURATION
# # # =====================================
# # load_dotenv()
# # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # if not GEMINI_API_KEY:
# #     st.error("🚨 Please add your GEMINI_API_KEY to the .env file.")
# # else:
# #     genai.configure(api_key=GEMINI_API_KEY)

# # # =====================================
# # # 🌟 PAGE CONFIG
# # # =====================================
# # st.set_page_config(
# #     page_title="AI Healthcare Assistant",
# #     page_icon="💊",
# #     layout="centered",
# #     initial_sidebar_state="collapsed"
# # )

# # # =====================================
# # # 💅 CUSTOM CSS STYLING
# # # =====================================
# # st.markdown("""
# # <style>
# # /* Background and layout */
# # body, [class*="css"]  {
# #     background-color: #f6f8fc !important;
# #     font-family: 'Segoe UI', sans-serif !important;
# # }

# # /* Header */
# # h1 {
# #     color: #2c3e50 !important;
# #     text-align: center;
# #     font-weight: 700 !important;
# #     margin-bottom: 0 !important;
# # }

# # h3, h4 {
# #     color: #34495e !important;
# # }

# # /* Chat bubbles */
# # .user-bubble {
# #     background-color: #e8f4fd;
# #     padding: 10px 15px;
# #     border-radius: 15px;
# #     margin-bottom: 10px;
# #     color: #2c3e50;
# #     width: 80%;
# # }

# # .ai-bubble {
# #     background-color: #d6f5d6;
# #     padding: 10px 15px;
# #     border-radius: 15px;
# #     margin-bottom: 10px;
# #     margin-left: auto;
# #     color: #2c3e50;
# #     width: 80%;
# # }

# # /* Buttons */
# # div.stButton > button {
# #     background: linear-gradient(90deg, #1e90ff, #00bfff);
# #     color: white;
# #     border: none;
# #     border-radius: 10px;
# #     padding: 0.5rem 1rem;
# #     font-weight: 600;
# # }

# # div.stButton > button:hover {
# #     background: linear-gradient(90deg, #0077cc, #00aaff);
# # }

# # /* Footer disclaimer */
# # .footer {
# #     text-align: center;
# #     font-size: 0.9rem;
# #     color: #777;
# #     margin-top: 30px;
# # }
# # </style>
# # """, unsafe_allow_html=True)

# # # =====================================
# # # 🎨 PAGE HEADER
# # # =====================================
# # st.markdown("<h1>💊 AI Healthcare Assistant</h1>", unsafe_allow_html=True)
# # st.markdown("<h4 style='text-align:center;'>Your intelligent, caring virtual health companion 🩺</h4>", unsafe_allow_html=True)
# # st.markdown("<p style='text-align:center; color:gray;'>💡 Tip of the Day: Take short breaks and drink water regularly to stay healthy!</p>", unsafe_allow_html=True)
# # st.markdown("---")

# # # =====================================
# # # 🧠 CHAT HISTORY
# # # =====================================
# # if "chat_history" not in st.session_state:
# #     st.session_state.chat_history = []

# # # =====================================
# # # 🔊 TEXT-TO-SPEECH FUNCTION
# # # =====================================
# # def speak_text(text):
# #     tts = gTTS(text)
# #     audio_fp = BytesIO()
# #     tts.write_to_fp(audio_fp)
# #     st.audio(audio_fp.getvalue(), format="audio/mp3")

# # # =====================================
# # # 🎤 VOICE INPUT FUNCTION
# # # =====================================
# # def listen_to_user():
# #     recognizer = sr.Recognizer()
# #     with sr.Microphone() as source:
# #         st.info("🎙️ Listening... Please speak clearly.")
# #         audio = recognizer.listen(source, phrase_time_limit=6)
# #     try:
# #         text = recognizer.recognize_google(audio)
# #         st.success(f"🗣️ You said: {text}")
# #         return text
# #     except sr.UnknownValueError:
# #         st.error("❌ Could not understand audio. Please try again.")
# #         return None
# #     except sr.RequestError:
# #         st.error("⚠️ Network error while recognizing speech.")
# #         return None

# # # =====================================
# # # 🤖 GEMINI RESPONSE FUNCTION
# # # =====================================
# # def get_health_response(user_input):
# #     model = genai.GenerativeModel("models/gemini-2.5-flash")

# #     system_prompt = (
# #         "You are MedAI — a compassionate, trustworthy AI health assistant. "
# #         "Analyze symptoms briefly and provide possible common causes (not diagnoses). "
# #         "Offer simple, safe home remedies or self-care advice. "
# #         "Always advise to see a doctor if the problem persists. "
# #         "Be empathetic, professional, and clear."
# #     )

# #     conversation = "\n".join(
# #         [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:]]
# #     )

# #     prompt = f"{system_prompt}\n\n{conversation}\nUser: {user_input}\nAssistant:"
# #     response = model.generate_content(prompt)
# #     return response.text.strip()

# # # =====================================
# # # 💬 CHAT UI
# # # =====================================
# # st.subheader("💬 Chat with MedAI")

# # col1, col2 = st.columns([4, 1])
# # with col1:
# #     user_input = st.text_input(
# #         "Describe your symptom (e.g., 'I feel dizzy', 'I have a headache')",
# #         key="symptom_input",
# #         placeholder="Type or use voice input below..."
# #     )
# # with col2:
# #     if st.button("🎤 Speak"):
# #         spoken_text = listen_to_user()
# #         if spoken_text:
# #             st.session_state.chat_history.append({"role": "user", "content": spoken_text})
# #             with st.spinner("Analyzing your symptoms... 🧠"):
# #                 ai_response = get_health_response(spoken_text)
# #             st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
# #             speak_text(ai_response)
# #             st.rerun()

# # if st.button("Send"):
# #     if user_input:
# #         st.session_state.chat_history.append({"role": "user", "content": user_input})
# #         with st.spinner("Analyzing your symptoms... 🧠"):
# #             ai_response = get_health_response(user_input)
# #         st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
# #         speak_text(ai_response)
# #         st.rerun()
# #     else:
# #         st.warning("⚠️ Please type or speak your symptom first.")

# # # =====================================
# # # 🗨️ DISPLAY CHAT HISTORY
# # # =====================================
# # st.markdown("---")
# # for msg in st.session_state.chat_history:
# #     if msg["role"] == "user":
# #         st.markdown(f"<div class='user-bubble'>🧍‍♀️ <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
# #     else:
# #         st.markdown(f"<div class='ai-bubble'>🤖 <b>Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)

# # # =====================================
# # # 💾 DOWNLOAD CHAT
# # # =====================================
# # if st.session_state.chat_history:
# #     if st.button("📥 Download Chat as TXT"):
# #         chat_text = "\n".join(
# #             [f"You: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
# #              for m in st.session_state.chat_history]
# #         )
# #         with open("health_chat.txt", "w", encoding="utf-8") as f:
# #             f.write(chat_text)
# #         st.success("✅ Chat saved as `health_chat.txt` in your project folder.")

# # # =====================================
# # # ⚠️ DISCLAIMER
# # # =====================================
# # st.markdown("---")
# # st.markdown("""
# # <div class="footer">
# # ⚠️ <b>Disclaimer:</b> This AI provides general health information only.<br>
# # It does <i>not</i> replace professional medical diagnosis or treatment.<br>
# # Always consult a licensed healthcare provider for proper advice.
# # </div>
# # """, unsafe_allow_html=True)






# import streamlit as st
# import google.generativeai as genai
# import os
# from gtts import gTTS
# from io import BytesIO
# import speech_recognition as sr
# from dotenv import load_dotenv

# # =============================
# # 🚀 CONFIGURATION
# # =============================
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     st.error("🚨 Please add your GEMINI_API_KEY to the .env file.")
# else:
#     genai.configure(api_key=GEMINI_API_KEY)

# # =============================
# # 🌟 PAGE SETTINGS
# # =============================
# st.set_page_config(
#     page_title="AI Healthcare Assistant",
#     page_icon="💊",
#     layout="wide",
# )

# # =============================
# # 💅 CUSTOM CSS STYLING
# # =============================
# st.markdown("""
#     <style>
#         body {
#             font-family: 'Inter', sans-serif;
#         }
#         .main {
#             background-color: #0E1117;
#             color: white;
#         }
#         .sidebar .sidebar-content {
#             background-color: #F0F4FA !important;
#         }
#         .stButton>button {
#             background: linear-gradient(to right, #00B4DB, #0083B0);
#             color: white;
#             border: none;
#             border-radius: 10px;
#             padding: 8px 20px;
#             font-weight: 600;
#         }
#         .stButton>button:hover {
#             background: linear-gradient(to right, #0083B0, #00B4DB);
#             transform: scale(1.03);
#         }
#         .chat-bubble-user {
#             background-color: #0078D4;
#             color: white;
#             padding: 10px 15px;
#             border-radius: 15px;
#             margin: 5px 0;
#             width: fit-content;
#             max-width: 75%;
#         }
#         .chat-bubble-ai {
#             background-color: #262730;
#             color: #EDEDED;
#             padding: 10px 15px;
#             border-radius: 15px;
#             margin: 5px 0;
#             width: fit-content;
#             max-width: 75%;
#         }
#         footer {visibility: hidden;}
#     </style>
# """, unsafe_allow_html=True)

# # =============================
# # 🧠 CHAT HISTORY
# # =============================
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # =============================
# # 🔊 TEXT TO SPEECH
# # =============================
# def speak_text(text):
#     tts = gTTS(text)
#     audio_fp = BytesIO()
#     tts.write_to_fp(audio_fp)
#     st.audio(audio_fp.getvalue(), format="audio/mp3")

# # =============================
# # 🎤 VOICE INPUT
# # =============================
# def listen_to_user():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         st.info("🎙️ Listening... Please speak clearly.")
#         audio = recognizer.listen(source, phrase_time_limit=6)
#     try:
#         text = recognizer.recognize_google(audio)
#         st.success(f"🗣️ You said: {text}")
#         return text
#     except sr.UnknownValueError:
#         st.error("❌ Could not understand audio. Please try again.")
#         return None
#     except sr.RequestError:
#         st.error("⚠️ Network error while recognizing speech.")
#         return None

# # =============================
# # 🤖 AI RESPONSE
# # =============================
# def get_health_response(user_input):
#     model = genai.GenerativeModel("models/gemini-2.5-flash")

#     system_prompt = (
#         "You are MedAI — a compassionate AI health assistant. "
#         "Give concise, friendly guidance for common symptoms. "
#         "Mention possible causes, home remedies, and when to consult a doctor. "
#         "Avoid giving diagnoses. Be empathetic and human-like."
#     )

#     conversation = "\n".join(
#         [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:]]
#     )

#     prompt = f"{system_prompt}\n\n{conversation}\nUser: {user_input}\nAssistant:"
#     response = model.generate_content(prompt)
#     return response.text.strip()

# # =============================
# # 🧭 SIDEBAR
# # =============================
# with st.sidebar:
#     st.markdown("## 💡 Quick Health Tips")
#     tips = [
#         "Stay hydrated — aim for 8 glasses of water daily.",
#         "Take a 5-minute walk every hour during work.",
#         "Avoid screens 30 mins before bed.",
#         "Eat fruits and vegetables daily for immunity.",
#         "Practice mindful breathing for 2 minutes a day.",
#     ]
#     for tip in tips:
#         st.info(f"• {tip}")

#     st.markdown("## 🧍‍♀️ Recent Symptoms")
#     if st.session_state.chat_history:
#         symptoms = [m["content"] for m in st.session_state.chat_history if m["role"] == "user"]
#         for s in symptoms[-5:]:
#             st.write(f"🩺 {s}")
#     else:
#         st.write("No recent symptoms logged yet.")

#     st.markdown("## ℹ️ About MedAI")
#     st.caption("MedAI is your AI-powered health assistant built with Gemini AI. 💊")

# # =============================
# # 💬 MAIN CHAT AREA
# # =============================
# st.markdown("### 💊 AI Healthcare Assistant")
# st.markdown("#### Your intelligent, caring health companion 🩺")
# st.divider()

# st.subheader("💬 Chat with MedAI")

# col1, col2 = st.columns([4, 1])
# with col1:
#     user_input = st.text_input(
#         "Describe your symptom (e.g., 'I feel dizzy', 'I have a headache')",
#         key="symptom_input",
#         placeholder="Type or use voice input below..."
#     )
# with col2:
#     if st.button("🎤 Speak"):
#         spoken_text = listen_to_user()
#         if spoken_text:
#             st.session_state.chat_history.append({"role": "user", "content": spoken_text})
#             with st.spinner("Analyzing your symptoms... 🧠"):
#                 ai_response = get_health_response(spoken_text)
#             st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
#             speak_text(ai_response)
#             st.rerun()

# if st.button("Send"):
#     if user_input:
#         st.session_state.chat_history.append({"role": "user", "content": user_input})
#         with st.spinner("Analyzing your symptoms... 🧠"):
#             ai_response = get_health_response(user_input)
#         st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
#         speak_text(ai_response)
#         st.rerun()
#     else:
#         st.warning("⚠️ Please type or speak your symptom first.")

# st.divider()

# # =============================
# # 📜 DISPLAY CHAT
# # =============================
# for msg in st.session_state.chat_history:
#     if msg["role"] == "user":
#         st.markdown(f"<div class='chat-bubble-user'>🧍‍♀️ You: {msg['content']}</div>", unsafe_allow_html=True)
#     else:
#         st.markdown(f"<div class='chat-bubble-ai'>🤖 MedAI: {msg['content']}</div>", unsafe_allow_html=True)

# # =============================
# # 💾 DOWNLOAD CHAT
# # =============================
# if st.session_state.chat_history:
#     if st.download_button("📥 Download Chat", 
#                           "\n".join(
#                               [f"You: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
#                                for m in st.session_state.chat_history]
#                           ).encode("utf-8"),
#                           file_name="health_chat.txt"):
#         st.success("✅ Chat downloaded successfully!")

# # =============================
# # ⚠️ DISCLAIMER
# # =============================
# st.markdown("---")
# st.info(
#     "⚠️ **Disclaimer:** This AI provides general health information only. "
#     "It does *not* replace medical diagnosis or treatment. "
#     "Always consult a licensed healthcare provider for professional advice."
# )










import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime

# ====================================================
# 🔧 CONFIGURATION
# ====================================================
st.set_page_config(page_title="AI Healthcare Assistant", page_icon="💊", layout="wide")

# Load .env file (for local development)
# In Docker, environment variables are set by docker-compose
load_dotenv()

FIREBASE_KEY_PATH = "firebase_key.json"
GEMINI_MODEL = "gemini-2.5-flash"

# 👉 Read API key correctly from environment variables (set by docker-compose or .env)
# Priority: 1) Environment variable, 2) .env file (via load_dotenv)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Debug: Check if API key is loaded (only show in sidebar for debugging)
if not GEMINI_API_KEY:
    st.error("🚨 Gemini API key missing! Please add it to your .env file or set GEMINI_API_KEY environment variable.")
    st.info("💡 **Troubleshooting:**\n1. Create a `.env` file with `GEMINI_API_KEY=your_key`\n2. Or set environment variable before running Docker\n3. Restart the container after adding the key")
else:
    # Strip whitespace in case there are any spaces
    GEMINI_API_KEY = GEMINI_API_KEY.strip()
    if len(GEMINI_API_KEY) < 20:  # Basic validation - API keys are usually longer
        st.error(f"⚠️ API key seems too short. Please check your .env file.")
    else:
        genai.configure(api_key=GEMINI_API_KEY)

# ====================================================
# 🚀 INITIALIZE FIREBASE
# ====================================================
firebase_initialized = False
db = None

if os.path.exists(FIREBASE_KEY_PATH):
    try:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
    except Exception as e:
        st.error(f"🔥 Firebase initialization failed: {e}")
else:
    st.error("🚨 Missing firebase_key.json in project root.")

# ====================================================
# 🤖 INITIALIZE GEMINI
# ====================================================
try:
    ai_model = genai.GenerativeModel(GEMINI_MODEL)
except Exception as e:
    st.error(f"⚠️ Gemini initialization failed: {e}")
    ai_model = None

# ====================================================
# 🧠 SESSION STATE
# ====================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_page" not in st.session_state:
    st.session_state.active_page = "Chat"

# ====================================================
# 🎨 CUSTOM STYLES
# ====================================================
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        color: #6C63FF;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 30px;
    }
    .card {
        background-color: #f9f9ff;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(108, 99, 255, 0.2);
        margin-top: 20px;
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #6C63FF !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================
# 🔐 AUTHENTICATION HELPERS
# ====================================================
def signup(email, password, name):
    if firebase_initialized:
        try:
            user = auth.create_user(email=email, password=password, display_name=name)
            db.collection("users").document(user.uid).set({
                "email": email,
                "name": name,
                "created_at": datetime.now()
            })
            st.success(f"🎉 Account created for {user.email}")
        except Exception as e:
            st.error(f"⚠️ Signup failed: {e}")

def login(email):
    if firebase_initialized:
        try:
            user = auth.get_user_by_email(email)
            st.session_state.user = {
                "email": user.email,
                "uid": user.uid,
                "name": user.display_name or "User"
            }
            st.success(f"✅ Welcome back, {user.email}!")
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Login failed: {e}")

def update_profile(uid, name=None, password=None):
    try:
        auth.update_user(uid, display_name=name if name else None, password=password if password else None)
        if name:
            db.collection("users").document(uid).update({"name": name})
        st.success("✅ Profile updated successfully!")
    except Exception as e:
        st.error(f"⚠️ Update failed: {e}")

# ====================================================
# 🧭 SIDEBAR NAVIGATION
# ====================================================
with st.sidebar:
    st.markdown("## 💊 MedAI")
    if st.session_state.user:
        st.markdown(f"👤 **{st.session_state.user['name']}**")
        st.markdown(f"📧 {st.session_state.user['email']}")
        st.divider()
        page = st.radio("Navigate", ["💬 Chat", "🧠 Profile", "📜 History"])
        st.session_state.active_page = page
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.success("👋 Logged out successfully.")
            st.rerun()
    else:
        st.markdown("### 🔐 Please log in to access features.")

    st.markdown("---")
    st.markdown("### 💡 Health Tips")
    st.info("💧 Stay hydrated\n🥗 Eat fruits daily\n🧘 Do breathing exercises\n😴 Sleep 7+ hrs")

# ====================================================
# 🏥 MAIN UI
# ====================================================
st.markdown('<h1 class="main-title">AI Healthcare Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered personal health companion 🩺</p>', unsafe_allow_html=True)

# -------------------------
# LOGIN / SIGNUP
# -------------------------
if not st.session_state.user:
    tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Signup"])

    with tab_login:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔒 Password", type="password", key="login_password")
        if st.button("Login"):
            login(email)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_signup:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        name = st.text_input("👤 Full Name")
        signup_email = st.text_input("📧 Email", key="signup_email")
        signup_password = st.text_input("🔒 Password", type="password", key="signup_password")
        if st.button("Signup"):
            signup(signup_email, signup_password, name)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # -------------------------------------------
    # 💬 CHAT PAGE
    # -------------------------------------------
    if "Chat" in st.session_state.active_page:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Health Assistant")

        user_symptom = st.text_area(
            "Describe your health symptoms:",
            placeholder="e.g., I have been coughing for two days..."
        )

        if st.button("Ask AI Doctor 💬"):
            if not ai_model:
                st.error("⚠️ Gemini model not initialized.")
            elif user_symptom.strip():
                with st.spinner("Thinking... 💭"):
                    try:
                        response = ai_model.generate_content(
                            f"You are a friendly, professional medical assistant. "
                            f"The user says: {user_symptom}. Give a clear explanation, possible causes, "
                            f"home remedies, and recommend seeing a doctor if needed."
                        )
                        ai_reply = response.text

                        st.markdown("### 🩺 AI Response:")
                        st.write(ai_reply)

                        # Save history
                        st.session_state.chat_history.append({
                            "query": user_symptom,
                            "response": ai_reply,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })

                        if db:
                            db.collection("user_chats").add({
                                "user": st.session_state.user["email"],
                                "query": user_symptom,
                                "response": ai_reply,
                                "timestamp": datetime.now()
                            })

                    except Exception as e:
                        st.error(f"⚠️ AI Error: {e}")
            else:
                st.warning("Please enter your symptom first.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------
    # 🧠 PROFILE PAGE
    # -------------------------------------------
    elif "Profile" in st.session_state.active_page:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👤 Your Profile")

        name = st.text_input("Full Name", value=st.session_state.user["name"])
        new_password = st.text_input("New Password (optional)", type="password")

        if st.button("Update Profile"):
            update_profile(st.session_state.user["uid"], name, new_password)

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------
    # 📜 HISTORY PAGE
    # -------------------------------------------
    elif "History" in st.session_state.active_page:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🕒 Chat History")

        if db:
            chats = (
                db.collection("user_chats")
                .where("user", "==", st.session_state.user["email"])
                .stream()
            )
            for chat in chats:
                data = chat.to_dict()
                st.write(f"🗓️ **{data['timestamp'].strftime('%Y-%m-%d %H:%M')}** — {data['query']}")
                st.caption(data["response"])
                st.divider()
        else:
            st.caption("No chat history found.")

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("⚠️ Disclaimer: This AI provides educational info only — not a medical diagnosis or substitute for a doctor.")
