
import asyncio
import os
from datetime import datetime, timedelta, timezone

from langsmith import Client
import redis

PROJECT_NAME = "KILLSWITCH"
POLL_INTERVAL = 10
REDIS_CLIENT = redis.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)
KILL_STATE_KEY = "ai_service:state"

SENSITIVE_VALUES = [
    "9876543210",
    "123456789",
]

def find_sensitive_values(output):
    text = str(output or "")
    return [value for value in SENSITIVE_VALUES if value in text]


async def main():
    client = Client()
    project = await client.aread_project(project_name=PROJECT_NAME)
    project_id = str(project.id)

    seen_run_ids = set()

    print(f"Monitoring LangSmith project: {PROJECT_NAME}")
    print(f"Checking every {POLL_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            now = datetime.now(timezone.utc)

            async for run in client.runs.query(
                project_ids=[project_id],
                min_start_time=now - timedelta(minutes=5),
                max_start_time=now,
                filter='eq(name, "KILLSWITCH Ollama Generation")',
                selects=[
                    "ID", "NAME", "START_TIME", "OUTPUTS", "ERROR"
                ],
                page_size=100,
            ):
                run_id = str(run.id)

                if run_id in seen_run_ids:
                    continue

                # Don't mark a run as seen if its output
                # hasn't arrived yet.
                if not run.outputs:
                    continue

                matches = find_sensitive_values(run.outputs)

                if matches:
                    print("\n🚨 SUSPICIOUS TRACE DETECTED")
                    print("Run ID:", run_id)
                    print("Trace name:", run.name)
                    print("Started:", run.start_time)
                    print("Matched test values:", len(matches))

                    # Write to Redis directly. Nginx reads this state before
                    # proxying, so detection does not depend on a Django request.
                    REDIS_CLIENT.set(KILL_STATE_KEY, "KILLED")
                    print("Redis state set to KILLED; Nginx will block regular requests.")
                else:
                    print(f"[OK] New trace: {run_id}")

                # If the Redis write fails, leave the run unseen so the next
                # poll retries the kill action.
                seen_run_ids.add(run_id)

                if run.error:
                    print("Trace reported an error.")

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(
                f"Monitor error: {type(exc).__name__}. "
                "Retrying next cycle."
            )

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLangSmith monitor stopped.")
