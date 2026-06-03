"""
Simple Flask server for TN26 Election Dashboard
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
            static_folder='dashboard',
            static_url_path='/dashboard')

# Serve main dashboard
@app.route('/')
def index():
    return send_from_directory('dashboard', 'index.html')

# Serve static files (CSS, JS)
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('dashboard/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('dashboard/js', filename)

# Serve CSV data files
@app.route('/data/<path:filename>')
def serve_data(filename):
    # Only allow CSV files
    if not filename.endswith('.csv'):
        return 'Access denied', 403
    return send_from_directory('data', filename)

# Error handler
@app.errorhandler(404)
def not_found(error):
    return 'File not found', 404

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   TN26 ELECTION DASHBOARD - Flask Server               ║
    ╚════════════════════════════════════════════════════════╝
    
    📊 Dashboard: http://localhost:5000
    
    Press Ctrl+C to stop
    """)
    app.run(debug=True, port=5000, host='0.0.0.0')
