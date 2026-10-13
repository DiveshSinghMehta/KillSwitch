
from datetime import datetime, timedelta, timezone
from langsmith import Client

client = Client()

# Test values only. Use fictional data.
SENSITIVE_VALUES = [
    "9876543210",
    "123456789",
]

runs = client.list_runs(
    project_name="KILLSWITCH",
    start_time=datetime.now(timezone.utc) - timedelta(days=1),
    limit=100,
)

total = 0
flagged = 0

for run in runs:
    total += 1

    output = str(run.outputs or "")
    matches = [
        value for value in SENSITIVE_VALUES
        if value in output
    ]

    if matches:
        flagged += 1
        print("\n🚨 SUSPICIOUS OUTPUT")
        print("Run ID:", run.id)
        print("Run name:", run.name)
        print("Started:", run.start_time)
        print("Matched test values:", len(matches))
        # Avoid printing the sensitive output itself.

print("\n========== SUMMARY ==========")
print("Traces scanned:", total)
print("Suspicious traces:", flagged)
print("Other traces:", total - flagged)
