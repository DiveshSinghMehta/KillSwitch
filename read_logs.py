
from langsmith import Client
from datetime import datetime, timedelta, timezone

client = Client()

runs = client.list_runs(
    project_name="KILLSWITCH",
    start_time=datetime.now(timezone.utc) - timedelta(days=1),
    limit=20,
)

for run in runs:
    print("-" * 50)
    print("Name:", run.name)
    print("Run ID:", run.id)
    print("Started:", run.start_time)
    print("Error:", run.error)
    print("Input:", run.inputs)
    print("Output:", run.outputs)
