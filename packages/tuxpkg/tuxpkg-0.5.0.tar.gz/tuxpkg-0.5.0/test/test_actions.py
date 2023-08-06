import os

from pathlib import Path
from tuxpkg.actions import Action
from tuxpkg.actions import PointToFile
from tuxpkg.actions import RunScript
from tuxpkg.actions import CopyDirectory
from tuxpkg.actions import CompositeAction


class TestAction:
    def test_is_callable(self):
        action = Action()
        action()


class TestPointToFile:
    def test_shows_content(self, capsys):
        action = PointToFile("tuxpkg.mk")
        action()
        out, _ = capsys.readouterr()
        file = Path(out.strip())
        assert file.exists


class TestRunScript:
    def test_runs_script(self, mocker):
        execv = mocker.patch("os.execv")
        run_script = RunScript("create-repository")
        run_script()
        execv.assert_called()
        script_path = Path(execv.call_args[0][0])
        assert script_path.name == "create-repository"
        assert script_path.exists()
        assert type(execv.call_args[0][1]) in [list, tuple]


class TestCopyDirectory:
    def test_copies_files(self, tmp_path):
        cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            action = CopyDirectory("init")
            action()
        finally:
            os.chdir(cwd)

        # copies files
        assert (tmp_path / "Dockerfile.ci-fedora").exists()
        # subdirectories
        assert (tmp_path / "debian" / "rules").exists()
        # template expansion
        assert tmp_path.name in (tmp_path / "Makefile").read_text()
        # template expansion in directory names
        name = tmp_path.name
        assert (tmp_path / name / "__init__.py").exists()
        # template expansion in template names
        assert (tmp_path / name).with_suffix(".spec").exists()
        # file mode
        assert os.access(str(tmp_path / "debian" / "rules"), os.X_OK)

    def test_wont_override_existing_files(self, tmp_path):
        cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            Path("Makefile").write_text("")  # template
            Path("Dockerfile.ci-fedora").write_text("")  # regular file
            action = CopyDirectory("init")
            action()
        finally:
            os.chdir(cwd)

        assert (tmp_path / "Makefile").read_text() == ""
        assert (tmp_path / "Dockerfile.ci-fedora").read_text() == ""


class TestCompositeAction:
    def test_runs_all_subactions(self):
        class TestAction(Action):
            called = False

            def __call__(self):
                self.called = True

        action1 = TestAction()
        action2 = TestAction()
        composite = CompositeAction(action1, action2)
        composite()
        assert action1.called
        assert action2.called
