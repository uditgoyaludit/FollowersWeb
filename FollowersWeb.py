from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Folder to save the uploaded files
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

@app.route('/', methods=['POST'])
def upload_file():
    try:
        # Retrieve the file content from the request body
        file_content = request.get_data()
        filename = request.headers.get('X-Filename', 'uploaded_file')  # Use the filename header or a default
        
        if not filename:
            return jsonify({'error': 'No filename provided in the request header.'}), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file in chunks as received
        with open(file_path, 'wb') as f:  # Append to the file if it already exists
            f.write(file_content)

        return jsonify({'message': f'File {filename} uploaded successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
