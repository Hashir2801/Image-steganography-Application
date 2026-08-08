import io
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Image Steganography App", page_icon="🖼️", layout="wide")

st.title("Image Steganography App")
st.caption("Hide a secret message inside an image or decode a previously encoded image.")

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    text = ""
    for char in chars:
        if len(char) < 8 or char == "00000000":
            break
        text += chr(int(char, 2))
    return text

def encode_message(image, secret_text):
    img = image.convert("RGB")
    arr = np.array(img)
    flat_arr = arr.flatten()
    binary_text = text_to_binary(secret_text) + "00000000"

    if len(binary_text) > len(flat_arr):
        raise ValueError("Message is too long for this image.")

    for i in range(len(binary_text)):
        flat_arr[i] = (flat_arr[i] & 254) | int(binary_text[i])

    encoded_arr = flat_arr.reshape(arr.shape)
    return Image.fromarray(encoded_arr.astype(np.uint8))

def decode_message(image):
    img = image.convert("RGB")
    arr = np.array(img).flatten()
    binary_data = ""

    for value in arr:
        binary_data += str(value & 1)
        if len(binary_data) >= 8 and binary_data[-8:] == "00000000":
            break

    return binary_to_text(binary_data)

encode_tab, decode_tab = st.tabs(["Encode Message", "Decode Message"])

with encode_tab:
    left, right = st.columns(2)
    with left:
        uploaded_image = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="encode_upload"
        )
        if uploaded_image is not None:
            source_image = Image.open(uploaded_image)
            st.image(source_image, caption=uploaded_image.name, use_column_width=True)

    with right:
        secret_text = st.text_area(
            "Secret Message",
            height=180,
            placeholder="Type the message you want to hide..."
        )

        if st.button("Encode Message", type="primary"):
            if uploaded_image is None:
                st.error("Please upload an image first.")
            elif not secret_text.strip():
                st.error("Please enter a secret message.")
            else:
                try:
                    encoded_image = encode_message(Image.open(uploaded_image), secret_text.strip())
                    buffer = io.BytesIO()
                    encoded_image.save(buffer, format="PNG")
                    buffer.seek(0)

                    st.success("Secret message encoded successfully.")
                    st.image(encoded_image, caption="Encoded Image", use_column_width=True)
                    st.download_button(
                        "Download Encoded Image",
                        data=buffer,
                        file_name="encoded_image.png",
                        mime="image/png"
                    )
                except ValueError as e:
                    st.error(str(e))

with decode_tab:
    left, right = st.columns(2)
    with left:
        encoded_upload = st.file_uploader(
            "Choose an encoded image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="decode_upload"
        )
        if encoded_upload is not None:
            decode_image = Image.open(encoded_upload)
            st.image(decode_image, caption=encoded_upload.name, use_column_width=True)

    with right:
        if st.button("Decode Message"):
            if encoded_upload is None:
                st.error("Please upload an encoded image first.")
            else:
                decoded_text = decode_message(Image.open(encoded_upload))
                if decoded_text:
                    st.success("Message decoded successfully.")
                    st.text_area("Decoded Message", value=decoded_text, height=180)
                else:
                    st.warning("No hidden message was found.")

st.divider()
st.caption("Built with Python, Streamlit, Pillow and NumPy.")