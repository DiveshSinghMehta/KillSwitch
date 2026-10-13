"""Optional output scanner; detections require a human to trigger the switch."""


def monitor_output(output):
    sensitive_values = ["9876543210"]
    text = str(output or "")
    found = [value for value in sensitive_values if value in text]
    if found:
        print("Sensitive output detected; manual review required.")
    return bool(found)
