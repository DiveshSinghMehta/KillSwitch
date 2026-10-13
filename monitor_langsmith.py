
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from langsmith import Client

PROJECT_NAME = "KILLSWITCH"
POLL_INTERVAL = 10

SENSITIVE_VALUES = [
    "9876543210",
    "123456789",
]

# Must match the location used by ai_app/kill_switch.py
FLAG_FILE = Path(__file__).resolve().parent / "kill_switch.flag"


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

                # Mark processed only after output is available.
                seen_run_ids.add(run_id)

                if matches:
                    print("\n🚨 SUSPICIOUS TRACE DETECTED")
                    print("Run ID:", run_id)
                    print("Trace name:", run.name)
                    print("Started:", run.start_time)
                    print("Matched test values:", len(matches))

                    FLAG_FILE.write_text("DISABLED", encoding="utf-8")
                    print("🛑 Shared kill-switch flag created.")
                    print("Future requests should be blocked.")
                else:
                    print(f"[OK] New trace: {run_id}")

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
