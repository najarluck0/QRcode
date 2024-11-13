from flask import Flask, render_template, request, send_file, url_for, redirect
import qrcode
import os
import re

app = Flask(__name__)

# Folder to store generated QR codes
QR_FOLDER = 'static/qr_codes'

# Ensure the folder exists
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

# Sanitize function for filenames
def sanitize_filename(data):
    # Replace invalid characters (e.g., :, *, ?, etc.) with underscores
    sanitized_data = re.sub(r'[\\/:*?"<>|]', '_', data)  # Replace any invalid characters
    return sanitized_data

def generate_qr_code(data, save_dir):
    # Sanitize the input data to create a valid file name
    sanitized_data = sanitize_filename(data)
    
    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Define the file path using sanitized data
    file_path = os.path.join(save_dir, f"{sanitized_data}.png")
    
    # Generate the QR code and save it
    img = qrcode.make(data)
    img.save(file_path)
    return file_path

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr_code_route():
    data = request.form['data']

    # Ensure data is not empty
    if not data:
        return redirect(url_for('index'))

    # Sanitize the URL or text data to ensure it's safe for use in filenames
    sanitized_data = sanitize_filename(data)

    # Generate the QR code with plain data (no encryption)
    qr = qrcode.QRCode(
        version=1,  # Version 1 is small but still readable
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (better for damaged codes)
        box_size=15,  # Smaller box size
        border=5,  # Smaller border around the QR code
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Define a file path for the QR code image
    qr_code_filename = f"{sanitized_data[:10]}_qr_code.png"  # Limit filename to first 10 sanitized characters
    qr_code_path = os.path.join(QR_FOLDER, qr_code_filename)

    # Save the QR code image to the static/qr_codes folder
    img.save(qr_code_path)

    # Pass the URL of the saved image back to the template
    qr_code_url = url_for('static', filename=f'qr_codes/{qr_code_filename}')
    return render_template('index.html', qr_code_url=qr_code_url, filename=qr_code_filename)

@app.route('/download', methods=['POST'])
def download_qr_code():
    filename = request.form['filename']
    qr_code_url = request.form['qr_code_url']
    
    # Extract the actual filename from the URL and create a path to it
    qr_code_path = qr_code_url.split('/qr_codes/')[-1]  # This should be a relative path only
    full_qr_code_path = os.path.join('static', 'qr_codes', qr_code_path)
    
    # If the filename provided by the user does not have .png, add it
    if not filename.endswith('.png'):
        filename += '.png'
    
    # Send the file with the name the user provided
    return send_file(full_qr_code_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
