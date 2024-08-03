import logging
import os
import tempfile
from flask import Flask, request, render_template, redirect, url_for, session, send_file
from google.cloud import storage

app = Flask(__name__)

# Secret key from environment variable, with fallback for local development
app.secret_key = os.environ.get('SECRET_KEY') or 'a9b8c7d6e5f4a3b2c1d0e9f8d7c6b5a4'

# User credentials (Ideally, fetch from a secure database)
users = {'Venki': 'venk@123', 'prem': 'venky@12345', 'theja': 'sunny@6163'}

# Google Cloud Storage configuration
bucket_name = "caps-ven"  # Replace with your actual bucket name

# Function to list blobs with a given prefix
def list_blobs_with_prefix(bucket_name, prefix):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    return blobs

# Routes for login/authentication
@app.route('/')
def login():
    try:
        return render_template('login.html')
    except Exception as e:
        app.logger.error(f"Error in login route: {e}")
        return "An error occurred", 500

@app.route('/login', methods=['POST'])
def do_login():
    try:
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('bucket'))
        else:
            return 'Invalid credentials'
    except Exception as e:
        app.logger.error(f"Error in do_login route: {e}")
        return "An error occurred", 500

# Routes for bucket/folder listing
@app.route('/bucket')
def bucket():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        blobs = list_blobs_with_prefix(bucket_name, '')
        return render_template('bucket.html', blobs=blobs)
    except Exception as e:
        app.logger.error(f"Error in bucket route: {e}")
        return "An error occurred", 500

@app.route('/folder/<path:folder_name>')
def folder(folder_name):
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        blobs = list_blobs_with_prefix(bucket_name, folder_name)
        return render_template('folder.html', blobs=blobs, folder_name=folder_name)
    except Exception as e:
        app.logger.error(f"Error in folder route: {e}")
        return "An error occurred", 500

# Secure file download route
@app.route('/download/<path:blob_name>')
def download(blob_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file_path = temp_file.name
            blob.download_to_filename(file_path)

        # Send the file to the user
        response = send_file(file_path, as_attachment=True, download_name=blob.name)

        # Cleanup the temporary file
        os.remove(file_path)
        return response
    except Exception as e:
        app.logger.error(f"Error in download route: {e}")
        return "An error occurred", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 
