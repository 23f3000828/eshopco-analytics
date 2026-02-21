import json
import statistics
import os

def handler(request, context):

    # CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": ""
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": cors_headers(),
            "body": "Method Not Allowed"
        }

    try:
        body = json.loads(request.body)
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": f"Invalid JSON: {str(e)}"
        }

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Correct file path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, "telemetry.json")

    with open(file_path) as f:
        data = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        if latencies:
            avg_latency = sum(latencies) / len(latencies)

            # Manual p95 (no numpy)
            sorted_lat = sorted(latencies)
            index = int(0.95 * (len(sorted_lat) - 1))
            p95_latency = sorted_lat[index]

            avg_uptime = sum(uptimes) / len(uptimes)
            breaches = sum(1 for l in latencies if l > threshold)
        else:
            avg_latency = 0
            p95_latency = 0
            avg_uptime = 0
            breaches = 0

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(result)
    }


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }