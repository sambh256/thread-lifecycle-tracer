import csv
import matplotlib.pyplot as plt
from datetime import datetime

csv_file = "thread_events_log.csv"  # path to your CSV file

timestamps = []
event_types = []

event_labels = {
    "FORK": 0,
    "EXIT": 1,
}

with open(csv_file, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ts = datetime.strptime(row["Timestamp"],"%H:%M:%S")
        timestamps.append(ts)
        event_types.append(event_labels.get(row["Event_Type"], -1))

# Convert event_types to strings for plotting
event_names = ["FORK" if e == 0 else "EXIT" for e in event_types]

plt.figure(figsize=(12, 6))
plt.scatter(timestamps, event_types, c=["blue" if e == 0 else "red" for e in event_types], label="Events")

plt.yticks([0, 1], ["FORK", "EXIT"])
plt.title("Thread Lifecycle Events Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Event Type")
plt.grid(True)
plt.tight_layout()
plt.savefig("event_timeline.png", dpi=300, bbox_inches='tight')
print("Saved visualization as event_timeline.png")

