import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SERVICES = ["auth-api", "docs-api", "search-api", "notifications-api"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
CLIENT_TYPES = ["web", "desktop", "mobile"]
REGIONS = ["ap-south-1", "eu-west-1", "us-east-1"]

ENDPOINTS = {
    "auth-api": ["/v1/login", "/v1/logout", "/v1/refresh"],
    "docs-api": ["/v1/documents/upload", "/v1/documents/get"],
    "search-api": ["/v1/search"],
    "notifications-api": ["/v1/notify"]
}


def weighted_status_code():
    r = random.random()
    if r < 0.75:
        return random.choice([200, 201])
    elif r < 0.92:
        return random.choice([400, 401, 404])
    else:
        return random.choice([500, 503])


def generate_event_time(base_date, hour, late_rate):
    base_dt = datetime.strptime(f"{base_date} {hour}", "%Y-%m-%d %H")

    if random.random() < late_rate:
        # late event → previous day
        base_dt -= timedelta(days=1)

    # random seconds within the hour
    seconds = random.randint(0, 3599)
    return (base_dt + timedelta(seconds=seconds)).isoformat() + "Z"


def generate_row(idx, base_date, hour, late_rate):
    service = random.choice(SERVICES)
    endpoint = random.choice(ENDPOINTS[service])

    row = {
        "request_id": f"req_{base_date.replace('-', '')}_{idx:06d}",
        "event_time": generate_event_time(base_date, hour, late_rate),
        "service": service,
        "endpoint": endpoint,
        "method": random.choice(METHODS),
        "status_code": weighted_status_code(),
        "latency_ms": max(1, int(random.gauss(120, 50))),
        "bytes_in": random.randint(100, 2000),
        "bytes_out": random.randint(500, 50000),
        "client_type": random.choice(CLIENT_TYPES),
        "region": random.choice(REGIONS),
        "host": f"app-{random.randint(1, 5):02d}"
    }

    return row


def inject_bad_row(row):
    bad_type = random.choice(["missing_id", "negative_latency", "bad_status"])

    if bad_type == "missing_id":
        row.pop("request_id", None)
    elif bad_type == "negative_latency":
        row["latency_ms"] = -random.randint(1, 100)
    elif bad_type == "bad_status":
        row["status_code"] = 999

    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--hour", required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--late-rate", type=float, default=0.0)
    parser.add_argument("--dup-rate", type=float, default=0.0)
    parser.add_argument("--bad-rate", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    random.seed(args.seed)

    rows = []
    seen_rows = []

    for i in range(1, args.rows + 1):
        row = generate_row(i, args.date, args.hour, args.late_rate)

        # inject bad row
        if random.random() < args.bad_rate:
            row = inject_bad_row(row)

        rows.append(row)
        seen_rows.append(row)

        # inject duplicate
        if seen_rows and random.random() < args.dup_rate:
            dup = random.choice(seen_rows)
            rows.append(dup)

    # ensure output directory exists
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # write JSON lines
    with open(output_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()