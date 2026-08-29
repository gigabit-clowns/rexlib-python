"""Build and install the rexlib this binding wraps.

CI runs this once per platform before building wheels, so that the
per-interpreter builds only have to compile the binding itself rather than
the whole C++ library. It is also the quickest way to get a development
machine ready.

The commit is read from CMakeLists.txt so that it is pinned in one place.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ARCHIVE = "https://github.com/gigabit-clowns/rexlib/archive/{commit}.tar.gz"

# The rexlib this binding is developed against. Only a default: any
# installation satisfying the version CMakeLists.txt asks for will do.
COMMIT = "474ba80d27c7ace6979b7193db53b3d481804885"


def download(commit: str, into: pathlib.Path) -> pathlib.Path:
	"""Download and unpack a rexlib source archive, returning its root."""
	archive = into / "rexlib.tar.gz"
	urllib.request.urlretrieve(ARCHIVE.format(commit=commit), archive)
	with tarfile.open(archive) as tar:
		tar.extractall(into)
	return next(p for p in into.iterdir() if p.is_dir())


def default_parallelism() -> int:
	"""How many compilers to run at once.

	Never unbounded, which is what `cmake --build --parallel` without a
	number means for a Makefile generator, and which exhausts a CI runner
	here: rexlib's heaviest translation units peak around 2.5 GB each, so
	memory runs out long before cores do.
	"""
	jobs = os.cpu_count() or 1
	try:
		gigabytes = (
			os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 1e9
		)
	except (ValueError, OSError, AttributeError):
		return jobs
	return max(1, min(jobs, int(gigabytes // 2.5)))


def build(
	source: pathlib.Path,
	prefix: pathlib.Path,
	build_dir: pathlib.Path,
	parallel: int,
	compiler_launcher: str | None,
) -> None:
	"""Configure, build and install rexlib into the prefix."""
	subprocess.run(
		[
			"cmake", "-S", str(source), "-B", str(build_dir),
			"-DCMAKE_BUILD_TYPE=Release",
			f"-DCMAKE_INSTALL_PREFIX={prefix}",
			"-DCMAKE_INSTALL_LIBDIR=lib",  # never lib64, so staging is uniform
			"-DBUILD_TESTING=OFF",
			*(
				[
					f"-DCMAKE_C_COMPILER_LAUNCHER={compiler_launcher}",
					f"-DCMAKE_CXX_COMPILER_LAUNCHER={compiler_launcher}",
				]
				if compiler_launcher
				else []
			),
		],
		check=True,
	)
	subprocess.run(
		[
			"cmake", "--build", str(build_dir),
			"--config", "Release", "--target", "install",
			"--parallel", str(parallel),
		],
		check=True,
	)


def main() -> None:
	"""Parse the arguments and install rexlib."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--prefix", required=True, type=pathlib.Path)
	parser.add_argument("--commit", help="Defaults to the CMakeLists pin.")
	parser.add_argument(
		"--parallel", type=int, default=default_parallelism(),
		help="Compilers to run at once. Never unbounded; see the default.",
	)
	parser.add_argument(
		"--compiler-launcher",
		help="Wrapper for each compiler invocation, such as ccache.",
	)
	parser.add_argument(
		"--build-dir", type=pathlib.Path,
		help="Kept between runs so a compiler cache can be reused.",
	)
	args = parser.parse_args()

	commit = args.commit or COMMIT

	if (args.prefix / "lib" / "cmake" / "rexlib").is_dir():
		print(f"rexlib already installed in {args.prefix}", file=sys.stderr)
		return

	with tempfile.TemporaryDirectory() as tmp:
		source = download(commit, pathlib.Path(tmp))
		build_dir = args.build_dir or pathlib.Path(tmp) / "build"
		build_dir.mkdir(parents=True, exist_ok=True)
		build(
			source,
			args.prefix.resolve(),
			build_dir,
			args.parallel,
			args.compiler_launcher,
		)
		if args.build_dir is None:
			shutil.rmtree(build_dir, ignore_errors=True)


if __name__ == "__main__":
	main()
