"""Sayd package."""

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

__all__ = ("SaydServer", "SaydClient")
__version__ = "1.1.2"

__author__ = "LW016"
__license__ = "Apache License, Version 2.0"


from ._server import SaydServer
from ._client import SaydClient
