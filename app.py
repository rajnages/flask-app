from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import psutil
from functools import wraps
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add basic authentication
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    # Replace with secure authentication
    return username == os.environ.get('API_USER') and password == os.environ.get('API_PASS')

def get_safe_metrics():
    """Get limited system metrics"""
    try:
        return {
            'cpu_usage': min(psutil.cpu_percent(), 100),
            'memory_usage': min(psutil.virtual_memory().percent, 100)
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {'cpu_usage': 0, 'memory_usage': 0}

@app.route('/')
def index():
    try:
        data = {
            'build_number': os.environ.get('BUILD_NUMBER', 'Development'),
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': get_safe_metrics(),
            'logs': get_recent_logs(limit=5)  # Limit number of logs
        }
        return render_template('index.html', **data)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('error.html', error="Internal Server Error"), 500

@app.route('/api/metrics')
@require_auth
def get_metrics():
    """Protected metrics endpoint"""
    try:
        metrics = get_safe_metrics()
        return jsonify({
            'success': True,
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in metrics endpoint: {e}")
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

@app.route('/health')
def health():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': os.environ.get('BUILD_NUMBER', 'Development')
    })

if __name__ == '__main__':
    # Ensure debug mode is off in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode:
        logger.warning("Running in debug mode - not recommended for production!")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )