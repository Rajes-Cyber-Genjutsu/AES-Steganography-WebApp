from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from encode import encode_message, convert_to_png
from decode import decode_message

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'steganography_secret'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        flash("No image uploaded!", "error")
        return redirect(url_for('index'))
    
    image = request.files['image']
    message = request.form['message']
    password = request.form['password']

    if image.filename == '':
        flash("No selected file!", "error")
        return redirect(url_for('index'))
    
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(img_path)

    # Convert JPG to PNG
    img_path = convert_to_png(img_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "encoded_" + os.path.basename(img_path))
    encode_message(img_path, output_path, message, password)

    return send_file(output_path, as_attachment=True)

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        flash("No image uploaded!", "error")
        return redirect(url_for('index'))

    image = request.files['image']
    password = request.form['password']

    if image.filename == '':
        flash("No selected file!", "error")
        return redirect(url_for('index'))

    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(img_path)

    # Removed convert_to_png(img_path) ✅ No JPG-to-PNG conversion
    decrypted_message = decode_message(img_path, password)
    
    if decrypted_message is None:
        flash("Incorrect password or no hidden message found!", "error")
        return redirect(url_for('index'))

    flash(f"✅ Decoded Message: {decrypted_message}", "success")
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
