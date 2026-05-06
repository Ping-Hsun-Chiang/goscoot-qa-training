import re
from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)


def validate_telemetry(data):
    errors = []

    # vehicle_id
    vid = data.get("vehicle_id")
    if not isinstance(vid, str) or not vid.strip():
        errors.append("vehicle_id: 必須是非空字串")
    elif not re.match(r"^GS-\d{5}$", vid):
        errors.append(f"vehicle_id: 格式錯誤，必須符合 GS-XXXXX（如 GS-00123）")

    # timestamp
    ts = data.get("timestamp")
    if not isinstance(ts, str):
        errors.append("timestamp: 必須是字串（ISO 8601 格式）")
    else:
        try:
            datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            errors.append("timestamp: 格式錯誤，應為 ISO 8601")

    # gps
    gps = data.get("gps")
    if not isinstance(gps, dict):
        errors.append("gps: 必須是物件")
    else:
        lat = gps.get("lat")
        lng = gps.get("lng")
        if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
            errors.append("gps.lat: 必須是 -90 ~ 90 的數字")
        if not isinstance(lng, (int, float)) or not (-180 <= lng <= 180):
            errors.append("gps.lng: 必須是 -180 ~ 180 的數字")

    # battery
    battery = data.get("battery")
    if not isinstance(battery, (int, float)):
        errors.append("battery: 必須是數字")
    elif not (0 <= battery <= 100):
        errors.append(f"battery: 數值 {battery} 超出合法範圍 (0~100)")

    # speed
    speed = data.get("speed")
    if not isinstance(speed, (int, float)):
        errors.append("speed: 必須是數字")
    elif speed < 0:
        errors.append(f"speed: 不可為負數 ({speed})")
    elif speed > 200:
        errors.append(f"speed: 數值 {speed} 不合理（超過 200 km/h）")

    # status
    valid_statuses = {"in_use", "idle", "reserved", "maintenance"}
    status = data.get("status")
    if status not in valid_statuses:
        errors.append(f"status: 不合法的值 '{status}'，允許值為 {valid_statuses}")

    return errors


def decide_command(battery):
    if battery <= 5:
        return "lock"
    elif battery <= 15:
        return "slow_down"
    return "none"


@app.route("/api/v1/vehicle/telemetry", methods=["POST"])
def telemetry():
    if not request.is_json:
        return jsonify({"error": "Content-Type 必須為 application/json"}), 415

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body 無法解析為 JSON"}), 400

    errors = validate_telemetry(data)
    if errors:
        return jsonify({"error": "參數驗證失敗", "details": errors}), 400

    command = decide_command(data["battery"])

    print(
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"vehicle={data['vehicle_id']} battery={data['battery']}% "
        f"speed={data['speed']} → command={command}"
    )

    return jsonify({"command": command, "message": "OK"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    print("GoScoot Mock Server 啟動中...")
    print("端點: POST http://localhost:5000/api/v1/vehicle/telemetry")
    print("按 Ctrl+C 停止\n")
    app.run(port=5000, debug=False)
