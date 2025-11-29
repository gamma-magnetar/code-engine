# worker.py
import threading
import subprocess
import time
import queue

# Simple queue for jobs
job_queue = queue.Queue()

# Status & results storage
job_status = {}     # job_id → current state
job_results = {}    # job_id → final output

def evaluate_code(job):
    job_id = job["job_id"]
    filename = job["filename"]

    # Step 1: COMPILATION
    job_status[job_id] = "compiling"
    compile_cmd = ["g++", filename, "-o", f"{filename}.out"]
    compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)

    if compile_proc.returncode != 0:
        # Compilation error → store result & return
        job_status[job_id] = "completed"
        job_results[job_id] = {
            "verdict": "CE",
            "error": compile_proc.stderr
        }
        return

    # Step 2: RUNNING TESTCASES
    job_status[job_id] = "running"

    # Testcases (simple example)
    testcases = [
        {"input": "3\n", "expected": "6\n"},     # example problem: output input*2
        {"input": "5\n", "expected": "10\n"}
    ]

    testcase_results = []
    binary = f"{filename}.out"

    for t in testcases:
        try:
            # TIMEOUT for infinite loops
            run_proc = subprocess.run(
                [binary],
                input=t["input"],
                text=True,
                capture_output=True,
                timeout=2   # 2-second timeout
            )

            output = run_proc.stdout

            # Compare expected output
            verdict = "AC" if output == t["expected"] else "WA"

        except subprocess.TimeoutExpired:
            verdict = "TLE"
            output = ""

        testcase_results.append({
            "input": t["input"],
            "expected": t["expected"],
            "output": output,
            "verdict": verdict
        })

    job_status[job_id] = "completed"
    job_results[job_id] = {
        "verdict": "done",
        "testcases": testcase_results
    }


def worker_thread():
    """
    Background worker loop.
    Continuously picks jobs & evaluates them.
    """
    while True:
        job = job_queue.get()  # Wait for job
        evaluate_code(job)
        job_queue.task_done()


# Start worker thread (asynchronous)
thread = threading.Thread(target=worker_thread, daemon=True)
thread.start()
