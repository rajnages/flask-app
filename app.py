from flask import Flask, render_template, jsonify
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_metrics():
    """Get basic system metrics"""
    try:
        # Mock metrics instead of using psutil
        return {
            'cpu_usage': 75,
            'memory_usage': 60
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
            'metrics': get_metrics(),
            'logs': [
                {'time': '10:45', 'type': 'success', 'message': 'Pipeline deployment completed'},
                {'time': '10:43', 'type': 'info', 'message': 'Docker container started'},
                {'time': '10:42', 'type': 'info', 'message': 'Building Docker image'}
            ]
        }
        logger.info("Rendering index template with data")
        return render_template('index.html', **data)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return f"Server Error: {str(e)}", 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000, debug=True)