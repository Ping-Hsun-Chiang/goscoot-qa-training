import requests
import json

URL = "http://localhost:5000/api/v1/vehicle/telemetry"

test_cases = [
    {
        "name": "TC01 正常情境 (battery=42)",
        "expect_status": 200,
        "expect_command": "none",
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 42,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC02 邊界值：battery=16（正常模式上邊界）",
        "expect_status": 200,
        "expect_command": "none",
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 16,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC03 邊界值：battery=15（降速門檻）",
        "expect_status": 200,
        "expect_command": "slow_down",
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 15,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC04 邊界值：battery=6（降速模式下邊界）",
        "expect_status": 200,
        "expect_command": "slow_down",
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 6,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC05 邊界值：battery=5（強制鎖車門檻）",
        "expect_status": 200,
        "expect_command": "lock",
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 5,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC06 異常：battery=-1（負數）",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": -1,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC07 異常：battery=101（超過100）",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 101,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC08 異常：battery='abc'（字串型別）",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": "abc",
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC09 資安：SQL Injection in vehicle_id",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "'; DROP TABLE vehicles;--",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 42,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC10 異常：gps.lat=91（超出地球範圍）",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 91.0, "lng": 121.5654},
            "battery": 42,
            "speed": 18.5,
            "status": "in_use"
        }
    },
    {
        "name": "TC11 異常：speed=-10（負速度）",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026-05-06T14:00:00Z",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 42,
            "speed": -10,
            "status": "in_use"
        }
    },
    {
        "name": "TC12 異常：timestamp 格式錯誤",
        "expect_status": 400,
        "expect_command": None,
        "body": {
            "vehicle_id": "GS-00123",
            "timestamp": "2026/05/06 14:00:00",
            "gps": {"lat": 25.033, "lng": 121.5654},
            "battery": 42,
            "speed": 18.5,
            "status": "in_use"
        }
    },
]


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("GoScoot API 測試報告")
    print("=" * 60)

    for tc in test_cases:
        try:
            resp = requests.post(URL, json=tc["body"], timeout=5)
            actual_status = resp.status_code
            actual_body = resp.json()
            actual_command = actual_body.get("command")

            status_ok = actual_status == tc["expect_status"]
            command_ok = (tc["expect_command"] is None) or (actual_command == tc["expect_command"])

            if status_ok and command_ok:
                result = "PASS"
                passed += 1
            else:
                result = "FAIL"
                failed += 1

            print(f"\n[{result}] {tc['name']}")
            print(f"  預期: status={tc['expect_status']}, command={tc['expect_command']}")
            print(f"  實際: status={actual_status}, command={actual_command}")
            if not status_ok or not command_ok:
                print(f"  回應內容: {json.dumps(actual_body, ensure_ascii=False)}")

        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] {tc['name']}")
            print("  無法連線到 Mock Server，請確認 python mock_server.py 已啟動")
            return

    print("\n" + "=" * 60)
    print(f"結果：{passed} 通過 / {failed} 失敗 / 共 {len(test_cases)} 筆")
    print("=" * 60)


if __name__ == "__main__":
    run()
