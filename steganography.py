<<<<<<< HEAD
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
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography App")
        self.root.geometry("900x600")
        self.root.configure(bg="#eef4ff")

        self.image_path = None
        self.preview_image = None

        title = tk.Label(
            root,
            text="Image Steganography App",
            font=("Arial", 20, "bold"),
            bg="#eef4ff",
            fg="#1f3c88"
        )
        title.pack(pady=15)

        main_frame = tk.Frame(root, bg="#eef4ff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            left_frame,
            text="Selected Image",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1f3c88"
        ).pack(pady=10)

        self.image_label = tk.Label(left_frame, bg="white")
        self.image_label.pack(pady=10)

        self.image_name_label = tk.Label(
            left_frame,
            text="No image selected",
            bg="white",
            fg="gray",
            font=("Arial", 10)
        )
        self.image_name_label.pack(pady=5)

        tk.Button(
            left_frame,
            text="Choose Image",
            font=("Arial", 11, "bold"),
            bg="#4a90e2",
            fg="white",
            width=18,
            command=self.load_image
        ).pack(pady=10)

        tk.Label(
            right_frame,
            text="Secret Message",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1f3c88"
        ).pack(pady=10)

        self.text_box = tk.Text(
            right_frame,
            height=10,
            width=40,
            font=("Arial", 11),
            bd=1,
            relief="solid",
            wrap="word"
        )
        self.text_box.pack(pady=10, padx=15)

        button_frame = tk.Frame(right_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Encode Message",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            width=16,
            command=self.encode_message
        ).grid(row=0, column=0, padx=8, pady=5)

        tk.Button(
            button_frame,
            text="Decode Message",
            font=("Arial", 11, "bold"),
            bg="#f39c12",
            fg="white",
            width=16,
            command=self.decode_message
        ).grid(row=0, column=1, padx=8, pady=5)

        tk.Button(
            button_frame,
            text="Clear",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            width=16,
            command=self.clear_all
        ).grid(row=1, column=0, columnspan=2, pady=8)

        self.status_label = tk.Label(
            right_frame,
            text="Ready",
            bg="white",
            fg="green",
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(pady=15)

    def text_to_binary(self, text):
        return ''.join(format(ord(char), '08b') for char in text)

    def binary_to_text(self, binary_data):
        chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        text = ""
        for char in chars:
            if char == "00000000":
                break
            text += chr(int(char, 2))
        return text

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not path:
            return

        self.image_path = path
        self.image_name_label.config(text=os.path.basename(path))

        img = Image.open(path)
        img.thumbnail((350, 300))
        self.preview_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.preview_image)
        self.status_label.config(text="Image loaded successfully", fg="green")

    def encode_message(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return

        secret_text = self.text_box.get("1.0", tk.END).strip()
        if not secret_text:
            messagebox.showerror("Error", "Please enter a secret message.")
            return

        img = Image.open(self.image_path).convert("RGB")
        arr = np.array(img)
        flat_arr = arr.flatten()

        binary_text = self.text_to_binary(secret_text) + "00000000"

        if len(binary_text) > len(flat_arr):
            messagebox.showerror("Error", "Message is too long for this image.")
            return

        for i in range(len(binary_text)):
            flat_arr[i] = (flat_arr[i] & 254) | int(binary_text[i])

        encoded_arr = flat_arr.reshape(arr.shape)
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")]
        )

        if not output_path:
            return

        Image.fromarray(encoded_arr.astype(np.uint8)).save(output_path)
        self.status_label.config(text="Message encoded and image saved", fg="#2e8b57")
        messagebox.showinfo("Success", "Secret message encoded successfully.")

    def decode_message(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an encoded image first.")
            return

        img = Image.open(self.image_path).convert("RGB")
        arr = np.array(img).flatten()

        binary_data = ""
        for value in arr:
            binary_data += str(value & 1)

        secret_message = self.binary_to_text(binary_data)

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, secret_message)

        self.status_label.config(text="Message decoded successfully", fg="#d68910")
        messagebox.showinfo("Decoded Message", secret_message if secret_message else "No hidden message found.")

    def clear_all(self):
        self.image_path = None
        self.preview_image = None
        self.image_label.config(image="")
        self.image_name_label.config(text="No image selected")
        self.text_box.delete("1.0", tk.END)
        self.status_label.config(text="Cleared", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
>>>>>>> d7c326667d370e928cdbf131de5ec7ffa6b54133
