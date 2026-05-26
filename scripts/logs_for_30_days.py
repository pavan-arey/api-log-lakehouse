import subprocess
from datetime import date, timedelta
from pathlib import Path

START_DATE = date(2026, 4, 23)
DAYS = 30

ROWS_PER_DAY = 25_000
ROWS_PER_FILE = 25_000

OUT_BASE = Path("sample_data/raw_scaled")

def run_cmd(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    for day_offset in range(DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        date_str = current_date.isoformat()

        # Add late-arriving data on every 3rd day after day 1
        if day_offset >= 2 and day_offset % 3 == 0:
            late_rate = 0.08
        else:
            late_rate = 0.0

        for hour, seed_offset in [("09", 1), ("10", 2)]:
            out_path = OUT_BASE / f"ingest_date={date_str}" / f"hour={hour}" / "part-0001.json"

            seed = (day_offset + 1) * 100 + seed_offset

            cmd = [
                "python",
                "scripts/generate_logs.py",
                "--date", date_str,
                "--hour", hour,
                "--rows", str(ROWS_PER_FILE),
                "--late-rate", str(late_rate),
                "--dup-rate", "0.025",
                "--bad-rate", "0.015",
                "--seed", str(seed),
                "--out", str(out_path),
            ]

            run_cmd(cmd)

if __name__ == "__main__":
    main()