import pytest

from github_contrib_awtrix.cli import main


def test_no_flags_prints_help(capsys) -> None:
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: github-contrib-awtrix" in captured.out
    assert captured.err == ""


def test_output_flags_are_not_implemented_yet(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--terminal"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "not implemented yet" in captured.err
