import json
import statistics
import numpy as np

def handler(request, context):

    # Handle CORS preflight
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
    except:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": "Invalid JSON"
        }

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    with open("telemetry.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = float(np.percentile(latencies, 95))
            avg_uptime = statistics.mean(uptimes)
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