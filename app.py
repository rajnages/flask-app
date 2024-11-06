from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Get build number from environment variable or use 'Development'
    build_number = os.environ.get('BUILD_NUMBER', 'Development')
    
    # Get current server time
    server_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Mock data for metrics
    metrics = {
        'cpu_usage': 75,
        'memory_usage': 60,
    }
    
    # Mock data for recent logs
    logs = [
        {'time': '10:45', 'type': 'success', 'message': 'Pipeline deployment completed'},
        {'time': '10:43', 'type': 'info', 'message': 'Docker container started'},
        {'time': '10:42', 'type': 'info', 'message': 'Building Docker image'}
    ]
    
    return render_template('index.html',
                         build_number=build_number,
                         server_time=server_time,
                         metrics=metrics,
                         logs=logs)

@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': os.environ.get('BUILD_NUMBER', 'Development')
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)