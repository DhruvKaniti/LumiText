import streamlit as st
from utils import chat_bubble, accessibility_helper_gemini,simplify_text , extract_text_from_image, describe_image, transcribe_audio_local, translate_text_gemini
from PIL import Image

##BACKGROUND COLOR FOR AI ASSISTANT

st.set_page_config(
    page_title="LumiText",
    layout="centered"
)

st.markdown(
    """
    <style>
    /* App background – subtle, not flashy */
    .stApp {
        background: linear-gradient(180deg, #f8fafc, #eef2ff);
        color: #0f172a;
    }

    /* Remove ALL card / block backgrounds */
    div[data-testid="stVerticalBlock"] > div {
        background: none !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 1.5rem;
    }

    /* Text areas */
    textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #c7d2fe !important;
        border-radius: 10px;
    }

    /* Inputs */
    input {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }

    /* Buttons – minimal */
    button {
        background-color: #ffffff !important;
        color: #of172a !important;
        border: 1px solid #c7d2fe !important;
        border-radius: 10px;
        font-weight: 500;
    }

    button:hover {
        border-color: #eef2ff !important;
        color: #6366f1 !important;
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
    }

    </style>
    """,
    unsafe_allow_html=True
)


## Header with UI MARKDOWN of LUMITEXT
st.markdown("""
<h1 style="text-align:center;">✨ LumiText</h1>
<p style="text-align:center; font-size:18px; color:gray;">
AI-powered accessibility assistant for text, images, and audio
</p>
<hr>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs([ "🌏 Gemini Language Translation","🤖 Gemini Accessibility Helper", "🖼️Image Description", "📄Extract Text", "🎤Speech to text"])


# Full Accessible using GEMINI API KEY

with tab1:
    st.header("🌏 Language Translation(Accessiblity Mode)")

    st.markdown(
        "Translate between **any language**. " 
        "The input language is detected automatically."
    )

    st.divider()
    
    ## Input
    text_to_translate = st.text_area(
        "Enter text in any Language",
        placeholder="Paste text here — language will be detected automatically",
        height=180
    )

    target_lang = st.text_input(
        "Translate to",
        placeholder= "English, Spanish, Hindi, Italian, French, Arabic..."
    )

    translate_clicked = st.button("Translate", use_container_width=True)

    if translate_clicked:
        if text_to_translate.strip() and target_lang.strip():
            with st.spinner("Detecting language and translating..."):
                result = translate_text_gemini(text_to_translate, target_lang)

            if "Detected Language:" in result:
                detected, translation = result.split("Translation:", 1)

                st.divider()

                st.caption(f"🌐 {detected.replace('Detected Language:', '').strip()}")

                st.markdown("### Translation")
                st.write(translation.strip())
            else:
                # fallback (just in case)
                st.write(result)

        else:
            st.warning("Please enter text and target lagnuage")



with tab2:
    st.header("Gemini Accessibility Helper")

    mode = st.radio("Select Accessbility Mode",
                    ["Text","Audio"])
    
    #--- Text---
    if mode == "Text":
        user_text = st.text_area("Enter text to make accessible")

        if st.button("Process Text",key="access_text"):
            if user_text.strip() != "":
                with st.spinner("Processing with Gemini..."):
                    accessible_output = accessibility_helper_gemini(user_text,mode="text")
                    chat_bubble(accessible_output,role="assistant")
            else:
                st.warning("Please enter some text")
    # --Audio Mode --
    elif mode =="Audio":
        audio_file = st.file_uploader("Upload audio for accessible transcript",type=["wav","mp3","m4a"],key="access_audio")
        if audio_file and st.button("Transcribe audio",key="access_audio_btn"):
            with st.spinner("Generating accessible transcript..."):
                transcript = transcribe_audio_local(audio_file)
                accessible_output = accessibility_helper_gemini(transcript,mode="audio")
                chat_bubble(accessible_output,role="assistant")


# -- Describe image through ollama -- Feature 2
with tab3: 
    st.header("🖼️ Image Description")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg","png","jpeg"], key="desc_file")


    if uploaded_file:
        if st.button("Describe image"):
            with st.spinner("Generating description..."):
                try: 
                    described_image = describe_image(uploaded_file)
                    st.subheader("Image Description")
                    st.write(described_image)
                except Exception as e:
                    st.error(f"Error describing image: {str(e)}")
            



# Extract text from Image - Feature 3
with tab4:

    uploaded_file = st.file_uploader("Upload an image", type=["jpg","png","jpeg"], key = "extract_file" )


    if uploaded_file:
        if st.button("Extract Text"):
            with st.spinner("Extracting text from image..."):
                text_from_image = extract_text_from_image(uploaded_file)
                st.subheader("EXTRACTED TEXT")
                st.write(text_from_image)

            with st.container():
                st.markdown(
                    """
                    <div style="background-color:#F0F8FF; padding:15px; border-radius:10px;">
                    <h4>Simplified Text:</h4>
                    <p>{}</p>
                    </div>
                    """.format(text_from_image),
                    unsafe_allow_html=True
                )
            
            if st.expander("Simplify Extracted Text?"):
                with st.spinner("Simplifying Extracted Text"):
                    simplifiedText = simplify_text(text_from_image)
                    st.subheader("Simplified Text: ")
                    st.write(simplifiedText)


#-- speech to text --Feature 4

with tab5:
    st.header("🎤 Speech To Text")

    audio_file = st.file_uploader("Upload audio", type=["wav","mp3","m4a"])

    if audio_file and st.button("Transcribe Audio"):
        with st.spinner("Transcribing..."):
            text = transcribe_audio_local(audio_file)
        st.subheader("Transcription Result")
        st.write(text)

