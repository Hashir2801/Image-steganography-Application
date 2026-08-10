import io
import base64
import numpy as np
from flask import Flask, request, render_template_string, send_file
from PIL import Image

app = Flask(__name__)
LAST_ENCODED = None

def text_to_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binary_to_text(binary_data):
    raw = bytearray()
    for i in range(0, len(binary_data), 8):
        chunk = binary_data[i:i+8]
        if len(chunk) < 8 or chunk == '00000000':
            break
        raw.append(int(chunk, 2))
    return raw.decode('utf-8', errors='replace')

def encode_message(image, secret_text):
    img = image.convert('RGB')
    arr = np.array(img)
    flat_arr = arr.flatten()
    binary_text = text_to_binary(secret_text) + '00000000'
    if len(binary_text) > len(flat_arr):
        raise ValueError('Message is too long for this image.')
    for i, bit in enumerate(binary_text):
        flat_arr[i] = (int(flat_arr[i]) & 254) | int(bit)
    return Image.fromarray(flat_arr.reshape(arr.shape).astype(np.uint8))

def decode_message(image):
    arr = np.array(image.convert('RGB')).flatten()
    bits = []
    for value in arr:
        bits.append(str(int(value) & 1))
        if len(bits) >= 8 and ''.join(bits[-8:]) == '00000000':
            break
    return binary_to_text(''.join(bits))

HTML = '''
<!doctype html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Image Steganography App</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0e1117;color:#fafafa;font-family:Arial,sans-serif}
.wrap{max-width:1250px;margin:auto;padding:55px 24px}h1{font-size:42px;margin-bottom:12px}
.sub{color:#a8adb7;margin-bottom:35px}.tabs{display:flex;border-bottom:1px solid #30343d;margin-bottom:28px}
.tab{padding:12px 18px;color:#ddd;text-decoration:none}.active{color:#ff4b4b;border-bottom:2px solid #ff4b4b}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.card{background:#161a22;border:1px solid #292e39;border-radius:12px;padding:22px}
label{display:block;font-weight:bold;margin-bottom:10px}input,textarea{width:100%;background:#262a34;color:white;border:1px solid #3a404d;border-radius:8px;padding:13px}
textarea{height:180px}.btn{margin-top:16px;background:#ff4b4b;color:white;border:0;border-radius:8px;padding:12px 18px;font-weight:bold;cursor:pointer}
.preview{max-width:100%;max-height:430px;margin-top:18px;border-radius:8px}.msg{padding:12px;border-radius:8px;margin-bottom:18px}.ok{background:#173b2a}.err{background:#4b2227}
.decoded{white-space:pre-wrap;background:#262a34;padding:16px;border-radius:8px;min-height:120px}
footer{border-top:1px solid #30343d;margin-top:42px;padding-top:25px;color:#999}@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<h1>Image Steganography App</h1>
<div class="sub">Hide a secret message inside an image or decode a previously encoded image.</div>
<div class="tabs"><a class="tab {{ 'active' if tab=='encode' else '' }}" href="/">Encode Message</a><a class="tab {{ 'active' if tab=='decode' else '' }}" href="/decode">Decode Message</a></div>
{% if error %}<div class="msg err">{{ error }}</div>{% endif %}
{% if success %}<div class="msg ok">{{ success }}</div>{% endif %}
{% if tab=='encode' %}
<form method="post" enctype="multipart/form-data"><div class="grid">
<div class="card"><label>Choose an image</label><input type="file" name="image" accept=".png,.jpg,.jpeg,.bmp" required></div>
<div class="card"><label>Secret Message</label><textarea name="message" placeholder="Type the message you want to hide..." required></textarea><button class="btn">Encode Message</button></div>
</div></form>
{% if encoded_preview %}<div class="card" style="margin-top:28px"><label>Encoded Image</label><img class="preview" src="{{ encoded_preview }}"><br><a href="/download"><button class="btn">Download Encoded Image</button></a></div>{% endif %}
{% else %}
<form method="post" enctype="multipart/form-data"><div class="grid">
<div class="card"><label>Choose an encoded image</label><input type="file" name="image" accept=".png,.jpg,.jpeg,.bmp" required></div>
<div class="card"><label>Decoded Message</label><div class="decoded">{% if decoded_text is not none %}{{ decoded_text if decoded_text else 'No hidden message was found.' }}{% else %}Your decoded message will appear here.{% endif %}</div><button class="btn">Decode Message</button></div>
</div></form>
{% endif %}
<footer>Built with Python, Flask, Pillow and NumPy.</footer>
</div></body></html>
'''

@app.route('/', methods=['GET','POST'])
def home():
    global LAST_ENCODED
    error = success = preview = None
    if request.method == 'POST':
        f = request.files.get('image')
        message = request.form.get('message','').strip()
        if not f or not message:
            error = 'Please upload an image and enter a secret message.'
        else:
            try:
                encoded = encode_message(Image.open(f.stream), message)
                b = io.BytesIO()
                encoded.save(b, format='PNG')
                LAST_ENCODED = b.getvalue()
                preview = 'data:image/png;base64,' + base64.b64encode(LAST_ENCODED).decode('ascii')
                success = 'Secret message encoded successfully.'
            except Exception as e:
                error = str(e)
    return render_template_string(HTML, tab='encode', error=error, success=success, encoded_preview=preview, decoded_text=None)

@app.route('/decode', methods=['GET','POST'])
def decode():
    error = success = None
    decoded_text = None
    if request.method == 'POST':
        f = request.files.get('image')
        try:
            if not f:
                raise ValueError('Please upload an encoded image first.')
            decoded_text = decode_message(Image.open(f.stream))
            if decoded_text:
                success = 'Message decoded successfully.'
        except Exception as e:
            error = str(e)
    return render_template_string(HTML, tab='decode', error=error, success=success, encoded_preview=None, decoded_text=decoded_text)

@app.route('/download')
def download():
    if not LAST_ENCODED:
        return 'No encoded image is available. Encode an image first.', 404
    return send_file(io.BytesIO(LAST_ENCODED), mimetype='image/png', as_attachment=True, download_name='encoded_image.png')

if __name__ == '__main__':
    app.run(debug=True)
