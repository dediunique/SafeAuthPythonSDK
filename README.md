## Overview

SafeAuth is a Python SDK for license management, user authentication, and session management. It provides a secure way to verify software licenses and user credentials, supporting multi-platform hardware ID generation for enhanced security.

## Features

- Hardware ID generation for Windows, macOS, and Linux
- License key verification
- User authentication
- AES encryption for secure data transmission
- Session management with heartbeat mechanism
- Cross-platform compatibility

## Installation

- Download repo
- Put pythonsdk.py in the same project as your python application
- Check Quick Start/Usage Examples

## Quick Start

```python
from pythonsdk import LicenseManager

# Initialize the license manager
lm = LicenseManager("your_application_name")

# Start a session with the authentication server
success, token = lm.init()
if not success:
    raise Exception(f"Connection failed: {token}")

# Verify a license key
license_key = "your_license_key"
success, session_token, data = lm.verify_license(license_key)

if success:
    print(f"License verified. Expires at: {data['expires_at']}")
    print(f"Expiration date: {data['expires_at']}")
else:
    print(f"License verification failed: {session_token}")
```

## Usage Examples

### License Verification

```python
# Initialize the manager and verify a license
lm = LicenseManager("your_app_name")
success, token = lm.init()

license_key = "your_license_key"
success, session_token, data = lm.verify_license(license_key)

if success:
    print("License is valid!")
    print(f"Expiration date: {data['expires_at']}")
else:
    print(f"License validation failed: {session_token}")
```

### User Authentication

```python
# Initialize the manager and verify user credentials
lm = LicenseManager("your_app_name")
success, token = lm.init()

username = "your_username"
password = "your_password"
success, session_token, data = lm.verify_user(username, password)

if success:
    print(f"User authenticated successfully!")
    print(f"Session expires at: {data['expires_at']}")
else:
    print(f"Authentication failed: {session_token}")
```

### Session Management with Heartbeat

```python
import time

# Initialize and verify
lm = LicenseManager("your_app_name")
success, token = lm.init()
success, session_token, data = lm.verify_license("your_license_key")

if success:
    # Keep the session alive with heartbeats
    while True:
        success, expires_at = lm.heartbeat(session_token)
        if not success:
            print(f"Heartbeat failed: {expires_at}")
            break
        print(f"Session active, expires at {expires_at}")
        time.sleep(300)  # Send heartbeat every 5 minutes
```

## API Reference

### LicenseManager

#### `__init__(app_name)`

Initialize a new instance of the license manager.

- **Parameters**:
  - `app_name`: The name of your application

#### `init()`

Initialize a session with the authentication server.

- **Returns**: `(success: bool, token_or_error: str)`

#### `verify_license(license_key)`

Verify a license key with the server.

- **Parameters**:
  - `license_key`: The license key to verify
- **Returns**: `(success: bool, session_token_or_error: str, data: dict)`

#### `verify_user(username, password)`

Authenticate a user with username and password.

- **Parameters**:
  - `username`: User's username
  - `password`: User's password
- **Returns**: `(success: bool, session_token_or_error: str, data: dict)`

#### `heartbeat(session_token=None)`

Send a heartbeat to keep the session alive.

- **Parameters**:
  - `session_token`: Optional session token (uses the stored token if not provided)
- **Returns**: `(success: bool, expires_at_or_error: str)`

## Security

The SDK uses AES encryption for sensitive data and generates a unique hardware ID to prevent unauthorized use of licenses. All communication with the server is done over HTTPS.

## License

Copyright (c) 2025 SafeAuth