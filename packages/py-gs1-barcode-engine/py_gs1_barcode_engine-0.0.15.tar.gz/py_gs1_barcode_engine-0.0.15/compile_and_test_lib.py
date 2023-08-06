import pathlib
import shutil
import subprocess
from zipfile import ZipFile
import urllib.request


def execute(build_artifacts_path: pathlib.Path) -> None:
    """build_artifacts_path: Path to copy build outputs to."""

    LIBRARY_NAME = "gs1-barcode-engine"

    build_root_path = pathlib.Path(__file__).resolve().parent
    library_path = build_root_path / LIBRARY_NAME
    library_source_path = library_path / "src" / "c-lib"
    build_output_path = library_source_path / "build"

    shutil.rmtree(library_path, ignore_errors=True)

    archive_path = build_root_path / "archive.zip"
    urllib.request.urlretrieve(
        "https://github.com/gs1/gs1-barcode-engine/archive/refs/tags/2021-09-10.zip",
        archive_path,
    )
    with ZipFile(archive_path, "r") as z:
        z.extractall(build_root_path)
    archive_path.unlink()

    shutil.move("gs1-barcode-engine-2021-09-10", LIBRARY_NAME)

    _ = subprocess.check_output(["make", "test"], cwd=library_source_path)
    _ = subprocess.check_output(["make"], cwd=library_source_path)

    shutil.rmtree(build_artifacts_path, ignore_errors=True)
    shutil.copytree(build_output_path, build_artifacts_path)


if __name__ == "__main__":
    execute(pathlib.Path(__file__).resolve().parent / "build_artifacts")
