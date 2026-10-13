from .kill_switch import kill_switch


def monitor_output(output):
    sensitive_values = [
        "9876543210"
    ]

    for value in sensitive_values:
        if value in output:
            print("🚨 LEAK DETECTED!")
            kill_switch()
            return True

    return False