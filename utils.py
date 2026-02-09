import ollama
import pytesseract
from PIL import Image
import base64 
import io
import speech_recognition as sr
from pydub import AudioSegment
import whisper
import tempfile
import os 
from dotenv import load_dotenv
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import google.generativeai as genai
import streamlit as st


gemini_api_key = st.secrets["gemini"]["api_key"]
if not gemini_api_key:
    raise ValueError("GEMINI API KEY not found!")

genai.configure(api_key = gemini_api_key)



processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
 
def simplify_text (text): 
    response = ollama.chat(model = "mistral:7b-instruct", messages = [{"role": "system" , "content": "You are a helpful assistant that simplifies text"},
                                                                  {"role": "user","content": text} ])
    
    return response.message.content

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

whisper_model = whisper.load_model("base")


def describe_image(img_file):
    """
    Takes a PIL image or uploaded file and returns a description string.
    """
    # Open image
    image = Image.open(img_file).convert("RGB")
    
    # Prepare input
    inputs = processor(images=image, return_tensors="pt")
    
    # Generate description
    out = blip_model.generate(**inputs)
    
    # Decode to string
    description = processor.decode(out[0], skip_special_tokens=True)
    return description


def save_uploaded_file(uploaded_file):
    ext = uploaded_file.name.split(".")[-1]
    temp_file = tempfile.NamedTemporaryFile(delete=False,suffix=f".{ext}")
    temp_file.write(uploaded_file.read())
    temp_file.close()
    return temp_file.name



def transcribe_audio_local(uploaded_file):
    file_path = save_uploaded_file(uploaded_file)
    try:
        result = whisper_model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"
    
def accessibility_helper_gemini(input_text, mode = "text"):
    """
    mode: "text" -> simplify text for accessibility
          "audio" -> generate transcript-friendly output
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = ""

    if mode == "text":
        prompt = f"Simplify the text for easy accessibility and screen readers. Output **only one paragraph**, short and clear. Do **not** include explanations, options: \n{input_text}"
    elif mode == "audio":
        prompt = f"Provide a clean transcript suitable for accessibility readers: \n {input_text}"
    else:
        prompt = input_text
        
    response = model.generate_content(prompt)
    return response.text
    

def chat_bubble (text,role="assistant"):
    """
    role: "assistant" = AI Output (left)
          "user" = user input (right)
    """
    if role == "assistant":
        color = "#EED6D6"
        text_color = "#000000"
        align = "left"
    elif role == "user":
        color = "#4b0082"
        text_color = "#FFF1F1"
        align = "right"
    else:  # fallback if role is invalid
        color = "#CCCCCC"
        text_color = "#000000"
        align = "left"


    st.markdown(
        f"""<div style="
            background-color:{color};
            color:{text_color};
            padding:12px 15px;
            border-radius:15px;
            max-width:80%;
            margin-bottom:10px;
            text-align:{align};
            ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def translate_text_gemini(text, target_lang):


    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are an accessibility-focused translator.

    1. Automatically detect the language of the input text.
    2. Translate it into {target_lang}.
    3. Preserve meaning and clarity.
    4. Output ONLY the translated text.
    5. Do NOT explain anything.
    6. Return the result in Exactly this format: 

    Detected Language: <language name>
    Translation:
    <translated text>

    Do NOT add anything else.
    

    Text: 
    {text}
"""
    response = model.generate_content(prompt)
    return response.text.strip()