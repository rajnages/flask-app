from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_metrics():
    return {
        'cpu_usage': 75,
        'memory_usage': 60
    }

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
        return render_template('index.html', **data)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return str(e), 500

@app.route('/metrics')
def metrics():
    try:
        metrics_data = get_metrics()
        return render_template('metrics.html', metrics=metrics_data)
    except Exception as e:
        logger.error(f"Error in metrics route: {e}")
        return str(e), 500

@app.route('/history')
def history():
    try:
        history_data = [
            {'date': '2024-01-20', 'event': 'Deployment', 'status': 'Success'},
            {'date': '2024-01-19', 'event': 'Testing', 'status': 'Success'},
            {'date': '2024-01-18', 'event': 'Build', 'status': 'Failed'}
        ]
        return render_template('history.html', history=history_data)
    except Exception as e:
        logger.error(f"Error in history route: {e}")
        return str(e), 500

@app.route('/settings')
def settings():
    try:
        settings_data = {
            'notifications': True,
            'theme': 'light',
            'auto_deploy': False
        }
        return render_template('settings.html', settings=settings_data)
    except Exception as e:
        logger.error(f"Error in settings route: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)