import subprocess
import sys

test_cases = [
    "10.0.0.1",
    "155.185.10.1",
    "192.168.1.1",
    "192.168.",
    "192.157.1.1",
    "192.F0.1.1",
    "Prova",
]

for ip in test_cases:
    print(f"Test: {ip}")
    result = subprocess.run(
        [sys.executable, "client.py", "localhost", ip], capture_output=True, text=True
    )
    print(result.stdout)
    print("-" * 40)
