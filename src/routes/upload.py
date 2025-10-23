from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import os
import uuid
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Directory to store uploaded images
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload/image', methods=['POST'])
@jwt_required()
def upload_image():
    """Upload an image (base64 or file upload)"""
    user_id = int(get_jwt_identity())
    
    # Check if base64 data
    if request.is_json:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        try:
            # Decode base64 image
            image_data = data['image']
            
            # Remove data:image/...;base64, prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Generate unique filename
            file_extension = data.get('extension', 'jpg')
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            # Return URL
            image_url = f"/uploads/{filename}"
            
            return jsonify({
                'message': 'Image uploaded successfully',
                'image_url': image_url
            }), 201
            
        except Exception as e:
            return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500
    
    # Check if file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        # Generate unique filename
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Return URL
        image_url = f"/uploads/{filename}"
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image_url': image_url
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500

@upload_bp.route('/upload/images', methods=['POST'])
@jwt_required()
def upload_multiple_images():
    """Upload multiple images at once"""
    user_id = int(get_jwt_identity())
    
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400
    
    # Limit to 5 images
    if len(files) > 5:
        return jsonify({'error': 'Maximum 5 images allowed'}), 400
    
    uploaded_urls = []
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    try:
        for file in files:
            if file.filename == '':
                continue
            
            # Validate file type
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_extension not in allowed_extensions:
                continue
            
            # Generate unique filename
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            file.save(filepath)
            
            # Add URL to list
            image_url = f"/uploads/{filename}"
            uploaded_urls.append(image_url)
        
        if not uploaded_urls:
            return jsonify({'error': 'No valid images uploaded'}), 400
        
        return jsonify({
            'message': f'{len(uploaded_urls)} images uploaded successfully',
            'image_urls': uploaded_urls
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload images: {str(e)}'}), 500

@upload_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

