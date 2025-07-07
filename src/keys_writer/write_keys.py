import sys
import json
import subprocess
import base64
import time
import signal

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <dut_py_path> <generated_keys.json>")
        sys.exit(1)
    dut_path = sys.argv[1]
    json_path = sys.argv[2]
    with open(json_path, "r") as f:
        data = json.load(f)

    # Decode base64 and convert to hex for half_kek
    half_kek_b64 = data["kek_seed_half2"]
    half_kek = base64.b64decode(half_kek_b64).hex()
    encrypted_ipad = data["encrypted_ipad"]  # base64 string
    encrypted_opad = data["encrypted_opad"]  # base64 string
    challenge = data["challenge"]  # base64 string
    response = data["response"]  # base64 string

    dut_proc = subprocess.Popen([sys.executable, dut_path, json_path])

    def signal_handler(sig, frame):
        print("\nTerminating DUT process...")
        dut_proc.terminate()
        dut_proc.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    time.sleep(2)  # Wait for dut.py to initialize

    commands = [
        ["--write-battery-provision-key", half_kek],
        ["--write-battery-provision-ipad", encrypted_ipad],
        ["--write-battery-provision-opad", encrypted_opad],
        ["--write-battery-provision-challenge", challenge],
        ["--write-battery-provision-response", response],
        ["--provision-battery"],
    ]

    for cmd in commands:
        print("Running command:", " ".join(cmd))
        subprocess.run([sys.executable, dut_path] + cmd, check=True)

    print("All commands executed. DUT process is running. Press Ctrl+C to terminate.")
    dut_proc.wait()

if __name__ == "__main__":
    main()
