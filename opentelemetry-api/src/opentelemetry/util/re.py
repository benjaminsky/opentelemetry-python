# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from re import compile, split
from typing import Mapping

_logger = logging.getLogger(__name__)


# https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#specifying-headers-via-environment-variables
_OWS = r"[ \t]*"
# A key contains one or more US-ASCII character except CTLs or separators.
_KEY_FORMAT = (
    r"[\x21\x23-\x27\x2a\x2b\x2d\x2e\x30-\x39\x41-\x5a\x5e-\x7a\x7c\x7e]+"
)
# A value contains a URL encoded UTF-8 string.
_VALUE_FORMAT = r"[\x21\x23-\x2b\x2d-\x3a\x3c-\x5b\x5d-\x7e]*"
_HEADER_FORMAT = _KEY_FORMAT + _OWS + r"=" + _OWS + _VALUE_FORMAT
_HEADER_PATTERN = compile(_HEADER_FORMAT)
_DELIMITER_PATTERN = compile(r"[ \t]*,[ \t]*")


# pylint: disable=invalid-name
def parse_headers(s: str) -> Mapping[str, str]:
    """
    Parse ``s`` (a ``str`` instance containing HTTP headers). Uses W3C Baggage
    HTTP header format https://www.w3.org/TR/baggage/#baggage-http-header-format, except that
    additional semi-colon delimited metadata is not supported.
    """
    headers = {}
    for header in split(_DELIMITER_PATTERN, s):
        if not header:  # empty string
            continue
        match = _HEADER_PATTERN.fullmatch(header.strip())
        if not match:
            _logger.warning("Header doesn't match the format: %s.", header)
            continue
        # value may contain any number of `=`
        name, value = match.string.split("=", 1)
        name = name.strip().lower()
        value = value.strip()
        headers[name] = value

    return headers
