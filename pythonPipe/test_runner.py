import serial
import time
import csv

# Change this to your actual COM port
COM_PORT = "COM9"
BAUD_RATE = 115200
CSV_FILE = "expected_results.csv"

def read_expected_results(file_path):
    expected = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            expected.append([int(v) for v in row])
    return expected

def main():
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give Arduino time to reset

    # 🔁 Tell Arduino to start test
    ser.write(b'start\n')
    print("📡 Listening for test results...\n")

    results = []
    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        print("Arduino:", line)
        if line.startswith("✅ All tests"):
            break
        if line[0].isdigit():
            results.append([int(v) for v in line.split(",")])

    expected = read_expected_results(CSV_FILE)

    print("\n🔎 Checking results...")
    for actual, expect in zip(results, expected):
        status = "✅ PASS" if actual == expect else "❌ FAIL"
        print(f"Test {actual[0]}: Got {actual[1:]} | Expected {expect[1:]} → {status}")

    ser.close()

if __name__ == "__main__":
    main()
