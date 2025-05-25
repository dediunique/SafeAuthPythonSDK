import base64
import os
import requests
import platform
import uuid
import socket
import logging
from typing import Tuple, Union, Any

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad


class LicenseManager:
    _cached_hwid = None

    def __init__(self, app_name):
        self.app_name = app_name
        self.session_token = None
        self.hwid = self.get_hwid()
        self.encryption_key = None

    def encrypt_data(self, data):
        if not self.encryption_key:
            return data

        key_bytes = bytes.fromhex(self.encryption_key)
        iv = os.urandom(16)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        padded_data = pad(data.encode(), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

        return base64.b64encode(iv + encrypted_data).decode('utf-8')

    def get_hwid(self) -> str:
        if LicenseManager._cached_hwid:
            return LicenseManager._cached_hwid

        try:
            system = platform.system()
            machine_id = ""

            if system == "Windows":
                import subprocess
                result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    machine_id = result.stdout.strip().split('\n')[-1].strip()
            elif system == "Linux":
                try:
                    with open('/etc/machine-id', 'r') as f:
                        machine_id = f.read().strip()
                except Exception:
                    pass
            elif system == "Darwin":
                import subprocess
                result = subprocess.run(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'IOPlatformUUID' in line:
                            machine_id = line.split('"')[-2]
                            break

            processor = platform.processor() or "unknown"
            node_name = platform.node() or socket.gethostname() or "unknown"
            combined_id = f"{system}:{machine_id}:{processor}:{node_name}"

            hwid = uuid.uuid5(uuid.NAMESPACE_DNS, combined_id).hex
            LicenseManager._cached_hwid = hwid
            return hwid

        except Exception as e:
            logging.warning(f"Error generating hardware ID: {e}")
            mac = uuid.getnode()
            hwid = uuid.uuid5(uuid.NAMESPACE_DNS, str(mac)).hex
            LicenseManager._cached_hwid = hwid
            return hwid

    def _post_request(self, endpoint: str, payload: dict) -> Tuple[bool, Union[dict, str]]:
        url = f"https://safeauth.cc/{endpoint}"
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                return False, f"HTTP Error: {response.status_code} - {response.text}"

            data = response.json()
            if data.get('status') != 'success':
                return False, data.get('message', 'Request failed')

            return True, data

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def init(self):
        payload = {
            'app_name': self.app_name,
            'hwid': self.hwid
        }

        success, response = self._post_request('/init', payload)
        if success:
            if response.get('status') == 'success':
                self.session_token = response.get('token')
                self.encryption_key = response.get('encryption_key')
                return True, self.session_token
            return False, response.get('error', 'Unknown error')
        return False, response

    def verify_license(self, licensekey):
        if not self.encryption_key:
            return False, "Session not initialized", None

        payload = {
            'token': self.session_token,
            'license_key': self.encrypt_data(licensekey),
            'app_name': self.app_name,
            'hwid': self.hwid
        }

        success, response = self._post_request('/verify_license', payload)
        if success and response.get('status') == 'success':
            self.session_token = response.get('session_token')
            data = {
                'expires_at': response.get('expires_at'),
                'application': response.get('application'),
                'message': response.get('message')
            }
            return True, self.session_token, data

        error_msg = response.get('error', 'Unknown error') if success else response
        return False, error_msg, None

    def verify_user(self, username, password):
        if not self.encryption_key:
            return False, "Session not initialized", None

        payload = {
            'token': self.session_token,
            'username': self.encrypt_data(username),
            'password': self.encrypt_data(password),
            'app_name': self.app_name,
            'hwid': self.hwid
        }

        success, response = self._post_request('/verify', payload)
        if success and response.get('status') == 'success':
            self.session_token = response.get('session_token')
            data = {
                'expires_at': response.get('expires_at'),
                'application': response.get('application'),
                'message': response.get('message')
            }
            return True, self.session_token, data

        error_msg = response.get('error', 'Unknown error') if success else response
        return False, error_msg, None

    def heartbeat(self, session_token: Union[str, None] = None) -> Tuple[bool, str]:
        token_to_use = session_token or self.session_token
        if not token_to_use:
            return False, "No session token provided"

        payload = {
            'hwid': self.hwid,
            'session_token': token_to_use,
        }

        success, data = self._post_request('heartbeat', payload)
        if not success:
            return False, data

        expires_at = data.get('expires_at')
        if not expires_at:
            return False, "No expiry received from server"

        return True, expires_at
