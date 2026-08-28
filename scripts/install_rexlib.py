"""Build and install the rexlib this binding wraps.

CI runs this once per platform before building wheels, so that the
per-interpreter builds only have to compile the binding itself rather than
the whole C++ library. It is also the quickest way to get a development
machine ready.

The commit is read from CMakeLists.txt so that it is pinned in one place.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ARCHIVE = "https://github.com/gigabit-clowns/rexlib/archive/{commit}.tar.gz"
COMMIT = re.compile(r"REXLIB_PYTHON_REXLIB_COMMIT\s+([0-9a-f]{7,40})")


def read_pinned_commit(project: pathlib.Path) -> str:
	"""Read the pinned rexlib commit out of the project's CMakeLists.txt."""
	text = (project / "CMakeLists.txt").read_text()
	match = COMMIT.search(text)
	if not match:
		raise SystemExit("No REXLIB_PYTHON_REXLIB_COMMIT in CMakeLists.txt")
	return match.group(1)


def download(commit: str, into: pathlib.Path) -> pathlib.Path:
	"""Download and unpack a rexlib source archive, returning its root."""
	archive = into / "rexlib.tar.gz"
	urllib.request.urlretrieve(ARCHIVE.format(commit=commit), archive)
	with tarfile.open(archive) as tar:
		tar.extractall(into)  # noqa: S202 -- our own archive, from GitHub
	return next(p for p in into.iterdir() if p.is_dir())


def build(
	source: pathlib.Path, prefix: pathlib.Path, build_dir: pathlib.Path
) -> None:
	"""Configure, build and install rexlib into the prefix."""
	subprocess.run(
		[
			"cmake", "-S", str(source), "-B", str(build_dir),
			"-DCMAKE_BUILD_TYPE=Release",
			f"-DCMAKE_INSTALL_PREFIX={prefix}",
			"-DCMAKE_INSTALL_LIBDIR=lib",  # never lib64, so staging is uniform
			"-DBUILD_TESTING=OFF",
		],
		check=True,
	)
	subprocess.run(
		[
			"cmake", "--build", str(build_dir),
			"--config", "Release", "--target", "install", "--parallel",
		],
		check=True,
	)


def main() -> None:
	"""Parse the arguments and install rexlib."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--prefix", required=True, type=pathlib.Path)
	parser.add_argument("--commit", help="Defaults to the CMakeLists pin.")
	parser.add_argument(
		"--build-dir", type=pathlib.Path,
		help="Kept between runs so a compiler cache can be reused.",
	)
	args = parser.parse_args()

	project = pathlib.Path(__file__).resolve().parent.parent
	commit = args.commit or read_pinned_commit(project)

	if (args.prefix / "lib" / "cmake" / "rexlib").is_dir():
		print(f"rexlib already installed in {args.prefix}", file=sys.stderr)
		return

	with tempfile.TemporaryDirectory() as tmp:
		source = download(commit, pathlib.Path(tmp))
		build_dir = args.build_dir or pathlib.Path(tmp) / "build"
		build_dir.mkdir(parents=True, exist_ok=True)
		build(source, args.prefix.resolve(), build_dir)
		if args.build_dir is None:
			shutil.rmtree(build_dir, ignore_errors=True)


if __name__ == "__main__":
	main()
