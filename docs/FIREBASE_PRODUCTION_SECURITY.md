# Firebase Production Security Setup

This repository already tests Cloud Storage Security Rules in the Firebase Emulator Suite. The remaining production step is to authorize GitHub Actions to deploy those tested rules and configure Firebase App Check.

## Project

- Firebase / Google Cloud project: `my-attendance-c5c23`
- Project number: `312314814209`
- Android app ID: `1:312314814209:android:764780f6a72c65b9a38500`
- Android package: `com.personal.attendance`

## 1. Create a least-privilege deployment service account

In Google Cloud Console, open project `my-attendance-c5c23` and create a service account named for example:

`github-firebase-deployer`

Grant only these roles:

- **Firebase Rules Admin** — `roles/firebaserules.admin`
- **Firebase App Check Admin** — `roles/firebaseappcheck.admin`

Do not grant Owner or Editor.

Create one JSON key for this service account. Treat the JSON as a secret.

## 2. Add the JSON to GitHub Actions

Repository:

`ghargaathadesign-oss/MyAttendanceAndroid`

Open:

**Settings → Secrets and variables → Actions → New repository secret**

Name:

`FIREBASE_SERVICE_ACCOUNT_JSON`

Paste the entire service-account JSON file as the value.

Never commit this JSON file to the repository.

## 3. Confirm the Firebase App Check API can be called

In Google Cloud Console:

**APIs & Services → Enabled APIs & services**

Confirm **Firebase App Check API** (`firebaseappcheck.googleapis.com`) is enabled.

If the Firebase Android API key has **API restrictions**, edit the key and make sure **Firebase App Check API** is allowed. This is important because an earlier build received a 403 from `firebaseappcheck.googleapis.com`.

## 4. Run the production-security workflow

Open GitHub:

**Actions → Firebase Production Security → Run workflow**

For the first run use:

- Deploy Storage Rules: **ON**
- Configure App Check: **ON**
- Enforce App Check: **OFF**

This run will:

1. Test the Storage Rules in the emulator.
2. Deploy the tested rules to production.
3. Configure Play Integrity for an app distributed outside Google Play:
   - unrecognized/off-Play version allowed
   - Google Play license not required
   - minimum device recognition: `MEETS_DEVICE_INTEGRITY`
4. Put Cloud Storage App Check into **UNENFORCED / monitoring-only** mode.

Monitoring-only mode collects App Check metrics without blocking users.

## 5. Enable the App Check client in the Android build

After the first production workflow succeeds, enable the Android App Check client in the next APK build.

The current v13.2 build intentionally has App Check disabled by default until the backend is ready.

After installing that App Check-enabled APK:

1. Sign in.
2. Run **Backup Now**.
3. Run **Restore**.
4. Confirm no 403 App Check error occurs.
5. Check Firebase Console → Security → App Check metrics for Cloud Storage.

## 6. Enforce only after verified traffic is healthy

When legitimate requests are showing as verified, run **Firebase Production Security** again with:

- Deploy Storage Rules: optional
- Configure App Check: ON
- Enforce App Check: **ON**

This changes Cloud Storage from monitoring-only to enforced.

Do not enable enforcement before the App Check-enabled APK has been tested, because old app versions that do not send valid App Check tokens would be rejected.

## Security notes

- The service account has only Rules and App Check administration roles.
- The service-account key must remain only in GitHub Actions Secrets.
- Cloud Storage Security Rules and App Check are complementary: rules authorize the signed-in user; App Check verifies that traffic comes from an approved app/device.
- The workflow does not auto-enforce App Check on ordinary pushes.
