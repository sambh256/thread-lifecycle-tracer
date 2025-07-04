from flask import Flask, render_template, jsonify
import csv

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/events")
def get_events():
    events = []
    try:
        with open("thread_events_log.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in list(reader)[-20:]:
                events.append({
                    "Timestamp": row.get("Timestamp", ""),
                    "Event_Type": row.get("Event_Type", ""),
                    "PID": row.get("PID", ""),
                    "PPID": row.get("PPID", ""),
                    "Command": row.get("Command", ""),
                    "Parent_Command": row.get("Parent_Command", ""),
                    "Child_Command": row.get("Child_Command", "")
                })
    except Exception as e:
        print("CSV error:", e)
    return jsonify(events)

if __name__ == "__main__":
    app.run(debug=True)
