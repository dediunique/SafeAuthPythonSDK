from app.example.pythonsdk import LicenseManager
import time

lm = LicenseManager("tsaasdasd")

success, token = lm.init()
if not success:
    raise Exception(f"Init failed: {token}")

license_key = "df32e2e1fdf2252ddc8cb7ca5f25f1b5"
success, session_or_error, data = lm.verify_license(license_key)

if not success:
    raise Exception(f"License verification failed: {session_or_error}")

print(f"License verified. Session token: {session_or_error}")
print(f"Data: {data}")

username = "tsa_rewk1"
password = "test"
success, session_or_error, data = lm.verify_user(username, password)

if not success:
    raise Exception(f"User verification failed: {session_or_error}")

print(f"User verified. Session token: {session_or_error}")
print(f"Data: {data}")
print("License verified, session started.")

while True:
    success, expires_at = lm.heartbeat(session_or_error)
    if not success:
        print(f"Heartbeat error: {expires_at}")
        break
    print(f"Key expires at {expires_at}")
    time.sleep(300)
