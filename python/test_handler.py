import pytest
import json
import sys
import os
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            './'
        )
    )
)
import layer_name


@pytest.fixture()
def setup():
    print("setting up")
    return {
        "event": {
            "temp1": "test"
        },
        "expected_body": "test"
    }


@pytest.mark.parametrize("expected", [
    ("Good Day from CloudBot!")
])
def test_response_exists_bootstrapMethod(expected):
    result = layer_name.bootstrapMethod()
    assert result == expected
