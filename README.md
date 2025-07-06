# 🧵 Thread Lifecycle Tracer

A Linux thread lifecycle monitoring tool using **eBPF** and **BCC**, featuring:

- Real-time tracing of thread lifecycle events (FORK, EXIT, SWITCH, WAKEUP)
- CSV logging for analysis
- Live web dashboard using **Flask** + **Plotly.js**
- Optional static visualizer using Matplotlib

---

## 📁 Project Structure

```
thread-lifecycle-tracer/
├── thread_lifecycle_tracer.py    # Main tracer using eBPF + BCC
├── server.py                     # Flask app to serve API and frontend
├── thread_events_log.csv         # Event log file (auto-generated)
├── templates/
│   └── index.html                # Plotly dashboard (HTML + JS)
├── static/
│   └── plotly.min.js             # Plotly.js library
├── visualize_events.py           # Optional matplotlib-based visualizer
└── README.md                     # You're here!
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sambh256/thread-lifecycle-tracer.git
cd thread-lifecycle-tracer
```

### 2. Install Dependencies

Ensure you have:

- **Python 3**
- **BCC**:

```bash
sudo apt install bpfcc-tools linux-headers-$(uname -r)
```

- **Python modules**:

```bash
pip install bcc flask
```

---

## ▶️ Usage

### Start the Tracer

```bash
sudo python3 thread_lifecycle_tracer.py
```

This will begin tracing and write logs to `thread_events_log.csv`.

### Start the Web Server

In another terminal:

```bash
python3 server.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📊 Live Web Dashboard

- Real-time chart rendering using Plotly.js
- Filter by **PID** and **Event Type** using dropdowns
- Updated every 3 seconds with new event data

---

## 📂 CSV Format

Each row in `thread_events_log.csv` contains:

```
Timestamp,Event_Type,PID,PPID,Command,Parent_Command,Child_Command,Prev_PID,Prev_Command,Next_PID,Next_Command
```

Fields may be blank depending on the event.

---

## ❓ Event Types

| Type   | Description                      |
|--------|----------------------------------|
| FORK   | New thread created               |
| EXIT   | Thread terminated                |
| SWITCH | Context switch (prev → next)     |
| WAKEUP | Sleeping thread woken up         |

---

## 🧠 How it Works

- eBPF attaches to kernel tracepoints like `sched:sched_fork`, `sched:sched_exit`, etc.
- BCC processes events in userspace via perf buffers.
- Event data is filtered and logged into `thread_events_log.csv`.
- Flask serves this log data via a REST API (`/api/events`).
- The frontend (in `index.html`) fetches the API periodically and plots the data using Plotly.js.

---

## 🚧 Limitations

- High-frequency SWITCH/WAKEUP events can bloat the log.
- `Child_Command` is only populated for FORK.
- Tested on Ubuntu with Linux kernel ≥ 5.4

---

## 👤 Author

**Sambhav Powar**  
GitHub: [sambh256](https://github.com/sambh256)  
Project: [thread-lifecycle-tracer](https://github.com/sambh256/thread-lifecycle-tracer)

---

## 📜 License

MIT – feel free to use and modify.

