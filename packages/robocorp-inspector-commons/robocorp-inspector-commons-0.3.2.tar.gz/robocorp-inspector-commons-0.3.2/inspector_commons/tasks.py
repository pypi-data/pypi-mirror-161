import hashlib
import json
import platform
import shutil
from contextlib import contextmanager
from glob import glob
from pathlib import Path

from invoke import task

CLEAN_PATTERNS = [
    "dist",
    ".cache",
    ".pytest_cache",
    "**/__pycache__",
    "**/**/__pycache__",
    "**/*.pyc",
    "**/**/*.pyc",
    "**/*.egg-info",
]

NPMRC = """\
registry=https://registry.npmjs.org/
@robocorp:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken={}
"""


class Cache:
    PATH = ".taskcache.json"

    def __init__(self):
        self.data = {}

    def load(self):
        try:
            with open(self.PATH, "r") as fd:
                self.data = json.load(fd)
        except FileNotFoundError:
            print(f"Cache file does not exist: {self.PATH}")
            self.data = {}

    def update(self, path):
        self.data[path] = self._digest(path)
        with open(self.PATH, "w") as fd:
            json.dump(self.data, fd)

    def check(self, path):
        try:
            current = self._digest(path)
        except FileNotFoundError:
            print(f"Cache target does not exist: {path}")
            return False

        try:
            stored = self.data.get(path)
        except Exception as exc:
            print(f"Malformed cache file: {exc}")
            Path(self.PATH).unlink()
            self.data = {}
            return False

        if current != stored:
            print(f"Cache target changed: {path}")
            return False
        else:
            print(f"Cache target not changed: {path}")
            return True

    @staticmethod
    def _digest(path):
        with open(path, "rb") as fd:
            return hashlib.md5(fd.read()).hexdigest()


@contextmanager
def ensure_cache(*paths):
    cache = Cache()
    cache.load()

    yield all(cache.check(path) for path in paths)

    for path in paths:
        cache.update(path)


def npmrc(token):
    with open(".npmrc", "w") as fd:
        fd.write(NPMRC.format(token))


def yarn(ctx, command, **kwargs):
    kwargs.setdefault("echo", True)
    if platform.system() != "Windows":
        kwargs.setdefault("pty", True)
    ctx.run(f"yarn {command}", **kwargs)


def poetry(ctx, command, **kwargs):
    kwargs.setdefault("echo", True)
    if platform.system() != "Windows":
        kwargs.setdefault("pty", True)
    ctx.run(f"poetry {command}", **kwargs)


@task
def clean(ctx):
    """Remove all generated files"""
    for pattern in CLEAN_PATTERNS:
        for path in glob(pattern):
            print(f"Removing: {path}")
            shutil.rmtree(path, ignore_errors=True)

    yarn(ctx, "clean")


@task(help={"token": "Auth token for local .npmrc"})
def install(ctx, token="", force=False):
    """Install development environment"""
    if token:
        npmrc(token)

    with ensure_cache("pyproject.toml") as cached:
        if not cached or force:
            poetry(ctx, "lock")

    with ensure_cache("poetry.lock") as cached:
        if not cached or force:
            poetry(ctx, "install")

    with ensure_cache("package.json", "yarn.lock") as cached:
        if not cached or force:
            yarn(ctx, "install --immutable")


@task
def install_hooks(ctx):
    """Configure git hooks"""
    ctx.run("git config core.hooksPath ./config/git-hooks/")


@task(install)
def lint(ctx):
    """Run autoformat and static analysis"""
    poetry(ctx, "run black --check inspector")
    poetry(ctx, "run flake8 --config .flake8 inspector")
    poetry(ctx, "run pylint --rcfile .pylintrc inspector")
    yarn(ctx, "lint")


@task(install)
def pretty(ctx):
    """Run code formatter on source files"""
    poetry(ctx, "run black inspector")
    yarn(ctx, "pretty")


@task(install)
def typecheck(ctx):
    """Run static type checks"""
    # TODO: Add --strict mode
    poetry(ctx, "run mypy inspector")
    yarn(ctx, "typecheck")


@task(install)
def test(ctx):
    """Run unittests"""
    poetry(ctx, "run pytest -v tests/")
    yarn(ctx, "test")


@task(lint, typecheck, test)
def check(ctx):
    """Run all checks"""
    pass


@task(install)
def build_js(ctx):
    """Build javascript files"""
    yarn(ctx, "build")


@task(lint, typecheck, test, build_js)
def build(ctx):
    """Build distributable python package"""
    poetry(ctx, "run python tools/version.py")
    poetry(ctx, "build -v")


@task(install, build_js)
def run(ctx):
    """Start inspector"""
    poetry(ctx, "run inspector --verbose")


@task(clean, build, help={"ci": "Publish package to devpi instead of PyPI"})
def publish(ctx, ci=False):
    """Publish python package"""
    if ci:
        poetry(ctx, "publish -v --no-interaction --repository devpi")
    else:
        poetry(ctx, "publish -v")


@task(install)
def storybook(ctx):
    """Start UI component explorer"""
    poetry(ctx, "run yarn storybook")


@task(install)
def robot(ctx, macos=False):
    """Set devpi credentials for example robot"""
    cmd = "run python tools/robot_writer.py"
    if macos:
        cmd += " --macos"

    poetry(ctx, cmd)
