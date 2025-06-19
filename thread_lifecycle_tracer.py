from bcc import BPF
from time import sleep

bpf_program = """
TRACEPOINT_PROBE(sched, sched_process_fork) {
    bpf_trace_printk("Fork: Parent PID %d -> Child PID %d\\n", args->parent_pid, args->child_pid);
    return 0;
}

TRACEPOINT_PROBE(sched, sched_process_exit) {
    bpf_trace_printk("Exit: PID %d\\n", args->pid);
    return 0;
}
"""

b = BPF(text=bpf_program)
print("Tracing thread fork and exit... Press Ctrl+C to stop.\n")
try:
    b.trace_print()
except KeyboardInterrupt:
    print("\nStopped tracing.")
