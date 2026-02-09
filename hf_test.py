import os
import google.generativeai as genai

genai.configure(api_key=" AIzaSyAgPtgN6TENj02qgeqNVWVnF4RkTbbrZDk")

models = genai.list_models()
print("Available Gemini models:")
for m in models:
    print(m.name)
