from flask import Flask, render_template, request, jsonify, abort
import requests
import random
import secrets
import hashlib
import json
from io import BytesIO
import os
from PIL import Image
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['GOLDEN_TICKET_RARITY'] = 1000000
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB ish max file size
app.config['MAX_ATTEMPTS'] = 5
app.config['BYPASS_LOCALHOST_CHECK'] = os.environ.get("DEBUG", "false") == "true"

global_attempts = 0

def localhost_only(f):
    """Decorator to restrict access to localhost only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['BYPASS_LOCALHOST_CHECK'] and request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

with open('fortunes.json', 'r') as f:
    FORTUNES = json.load(f)

GOLDEN_FORTUNE = "The stars align perfectly for you. Exceptional fortune awaits in all endeavors. Your path is blessed with extraordinary luck and success beyond measure."

def analyze_image_hash(image_data):
    """Generate a hash from image data for fortune selection."""
    if isinstance(image_data, bytes):
        return hashlib.md5(image_data).hexdigest()
    return hashlib.md5(str(image_data).encode()).hexdigest()

def get_fortune_category(image_hash):
    """Determine fortune category based on image hash."""
    categories = list(FORTUNES.keys())
    index = int(image_hash[:8], 16) % len(categories)
    return categories[index]

def select_fortune(category):
    if random.randint(1, int(app.config['GOLDEN_TICKET_RARITY'])) == 1:
        return GOLDEN_FORTUNE, True
    
    fortunes = FORTUNES.get(category, FORTUNES['general'])
    return random.choice(fortunes), False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fortune', methods=['POST'])
def get_fortune():
    """Process image and return fortune."""
    global global_attempts
    
    if global_attempts >= int(app.config['MAX_ATTEMPTS']):
        return jsonify({'error': 'Maximum attempts reached'}), 429
    
    global_attempts += 1
    
    image_data = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename:
            try:
                img = Image.open(file.stream)
                img.verify()
                file.stream.seek(0)
                image_data = file.read()
            except Exception:
                return jsonify({'error': 'Invalid image file'}), 400
    
    elif request.is_json:
        data = request.get_json()
        image_url = data.get('image_url', '').strip()
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        try:
            # A proper fix would be to use an HTTP client that is resistant to DNS rebinding attacks.
            # In this case, we assume the admin panel will not be accessible over HTTPS given that it is bound to localhost.
            if not image_url.startswith('https://'):
                return jsonify({'error': 'Invalid URL scheme'}), 400
            
            response = requests.get(image_url, timeout=5, allow_redirects=False)
            response.raise_for_status()
            
            try:
                img = Image.open(BytesIO(response.content))
                img.verify()
                image_data = response.content
            except Exception:
                return jsonify({'error': 'URL does not contain a valid image'}), 400
                
        except requests.RequestException as e:
            return jsonify({'error': f'Failed to fetch image: {str(e)}'}), 400
    else:
        return jsonify({'error': 'No image provided'}), 400
    
    if image_data:
        image_hash = analyze_image_hash(image_data)
        category = get_fortune_category(image_hash)
        
        fortune, is_golden = select_fortune(category)
        
        return jsonify({
            'fortune': fortune,
            'category': category.title(),
            'special': is_golden
        })
    
    return jsonify({'error': 'Failed to process image'}), 400
    

# Allow for setting odds/attempts dynamically
@app.route('/admin/config')
@localhost_only
def admin_config():
    data = {}
    data.update(request.form.to_dict())
    data.update(request.args.to_dict())
    
    # Set all data as app config
    for key, value in data.items():
        app.config[key] = value
    
    # Return current config
    return str(app.config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6010, debug=False)