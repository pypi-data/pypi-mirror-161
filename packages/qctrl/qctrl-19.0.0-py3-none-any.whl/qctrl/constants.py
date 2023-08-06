# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring

BASE_URL = "https://{}.q-ctrl.com"
DEFAULT_API_ROOT = BASE_URL.format("api")
DEFAULT_OIDC_URL = BASE_URL.format("id")
OIDC_CLIENT_ID = "boulder-opal-python"
UNIVERSAL_ERROR_MESSAGE = (
    "Oops, something went wrong. Please start again or contact support@q-ctrl.com"
)

UNEXPECTED_TOKEN_ERROR = """
---------------------------------------------------------------------
An error occurred with your session authentication. Please try again.
If the issue persists, recreate your environment authentication by
running `qctrl auth` from the command line.

For non-interactive or alternative options check our help:

    $ qctrl auth --help

---------------------------------------------------------------------
"""

INVALID_SUBSCRIPTION_ERROR = """
---------------------------------------------------------------------
Your authentication succeeded, but your subscription is invalid for
this product.

Please access `https://boulder.q-ctrl.com` for more details.
---------------------------------------------------------------------
"""
