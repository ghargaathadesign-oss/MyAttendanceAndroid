#!/usr/bin/env python3
import hashlib
import json
import os
import sys

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "my-attendance-c5c23").strip()
TOPIC = os.environ.get("FCM_TOPIC", "attendance_updates").strip()
TOPICS = []
for _topic in [TOPIC, "attendance_all"]:
    if _topic and _topic not in TOPICS:
        TOPICS.append(_topic)
VERSION = os.environ["UPDATE_VERSION"].strip()
VERSION_CODE = os.environ["UPDATE_VERSION_CODE"].strip()
APK_URL = os.environ["UPDATE_APK_URL"].strip()
APK_SHA256 = os.environ["UPDATE_APK_SHA256"].strip().lower()
CHANGELOG = os.environ.get("UPDATE_CHANGELOG", "").strip()
SERVICE_ACCOUNT_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()

if not SERVICE_ACCOUNT_JSON:
    print("FIREBASE_SERVICE_ACCOUNT_JSON is not configured; update push was not sent.", file=sys.stderr)
    sys.exit(3)

if not APK_URL.startswith("https://"):
    raise SystemExit("Update APK URL must use HTTPS.")
if len(APK_SHA256) != 64 or any(c not in "0123456789abcdef" for c in APK_SHA256):
    raise SystemExit("Update APK SHA-256 is invalid.")

info = json.loads(SERVICE_ACCOUNT_JSON)
project_id = info.get("project_id") or PROJECT_ID
credentials = service_account.Credentials.from_service_account_info(
    info,
    scopes=["https://www.googleapis.com/auth/firebase.messaging"],
)
credentials.refresh(Request())

title = f"My Attendance v{VERSION} is available"
body = "A new My Attendance update is ready. Tap to review and install."

url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; UTF-8",
}
for topic in TOPICS:
    payload = {
        "message": {
            "topic": topic,
            "notification": {"title": title, "body": body},
            "data": {
                "id": f"update-{VERSION_CODE}",
                "type": "update",
                "title": title,
                "body": body,
                "version": VERSION,
                "versionCode": VERSION_CODE,
                "apkUrl": APK_URL,
                "sha256": APK_SHA256,
                "changelog": CHANGELOG,
            },
            "android": {
                "priority": "high",
                "notification": {
                    "channel_id": "attendance_updates",
                    "default_sound": True,
                },
            },
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if not r.ok:
        print(r.text, file=sys.stderr)
        r.raise_for_status()
    result = r.json()
    print(f"FCM update notification sent to {topic}:", result.get("name", "ok"))
