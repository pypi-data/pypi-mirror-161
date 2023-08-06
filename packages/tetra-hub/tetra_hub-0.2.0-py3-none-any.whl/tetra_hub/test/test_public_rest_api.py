import pytest
from unittest.mock import MagicMock
import tetra_hub.public_rest_api as api

OLD_APIT_RESUTS = None


def setup_module(module):
    global OLD_APIT_RESUTS
    OLD_APIT_RESUTS = api.requests


def teardown_module(module):
    api.requests = OLD_APIT_RESUTS


def test_rate_limit_get():
    api.requests = MagicMock()
    rval = MagicMock()
    rval.status_code = 429
    api.requests.get = MagicMock(return_value=rval)

    with pytest.raises(api.APIException) as e:
        api.get_model(1)

    assert e.value.status_code == 429  # too many requests
