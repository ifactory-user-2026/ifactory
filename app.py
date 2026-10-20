import os
import random
import requests
import uuid
import streamlit as st
from openai import OpenAI
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# ==========================================
# 🔐 СИСТЕМА БЕЗПЕКИ ТА АВТЕНТИФІКАЦІЇ
# ==========================================
st.set_page_config(page_title="Приватна ШІ-Фабрика", page_icon="🔒", layout="centered")

st.sidebar.title("🔒 Доступ обмежено")
password = st.sidebar.text_input("Введіть пароль розробника:", type="password")

if password != "Гриби2026":
    st.warning("Будь ласка, введіть правильний пароль у бічному меню для доступу до ШІ-Фабрики.")
    st.stop()

# Генеруємо унікальний ID для цієї сесії, щоб уникнути конфліктів імен файлів
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]


# ==========================================
# 1. ЗАГАЛЬНІ НАЛАШТУВАННЯ ТА ІНТЕРФЕЙС
# ==========================================
st.title("🎬 Мультимовна ШІ-Фабрика & Продюсер")
st.write("Автоматизація контенту «під ключ» та маркетинг для YouTube, Instagram, Facebook та TikTok!")

api_key = st.text_input("Введіть свій OpenAI API Key:", type="password")
eleven_key = st.text_input("Введіть свій ElevenLabs API Key:", type="password")
pexels_key = st.text_input("Введіть свій Pexels API Key:", type="password")

st.subheader("🌐 Налаштування мови проєкту")
lang = st.selectbox("Оберіть мову для контенту:", ["Українська 🇺🇦", "Polski 🇵🇱", "English 🇬🇧"])

mode = st.radio("Оберіть режим роботи:", [
    "🎬 Авто-монтаж довгого відео", 
    "💬 Відповідь на коментар",
    "📈 ШІ-Продюсер та Маркетинг (Вірусне просування)"
])

if lang == "Українська 🇺🇦":
    target_lang = "українською мовою"
    voice_id = "21m00Tcm4TlvDq8ikWAM" 
    disclaimer = "⚠️ *Матеріал має загальний інформаційний характер.*"
    caption_template = "🎬 Нове відео на тему:"
    caption_sub = "Дивіться до кінця, підписуйтесь! 👇"
elif lang == "Polski 🇵🇱":
    target_lang = "w języku polskim"
    voice_id = "pNInz6obpgfrhhZuoCwC" 
    disclaimer = "⚠️ *Materiał ma charakter wyłącznie informacyjny.*"
    caption_template = "🎬 Nowy film na temat:"
    caption_sub = "Oglądaj до кінця, subskrybuj! 👇"
else:
    target_lang = "in English language"
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    disclaimer = "⚠️ *This material is for general informational purposes only.*"
    caption_template = "🎬 New video about:"
    caption_sub = "Watch until the end, subscribe! 👇"


# ==========================================
# 🎬 РЕЖИМ 1: АВТО-МОНТАЖ ВІДЕО
# ==========================================
if mode == "🎬 Авто-монтаж довгого відео":
    st.subheader("🎬 Налаштування роликів")
    
    topic = st.selectbox("Оберіть тему контенту:", ["Здорове харчування", "Екотуризм", "Жива природа", "Спорт", "Сон", "Гумор та меми"])
    user_prompt = st.text_input("Головна ідея випуску: (Наприклад: Смішний міф про те, що від грибів худнуть за день)")
    
    video_duration = st.slider("Тривалість відео (в секундах):", 10, 90, 30)
    
    video_variant = st.radio("Оберіть варіант створення:", [
        "🎙️ З голосом диктора (Повний продакшен ElevenLabs)", 
        "🔇 Без голосу (Тільки відеоряд під трендову музику / меми)"
    ])
        if st.button("✨ Змонтувати ролик"):
        need_eleven = "🎙️ З голосом" in video_variant
        
        if not api_key or not pexels_key or (need_eleven and not eleven_key):
            st.error("Будь ласка, введіть необхідні API ключі для обраного варіанту!")
        elif not user_prompt:
            st.error("Вкажіть ідею для випуску!")
        else:
            s_id = st.session_state.session_id
            voice_file = f"voice_{s_id}.mp3"
            output_file = f"final_{s_id}.mp4"
            
            with st.spinner("🤖 ШІ створює ваш варіант відео..."):
                try:
                    client = OpenAI(api_key=api_key)
                    
                    style_note = "Пиши короткими смішними репліками-мемами." if "Гумор" in topic or not need_eleven else "Харизматичний розмовний стиль експерта."
                    
                    system_instruction = (
                        f"Ти — креативний ШІ-продюсер. Напиши текст для ролика тривалістю {video_duration} секунд. {style_note} "
                        f"Формат відповіді СУВОРЯ такий (два блоки через три знаки плюс '+++'):\n"
                        f"БЛОК 1: Текст контенту {target_lang}.\n"
                        f"+++\n"
                        f"БЛОК 2: Одне англійське слово для пошуку фонового відео на Pexels (наприклад, 'mushrooms', 'climbing', 'funny cat')."
                    )
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"Тема: {topic}. Ідея: {user_prompt}"}
                        ]
                    )
                    
                    # 1. Парсинг відповіді ШІ
                    ai_content = response.choices.message.content
                    if "+++" in ai_content:
                        script_text, pexels_query = ai_content.split("+++", 1)
                        script_text = script_text.replace("БЛОК 1:", "").strip()
                        pexels_query = pexels_query.replace("БЛОК 2:", "").strip().replace("'", "").replace('"', '')
                    else:
                        script_text = ai_content
                        pexels_query = "nature"

                    st.write(f"📝 **Текст:** {script_text}")
                    st.write(f"🔍 **Тег Pexels:** `{pexels_query}`")

                    # 2. ElevenLabs Озвучка
                    if need_eleven:
                        st.text("🎙️ Записуємо голос диктора...")
                        tts_url = f"https://elevenlabs.io{voice_id}"
                        headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
                        data = {"text": script_text, "model_id": "eleven_multilingual_v2"}
                        tts_res = requests.post(tts_url, json=data, headers=headers)
                        if tts_res.status_code == 200:
                            with open(voice_file, "wb") as f:
                                f.write(tts_res.content)
                        else:
                            st.error(f"Помилка ElevenLabs: {tts_res.text}")
                            st.stop()

                    # 3. Pexels Завантаження відео
                    st.text("🎥 Шукаємо відповідні відеокліпи...")
                    pexels_url = f"https://pexels.com{pexels_query}&per_page=3&orientation=portrait"
                    p_res = requests.get(pexels_url, headers={"Authorization": pexels_key}).json()

                    downloaded_clips = []
                    if "videos" in p_res and len(p_res["videos"]) > 0:
                        for idx, v_data in enumerate(p_res["videos"]):
                            video_files = v_data.get("video_files", [])
                            video_url = next((f["link"] for f in video_files if f["file_type"] == "video/mp4"), None)
                            if video_url:
                                c_name = f"clip_{idx}_{s_id}.mp4"
                                v_res = requests.get(video_url)
                                with open(c_name, "wb") as f:
                                    f.write(v_res.content)
                                downloaded_clips.append(c_name)
                    else:
                        st.error("Не знайдено відео на Pexels за цим запитом.")
                        st.stop()

                    # 4. Монтаж відео
                    st.text("🎬 Зшиваємо та монтуємо відео...")
                    video_objects = []
                    duration_per_clip = video_duration / max(len(downloaded_clips), 1)

                    for c in downloaded_clips:
                        if os.path.exists(c):
                            clip = VideoFileClip(c)
                            clip_duration = min(clip.duration, duration_per_clip)
                            trimmed = clip.subclip(0, clip_duration).copy() 
                            video_objects.append(trimmed)
                            clip.close()  # Безпечно звільняємо файли для хмари

                    if video_objects:
                        final_video = concatenate_videoclips(video_objects, method="compose")
                        
                        # Спочатку підганяємо тривалість відеоряду, потім накладаємо звук
                        if need_eleven and os.path.exists(voice_file):
                            audio = AudioFileClip(voice_file)
                            if final_video.duration > audio.duration:
                                final_video = final_video.subclip(0, audio.duration)
                            final_video = final_video.set_audio(audio)
                        else:
                            final_video = final_video.subclip(0, min(final_video.duration, video_duration))

                        # Рендеринг фінального файлу
                        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
                        
                        # Звільняємо всі ресурси з пам'яті комп'ютера/сервера
                        if need_eleven and 'audio' in locals():
                            audio.close()
                        final_video.close()
                        for v_obj in video_objects:
                            v_obj.close()

                        st.success("🎉 Готово!")
                        st.video(output_file)

                        # Очищення тимчасових завантажених кліпів
                        for c in downloaded_clips:
                            try: os.remove(c)
                            except: pass
                    else:
                        st.error("Не вдалося обробити відеофайли.")

                except Exception as e:
                    st.error(f"💥 Помилка під час створення: {e}")

elif mode == "💬 Відповідь на коментар":
    st.subheader("💬 Авто-відповідь на коментарі")
    st.info("Режим у розробці.")

elif mode == "📈 ШІ-Продюсер та Маркетинг (Вірусне просування)":
    st.subheader("📈 Маркетингова стратегія")
    st.info("Режим у розробці.")

    
