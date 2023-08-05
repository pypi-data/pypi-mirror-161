import pytest

from fiddler import FiddlerApi


def test_client_v1_creation_fail():
    with pytest.raises(ValueError) as e:
        client_v1 = FiddlerApi('', '', '')


def test_client_v2_creation_fail():
    with pytest.raises(ValueError) as e:
        client_v2 = FiddlerApi('', '', '', version=2)
