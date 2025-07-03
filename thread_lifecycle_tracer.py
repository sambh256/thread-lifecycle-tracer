import csv
import os
from bcc import BPF
from datetime import datetime
from time import sleep
import ctypes

# eBPF program
bpf_program = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

enum event_type {
    EVENT_FORK = 0,
    EVENT_EXIT,
    EVENT_SWITCH,
    EVENT_WAKEUP,
};

struct event_t {
    u32 event_type;
    u32 pid;
    u32 ppid;
    char comm[TASK_COMM_LEN];
    char parent_comm[TASK_COMM_LEN];
    char child_comm[TASK_COMM_LEN];
    u32 prev_pid;
    u32 next_pid;
    char prev_comm[TASK_COMM_LEN];
    char next_comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(events);

// sched_process_fork
TRACEPOINT_PROBE(sched, sched_process_fork) {
    struct event_t data = {};
    data.event_type = EVENT_FORK;
    data.pid = args->child_pid;
    data.ppid = args->parent_pid;
    __builtin_memcpy(&data.parent_comm, args->parent_comm, TASK_COMM_LEN);
    __builtin_memcpy(&data.child_comm, args->child_comm, TASK_COMM_LEN);
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}

// sched_process_exit
TRACEPOINT_PROBE(sched, sched_process_exit) {
    struct event_t data = {};
    data.event_type = EVENT_EXIT;
    data.pid = args->pid;
    __builtin_memcpy(&data.comm, args->comm, TASK_COMM_LEN);
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}

// sched_switch
TRACEPOINT_PROBE(sched, sched_switch) {
    struct event_t data = {};
    data.event_type = EVENT_SWITCH;
    data.prev_pid = args->prev_pid;
    data.next_pid = args->next_pid;
    __builtin_memcpy(&data.prev_comm, args->prev_comm, TASK_COMM_LEN);
    __builtin_memcpy(&data.next_comm, args->next_comm, TASK_COMM_LEN);
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}

// sched_wakeup
TRACEPOINT_PROBE(sched, sched_wakeup) {
    struct event_t data = {};
    data.event_type = EVENT_WAKEUP;
    data.pid = args->pid;
    __builtin_memcpy(&data.comm, args->comm, TASK_COMM_LEN);
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}
"""
log_file = "thread_events_log.csv"
new_file = not os.path.exists(log_file)

csvfile = open(log_file, "a", newline="")
csvwriter = csv.writer(csvfile)

if new_file:
    csvwriter.writerow([
        "Timestamp", "Event_Type", "PID", "PPID",
        "Command", "Parent_Command", "Child_Command",
        "Prev_PID", "Prev_Command", "Next_PID", "Next_Command"
    ])

# Load BPF
b = BPF(text=bpf_program)
log_file = "thread_events_log.csv"
new_file = not os.path.exists(log_file)

csvfile = open(log_file, "a", newline="")
csvwriter = csv.writer(csvfile)

if new_file:
    csvwriter.writerow([
        "Timestamp", "Event_Type", "PID", "PPID",
        "Command", "Parent_Command", "Child_Command",
        "Prev_PID", "Prev_Command", "Next_PID", "Next_Command"
    ])

# Define event struct
class Event(ctypes.Structure):
    _fields_ = [
        ("event_type", ctypes.c_uint),
        ("pid", ctypes.c_uint),
        ("ppid", ctypes.c_uint),
        ("comm", ctypes.c_char * 16),
        ("parent_comm", ctypes.c_char * 16),
        ("child_comm", ctypes.c_char * 16),
        ("prev_pid", ctypes.c_uint),
        ("next_pid", ctypes.c_uint),
        ("prev_comm", ctypes.c_char * 16),
        ("next_comm", ctypes.c_char * 16),
    ]

def handle_event(cpu, data, size):
    event = ctypes.cast(data, ctypes.POINTER(Event)).contents
    ts = datetime.now().strftime("%H:%M:%S")

    # Filter out SWITCH and WAKEUP events
    if event.event_type in (2, 3):
        return

    # Filter kernel background threads
    if event.event_type == 0:  # FORK
        if event.parent_comm.decode().startswith("kworker") or \
           event.child_comm.decode().startswith("kworker"):
            return
    elif event.event_type == 1:  # EXIT
        if event.comm.decode().startswith("kworker"):
            return

    # Print and log FORK
    if event.event_type == 0:
        print(f"[{ts}] FORK: Parent PID {event.ppid} ({event.parent_comm.decode()}) -> Child PID {event.pid} ({event.comm.decode()})")
        csvwriter.writerow([ts, "FORK", event.pid, event.ppid,
                            event.comm.decode(), event.parent_comm.decode(), "", "", "", "", ""])

    # Print and log EXIT
    elif event.event_type == 1:
        print(f"[{ts}] EXIT: PID {event.pid} ({event.comm.decode()})")
        csvwriter.writerow([ts, "EXIT", event.pid, "", event.comm.decode(),
                            "", "", "", "", "", ""])

    csvfile.flush()


    # Now print only filtered interesting events
    if event.event_type == 0:
        print(f"[{ts}] FORK: Parent PID {event.ppid} ({event.parent_comm.decode()}) -> Child PID {event.pid} ({event.child_comm.decode()})")
    elif event.event_type == 1:
        print(f"[{ts}] EXIT: PID {event.pid} ({event.comm.decode()})")
    elif event.event_type == 2:
        print(f"[{ts}] SWITCH: From PID {event.prev_pid} ({event.prev_comm.decode()}) -> To PID {event.next_pid} ({event.next_comm.decode()})")
    elif event.event_type == 3:
        print(f"[{ts}] WAKEUP: PID {event.pid} ({event.comm.decode()})")


# Set up perf event listener
b["events"].open_perf_buffer(handle_event)

print("Tracing thread lifecycle events... Ctrl+C to stop.")
try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    print("Stopped.")
