# app.py
from flask import Flask, request, jsonify
import uuid
from worker import job_queue, job_status, job_results

app = Flask(__name__)

@app.post("/submit")
def submit_code():
    """
    Accept user's C++ code and create a job.
    """
    code = request.json.get("code", "")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Create unique job ID
    job_id = str(uuid.uuid4())

    # Save code to a temporary file
    filename = f"submissions/{job_id}.cpp"
    with open(filename, "w") as f:
        f.write(code)

    # Add job to queue
    job_queue.append({
        "job_id": job_id,
        "filename": filename
    })

    # Mark initial status
    job_status[job_id] = "queued"

    return jsonify({"job_id": job_id}), 200


@app.get("/status/<job_id>")
def get_status(job_id):
    """
    User checks the CURRENT status of their job.
    """
    status = job_status.get(job_id, "not_found")
    return jsonify({"job_id": job_id, "status": status})


@app.get("/result/<job_id>")
def get_result(job_id):
    """
    User gets the final evaluation result.
    """
    result = job_results.get(job_id, None)
    if result is None:
        return jsonify({"error": "Results not available yet"}), 404
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
