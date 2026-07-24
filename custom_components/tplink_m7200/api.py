"""Minimal client for the TP-Link M7200 MiFi web API.

Ported from the (PHP) reference lib mt-ks/tp-link-m7200-api.

Auth scheme: the device hands out a per-session RSA public key + nonce + seq.
We invent an AES-128-CBC session key/iv, RSA-sign a small param block carrying
them, and from then on every call ships an AES-encrypted `data` blob plus that
`sign`. Responses come back AES-encrypted with the same key/iv.
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import string
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT_HOST = "192.168.0.1"


class M7200Error(Exception):
    """Any login / request failure."""


def _rand16() -> bytes:
    """16 ASCII bytes — valid AES-128 key, and round-trips through urlencode."""
    return "".join(secrets.choice(string.digits) for _ in range(16)).encode()


def _pad(b: bytes) -> bytes:
    p = 16 - len(b) % 16
    return b + bytes([p]) * p


def _unpad(b: bytes) -> bytes:
    return b[: -b[-1]]


class M7200Client:
    def __init__(self, password: str, host: str = DEFAULT_HOST, timeout: int = 10):
        self._pw = password
        self._base = f"http://{host}/cgi-bin"
        self._timeout = timeout
        self._key = b""
        self._iv = b""
        self._seq = 0
        self._rsa = (0, 0)  # (n, e), filled on login
        self.token = ""

    # --- crypto -----------------------------------------------------------
    def _aes_enc(self, text: str) -> str:
        enc = Cipher(algorithms.AES(self._key), modes.CBC(self._iv)).encryptor()
        return base64.b64encode(enc.update(_pad(text.encode())) + enc.finalize()).decode()

    def _aes_dec(self, b64: str) -> str:
        dec = Cipher(algorithms.AES(self._key), modes.CBC(self._iv)).decryptor()
        return _unpad(dec.update(base64.b64decode(b64)) + dec.finalize()).decode()

    def _rsa_sign(self, params: dict) -> str:
        n, e = self._rsa
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        data = urllib.parse.urlencode(params).encode()
        block = (n.bit_length() + 7) // 8 - 11  # PKCS#1 v1.5 max per block
        # ponytail: chunk so it works whatever the device key size is; the
        # device decrypts fixed keylen-sized blocks and concatenates.
        out = b"".join(
            pub.encrypt(data[i : i + block], padding.PKCS1v15())
            for i in range(0, len(data), block)
        )
        return out.hex()

    # --- transport --------------------------------------------------------
    def _post(self, path: str, fields: dict) -> str:
        req = urllib.request.Request(
            f"{self._base}/{path}",
            data=json.dumps(fields).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "okhttp/3.11.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as r:
                return r.read().decode()
        except OSError as err:
            raise M7200Error(f"POST {path} failed: {err}") from err

    # --- api --------------------------------------------------------------
    def login(self) -> str:
        # step 1: fetch nonce / rsa key / seq (plain base64, not encrypted)
        r = self._post(
            "auth_cgi",
            {"data": base64.b64encode(
                json.dumps({"module": "authenticator", "action": 0}).encode()
            ).decode()},
        )
        try:
            info = json.loads(base64.b64decode(r))
            self._seq = int(info["seqNum"])
            self._rsa = (int(info["rsaMod"], 16), int(info["rsaPubKey"], 16))
            nonce = info["nonce"]
        except (ValueError, KeyError) as err:
            raise M7200Error(f"bad auth handshake: {err}") from err

        # step 2: prove password knowledge, get token
        self._key, self._iv = _rand16(), _rand16()
        digest = hashlib.md5(f"{self._pw}:{nonce}".encode()).hexdigest()
        data = self._aes_enc(
            json.dumps({"module": "authenticator", "action": 1, "digest": digest})
        )
        sign = self._rsa_sign({
            "key": self._key.decode(),
            "iv": self._iv.decode(),
            "h": hashlib.md5(f"admin{self._pw}".encode()).hexdigest(),
            "s": self._seq + len(data),
        })
        r = self._post("auth_cgi", {"data": data, "sign": sign})
        try:
            self.token = json.loads(self._aes_dec(r))["token"]
        except (ValueError, KeyError) as err:
            raise M7200Error("login failed (wrong password?)") from err
        return self.token

    def invoke(self, module: str, action: int, data=None) -> dict:
        payload = {"token": self.token, "module": module, "action": action}
        if data is not None:
            payload["data"] = data
        enc = self._aes_enc(json.dumps(payload))
        sign = self._rsa_sign({
            "h": hashlib.md5(f"admin{self._pw}".encode()).hexdigest(),
            "s": self._seq + len(enc),
        })
        r = self._post("web_cgi", {"data": enc, "sign": sign})
        try:
            return json.loads(self._aes_dec(r))
        except ValueError as err:
            raise M7200Error(f"{module}/{action} decode failed: {err}") from err

    def get_status(self) -> dict:
        return self.invoke("status", 0)

    def get_flowstat(self) -> dict:
        return self.invoke("flowstat", 0)

    def reboot(self) -> dict:
        return self.invoke("reboot", 0)


def _demo() -> None:
    """Offline self-check: crypto round-trips without touching a device."""
    c = M7200Client("pw")
    c._key, c._iv = _rand16(), _rand16()
    assert c._aes_dec(c._aes_enc("hello world")) == "hello world"
    assert c._aes_dec(c._aes_enc("x" * 100)) == "x" * 100  # multi-block
    k = rsa.generate_private_key(public_exponent=65537, key_size=1024).public_key()
    nums = k.public_numbers()
    c._rsa = (nums.n, nums.e)
    sig = c._rsa_sign({"key": c._key.decode(), "iv": c._iv.decode(), "h": "a" * 32, "s": 5})
    assert sig and int(sig, 16)  # produced valid hex
    print("api self-check OK")


if __name__ == "__main__":
    _demo()
