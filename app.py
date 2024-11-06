from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def hello():
    build_number = os.environ.get('BUILD_NUMBER', 'Development')
    server_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html', 
                         build_number=build_number,
                         server_time=server_time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)