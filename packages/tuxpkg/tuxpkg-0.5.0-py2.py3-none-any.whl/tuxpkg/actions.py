from datetime import datetime
import os
from jinja2 import Template
from pathlib import Path
import shutil


class Action:
    def __call__(self) -> None:
        pass


class FileAction(Action):
    def __init__(self, source: str):
        self.source = source
        self.source_path = Path(__file__).parent / "data" / self.source


class PointToFile(FileAction):
    def __call__(self) -> None:
        print(self.source_path)


get_makefile = PointToFile("tuxpkg.mk")
get_debian_rules = PointToFile("debianrules.mk")


class RunScript(FileAction):
    def __call__(self) -> None:
        os.execv(str(self.source_path), [self.source])


create_repository = RunScript("create-repository")
release = RunScript("release")


class CopyDirectory(FileAction):
    def __init__(self, source: str):
        super().__init__(source)
        self.variables = {
            "project": Path(".").absolute().name,
            "timestamp": datetime.utcnow(),
        }

    def __call__(self) -> None:
        cwd = os.getcwd()
        os.chdir(self.source_path)
        try:
            root = Path(".")
            self.copy(root, Path(cwd).absolute())
        finally:
            os.chdir(cwd)

    def copy(self, source: Path, target: Path) -> None:
        if source.is_dir():
            (target / self.render(str(source))).mkdir(exist_ok=True)
            for child in source.iterdir():
                self.copy(child, target)
        else:
            if source.name.endswith(".jinja2"):
                self.expand_template(source, target)
            else:
                self.copy_file(source, target)

    def expand_template(self, source: Path, target: Path) -> None:
        destname = self.render(str(source.with_suffix("")))
        dest = target / destname
        if dest.exists():
            print(f"  SKIP {destname} (already exists)")
            return
        dest.write_text(self.render(source.read_text()))
        dest.chmod(source.stat().st_mode)
        print(f"CREATE {destname}")

    def copy_file(self, source: Path, target: Path) -> None:
        destname = self.render(str(source))
        dest = target / destname
        if dest.exists():
            print(f"  SKIP {destname} (already exists)")
            return
        shutil.copyfile(str(source), str(dest))
        print(f"CREATE {destname}")

    def render(self, template_text: str) -> str:
        template = Template(template_text)
        return template.render(**self.variables)


class CompositeAction(Action):
    def __init__(self, *actions):
        self.actions = actions

    def __call__(self):
        for action in self.actions:
            action()


init = CompositeAction(CopyDirectory("init"), RunScript("init.sh"))
