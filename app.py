import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")

# Streamlit page setup
st.title("Análisis de Imagen:🤖🏞️")

ke = st.text_input('Ingresa tu Clave', type="password")

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)

additional_details = ""
if show_details:
    # Text input for additional details about the image
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aquí:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if analyze_button:
    if not ke:
        st.warning("Por favor ingresa tu API key.")
    elif not uploaded_file:
        st.warning("Please upload an image.")
    else:
        with st.spinner("Analizando ..."):
            try:
                # Initialize OpenAI client safely after verifying API key exists
                client = OpenAI(api_key=ke)

                # Encode the image
                base64_image = encode_image(uploaded_file)
            
                prompt_text = "Describe what you see in the image in spanish"
            
                if show_details and additional_details:
                    prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            
                # Create the payload for the completion request
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]
            
                # Stream the response
                full_response = ""
                message_placeholder = st.empty()
                for completion in client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,   
                    max_tokens=1200,
                    stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                        
                message_placeholder.markdown(full_response)
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
