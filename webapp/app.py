from flask import Flask, render_template
import json
import os

app = Flask(__name__)

REPORT_FILE = "reports/health-report.json"


@app.route("/")
def dashboard():

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {
            "queue_manager": "QM1",
            "status": "NO DATA",
            "queues": []
        }

    return render_template(
        "dashboard.html",
        report=data
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
