"""CLI utility to generate self-signed certificates."""

# Copyright 2022 LW016 (GPG FINGERPRINT 33CA C1E8 EC4C 0B31 73AE  DD8B 31A5 35D1 2844 39ED)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from typer import run

from OpenSSL import crypto


def main(
        cert_output: str = "cert.crt",
        key_output: str = "cert.key",
        country: str = "BR",
        state: str = "Sao Paulo",
        locality: str = "Sao Paulo",
        org: str = "Local",
        org_unity: str = "Local",
        common_name: str = "localhost",
        exp_days: int = 365,
        email: Optional[str] = None
        ) -> None:
    """Generates a self-signed certificate."""

    # Create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    
    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = country
    cert.get_subject().ST = state
    cert.get_subject().L = locality
    cert.get_subject().O = org
    cert.get_subject().OU = org_unity
    cert.get_subject().CN = common_name

    if email is not None:
        cert.get_subject().emailAddress = email

    
    cert.set_serial_number(1000)

    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(exp_days * ((60*60)*24))

    
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    
    # Save certificate
    with open(cert_output, "wb") as file:
        file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    
    # Save key
    with open(key_output, "wb") as file:
        file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))


def execute() -> None:
    """Script entry point."""

    run(main)


if __name__ == "__main__":
    execute()
