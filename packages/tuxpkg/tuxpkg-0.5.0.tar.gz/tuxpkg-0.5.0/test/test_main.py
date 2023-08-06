import pytest
import sys
import tuxpkg.__main__ as main_module


@pytest.fixture
def argv():
    return ["tuxpkg"]


@pytest.fixture(autouse=True)
def patch_argv(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)


class TestMain:
    def test_calls_main(self, monkeypatch, mocker):
        monkeypatch.setattr(main_module, "__name__", "__main__")
        main = mocker.patch("tuxpkg.__main__.main", return_value=0)
        exit = mocker.patch("sys.exit")
        main_module.run()
        main.assert_called()
        exit.assert_called_with(0)

    def test_main(self):
        assert main_module.main() == 0

    def test_help(self, argv, capsys):
        argv.append("--help")
        with pytest.raises(SystemExit):
            main_module.main()
        out, _ = capsys.readouterr()
        assert "usage:" in out

    def test_get_makefile(self, argv, mocker):
        argv.append("get-makefile")
        main_module.main()
