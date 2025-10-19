"""
Bootstrap script to create a bearer token and self-signed TLS certificate
for the SOS orchestrator.
"""

from __future__ import annotations

import datetime
import pathlib
import secrets

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

SECURITY_DIR = pathlib.Path("_validation/security")
TOKEN_PATH = SECURITY_DIR / "sos_token.txt"
CERT_PATH = SECURITY_DIR / "sos_cert.pem"
KEY_PATH = SECURITY_DIR / "sos_key.pem"


def bootstrap_security(force: bool = False) -> str:
    """
    Generate a bearer token and a self-signed certificate if they do not exist.
    Returns the token string for logging purposes.
    """
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)

    if force or not TOKEN_PATH.exists():
        token = secrets.token_urlsafe(32)
        TOKEN_PATH.write_text(token, encoding="utf-8")
    else:
        token = TOKEN_PATH.read_text(encoding="utf-8").strip()

    if force or not (CERT_PATH.exists() and KEY_PATH.exists()):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Intamia LLC"),
                x509.NameAttribute(NameOID.COMMON_NAME, "sos.local"),
            ]
        )
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(private_key, hashes.SHA256())
        )

        CERT_PATH.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        KEY_PATH.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    print(f"Token -> {token}\nCerts in {SECURITY_DIR}")
    return token


if __name__ == "__main__":
    bootstrap_security()
