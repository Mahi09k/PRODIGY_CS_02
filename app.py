from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from PIL import Image
import os

def generate_key(key, size):
    """
    Custom key expansion algorithm to generate a key of the desired size.
    """
    key_len = len(key)
    expanded_key = [ord(char) for char in key]
    while len(expanded_key) < size:
        expanded_key.extend(expanded_key[:size - len(expanded_key)])
    return expanded_key[:size]

def encrypt_image(image_array, key):
    """
    Custom encryption algorithm using bitwise XOR and modular arithmetic.
    """
    key_array = np.array(generate_key(key, image_array.size), dtype=np.uint8)
    encrypted_array = np.bitwise_xor(image_array.flatten(), key_array)
    encrypted_image_array = encrypted_array.reshape(image_array.shape)
    return encrypted_image_array

def decrypt_image(image_array, key):
    """
    Custom decryption algorithm using bitwise XOR and modular arithmetic.
    """
    return encrypt_image(image_array, key)  # Decryption is the same as encryption

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENCRYPTED_FOLDER'] = 'static/encrypted'  # Save encrypted images in static folder
app.config['DECRYPTED_FOLDER'] = 'static/decrypted'  # Save decrypted images in static folder

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENCRYPTED_FOLDER'], exist_ok=True)
os.makedirs(app.config['DECRYPTED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)

    key = request.form['key']
    if not key:
        return redirect(request.url)

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        image = Image.open(filepath)
        image_array = np.array(image)

        if 'encrypt' in request.form:
            # Encrypt image
            encrypted_image_array = encrypt_image(image_array, key)
            encrypted_image = Image.fromarray(encrypted_image_array.astype('uint8'))
            encrypted_filename = 'encrypted_' + file.filename
            encrypted_filepath = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
            encrypted_image.save(encrypted_filepath)
            encrypted_image_url = url_for('static', filename='encrypted/' + encrypted_filename)
            return render_template('index.html', encrypted_image_url=encrypted_image_url)

        else:
            # Decrypt image
            decrypted_image_array = decrypt_image(image_array, key)
            decrypted_image = Image.fromarray(decrypted_image_array.astype('uint8'))
            decrypted_filename = 'decrypted_' + file.filename
            decrypted_filepath = os.path.join(app.config['DECRYPTED_FOLDER'], decrypted_filename)
            decrypted_image.save(decrypted_filepath)
            decrypted_image_url = url_for('static', filename='decrypted/' + decrypted_filename)
            return render_template('index.html', decrypted_image_url=decrypted_image_url)

    return redirect(request.url)

if __name__ == "__main__":
    app.run(debug=True)
