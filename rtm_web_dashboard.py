from flask import Flask, render_template, jsonify

# rtm_web_dashboard.py


app = Flask(__name__)

# Sample data for the dashboard
dashboard_data = {
    "title": "RTM Web Dashboard",
    "metrics": {
        "total_tasks": 120,
        "completed_tasks": 95,
        "pending_tasks": 25
    },
    "status": "Operational"
}

@app.route('/')
def index():
    return render_template('index.html', data=dashboard_data)

@app.route('/api/data')
def api_data():
    return jsonify(dashboard_data)

if __name__ == '__main__':
    app.run(debug=True)