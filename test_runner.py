import serial
import time
import csv
import json
import os

# --- Config ---
COM_PORT = "COM9"
BAUD_RATE = 115200
CSV_FILE = "expected_results.csv"
BADGE_FOLDER = "badges"
OVERALL_BADGE = os.path.join(BADGE_FOLDER, "results-badge.json")
PERCENTAGE_BADGE = os.path.join(BADGE_FOLDER, "results-percentage-badge.json")
FRACTION_BADGE = os.path.join(BADGE_FOLDER, "results-fraction-badge.json")


def read_expected_results(file_path):
    expected = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            expected.append([int(v) for v in row])
    return expected


def write_badge(passed):
    badge_data = {
        "schemaVersion": 1,
        "label": "Supervisor Tests",
        "message": "pass" if passed else "fail",
        "color": "brightgreen" if passed else "red"
    }
    with open(OVERALL_BADGE, "w") as f:
        json.dump(badge_data, f)


def write_percentage_badge(passed, total):
    percent = int((passed / total) * 100)
    badge_data = {
        "schemaVersion": 1,
        "label": "Passing",
        "message": f"{percent}%",
        "color": "brightgreen" if percent == 100 else "orange" if percent >= 50 else "red"
    }
    with open(PERCENTAGE_BADGE, "w") as f:
        json.dump(badge_data, f)


def write_fraction_badge(passed, total):
    badge_data = {
        "schemaVersion": 1,
        "label": "Passed",
        "message": f"{passed}/{total}",
        "color": "brightgreen" if passed == total else "orange" if passed > 0 else "red"
    }
    with open(FRACTION_BADGE, "w") as f:
        json.dump(badge_data, f)


def write_individual_badges(results, expected):
    for actual, expect in zip(results, expected):
        test_id = actual[0]
        passed = actual == expect
        badge_data = {
            "schemaVersion": 1,
            "label": f"Test {test_id}",
            "message": "pass" if passed else "fail",
            "color": "brightgreen" if passed else "red"
        }
        badge_path = os.path.join(BADGE_FOLDER, f"test{test_id}-badge.json")
        with open(badge_path, "w") as f:
            json.dump(badge_data, f)


def main():
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give Arduino time to reset

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
    num_passed = 0
    for actual, expect in zip(results, expected):
        passed = actual == expect
        if passed:
            num_passed += 1
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {actual[0]}: Got {actual[1:]} | Expected {expect[1:]} → {status}")

    total = len(expected)
    write_badge(num_passed == total)
    write_percentage_badge(num_passed, total)
    write_fraction_badge(num_passed, total)
    write_individual_badges(results, expected)

    ser.close()


if __name__ == "__main__":
    main()