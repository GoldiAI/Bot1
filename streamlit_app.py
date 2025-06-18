import streamlit as st
import openai
import base64

openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="בוט הדמיה מבוסס השראה", layout="wide")
st.title("🎨 הדמיה אוטומטית על בסיס לוח השראה + חלל")

col1, col2 = st.columns(2)
with col1:
    inspiration_file = st.file_uploader("לוח השראה (תמונה)", type=["jpg", "jpeg", "png"])
with col2:
    room_file = st.file_uploader("תמונה של החלל או תוכנית", type=["jpg", "jpeg", "png"])

notes = st.text_area("הערות מיוחדות (אופציונלי)")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

if st.button("🎬 צור הדמיה") and inspiration_file and room_file:
    with st.spinner("מריץ GPT..."):
        inspiration_encoded = encode_image(inspiration_file)
        room_encoded = encode_image(room_file)

        prompt_response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are a professional interior designer who writes prompts for DALL·E."},
                {"role": "user", "content": [
                    {"type": "text", "text": f"""You received two images. The first is a moodboard with style, colors and materials. 
The second is either a photo or a plan of the space. Write a detailed DALL·E prompt that combines the two. Notes: {notes or 'none'}."""},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{inspiration_encoded}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{room_encoded}"}}
                ]}
            ],
            max_tokens=1000
        )

        dalle_prompt = prompt_response.choices[0].message.content
        st.markdown("✅ פרומפט שנוצר:")
        st.code(dalle_prompt)

        with st.spinner("יוצר תמונה ב-DALL·E..."):
            image_response = openai.Image.create(
                model="dall-e-3",
                prompt=dalle_prompt,
                n=1,
                size="1024x1024",
                response_format="url"
            )
            image_url = image_response["data"][0]["url"]
            st.image(image_url, caption="הדמיה סופית", use_column_width=True)
