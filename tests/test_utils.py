from gg import utils


def test_call_and_error():
    command = 'ls -l'
    out, err = utils.call_and_error(command)
    assert out
    assert err == ''
