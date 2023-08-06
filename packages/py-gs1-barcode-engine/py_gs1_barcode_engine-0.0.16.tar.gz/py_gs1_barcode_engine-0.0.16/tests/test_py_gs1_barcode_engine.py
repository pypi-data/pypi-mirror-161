from pathlib import Path
import pytest
import os
import psutil
from py_gs1_barcode_engine import generate_gs1_datamatrix, Gs1GeneratorError


module_x_dim_mm = 0.7
module_x_dim_inches = module_x_dim_mm * 0.0393701
dpi = 157.35


def save_to_file(filename, data: bytes):
    with open(filename, "wb") as f:
        f.write(data)


@pytest.fixture
def good_barcode_text() -> str:
    return "(01)94210325403182(30)2(3922)0460(93)TQ"


@pytest.fixture(
    params=[
        pytest.param(
            {
                "test_string": "(01)94210325403182(30)2(3922asdasd)0460(93)TQ",
                "expect_string_in_exception": "Unrecognised AI",
            },
            id="Nonsense in middle of valid barcode text",
        ),
        pytest.param(
            {"test_string": "", "expect_string_in_exception": "Missing FNC1"},
            id="Empty string",
        ),
        pytest.param(
            {
                "test_string": "This is nonsense",
                "expect_string_in_exception": "Failed to parse AI data",
            },
            id="This is complete nonsense",
        ),
    ],
)
def bad_barcode_text(request) -> dict:
    return request.param


@pytest.fixture(
    params=[
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 2000,
                    "dm_cols": 22,
                    "x_undercut": 0,
                    "y_undercut": 0,
                    "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
                },
                "expect_string_in_exception": "Valid number of Data Matrix rows range is",
            },
            id="Huge number of rows",
        ),
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 22,
                    "dm_cols": 24000,
                    "x_undercut": 0,
                    "y_undercut": 0,
                    "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
                },
                "expect_string_in_exception": "Valid number of Data Matrix columns range is",
            },
            id="Huge number of columns",
        ),
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 22,
                    "dm_cols": 22,
                    "x_undercut": 900,
                    "y_undercut": 0,
                    "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
                },
                "expect_string_in_exception": "Valid X undercut range is",
            },
            id="Huge X undercut",
        ),
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 22,
                    "dm_cols": 22,
                    "x_undercut": 0,
                    "y_undercut": 900,
                    "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
                },
                "expect_string_in_exception": "Valid Y undercut range is",
            },
            id="Huge Y undercut",
        ),
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 22,
                    "dm_cols": 22,
                    "x_undercut": 0,
                    "y_undercut": 0,
                    "scaling": {
                        "resolution": dpi,
                        "target_x_dim": module_x_dim_inches,
                        "min_x_dim": module_x_dim_inches,
                        "max_x_dim": module_x_dim_inches,
                    },
                },
                "expect_string_in_exception": "Impossible to plot X-dimension of",
            },
            id="Unreasonable/impossible dot scaling constraints",
        ),
        pytest.param(
            {
                "test_params": {
                    "dm_rows": 22,
                    "dm_cols": 22,
                    "x_undercut": 0,
                    "y_undercut": 0,
                    "scaling": {
                        "pix_mult": 5000000,
                    },
                },
                "expect_string_in_exception": "Valid X-dimension range is 1 to 100",
            },
            id="Unreasonable/impossible pixel scaling constraints",
        ),
    ],
)
def bad_generation_params(request) -> dict:
    return request.param


@pytest.fixture
def output_dir() -> Path:
    DIR = ".test_output"
    path = Path(DIR)

    path.mkdir(exist_ok=True)
    for f in path.glob("*.*"):
        f.unlink()

    assert path.is_dir
    assert len(list(path.glob("*.*"))) == 0

    yield path

    assert len(list(path.glob("*.*"))) == 1, "no file created where one was expected"


@pytest.fixture(
    params=[
        pytest.param(
            {
                "dm_rows": 22,
                "dm_cols": 22,
                "x_undercut": 0,
                "y_undercut": 0,
                "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
            },
            id="Standard",
        ),
        pytest.param(
            {},
            id="No params",
        ),
        pytest.param(
            {
                "dm_rows": 22,
            },
            id="dm_rows only",
        ),
        pytest.param(
            {
                "dm_cols": 22,
            },
            id="dm_cols only",
        ),
        pytest.param(
            {
                "x_undercut": 1,
                "scaling": {"pix_mult": 50},
            },
            id="x undercut only (default scaling overwritten to make this possible)",
        ),
        pytest.param(
            {
                "y_undercut": 1,
                "scaling": {"pix_mult": 50},
            },
            id="y undercut only (default scaling overwritten to make this possible)",
        ),
        pytest.param(
            {
                "x_undercut": 1,
                "y_undercut": 1,
                "scaling": {"pix_mult": 50},
            },
            id="Both x and y undercut (default scaling overwritten to make this possible)",
        ),
        pytest.param(
            {
                "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
            },
            id="Device dot (i.e. physical dimensions e.g. inches) scaling, only target_x_dim defined",
        ),
        pytest.param(
            {
                "scaling": {
                    "resolution": 99999999,
                    "target_x_dim": module_x_dim_inches,
                },
            },
            id="Device dot (i.e. physical dimensions e.g. inches) scaling with a huge DPI. This is fine - the library will attempt to attacin the target but fail but this is okay",
        ),
        pytest.param(
            {
                "scaling": {
                    "resolution": 300,
                    "min_x_dim": 0.02,
                    "target_x_dim": 0.03,
                    "max_x_dim": 0.04,
                },
            },
            id="Device dot (i.e. physical dimensions e.g. inches) scaling, only target_x_dim defined",
        ),
        pytest.param(
            {
                "scaling": {"pix_mult": 50},
            },
            id="Pixel-based (i.e. pixels only, not physical dimensions) scaling scaling only",
        ),
    ],
)
def good_generation_params(request) -> dict:
    return request.param


def test_good_params(good_barcode_text, good_generation_params: dict, output_dir: Path):
    bmp_data = generate_gs1_datamatrix(good_barcode_text, **good_generation_params)
    save_to_file(output_dir / "gs1_barcode_enginer_wrapper.bmp", bmp_data)
    assert bmp_data


def test_bad_input(bad_barcode_text: dict, good_generation_params: dict):
    with pytest.raises(Gs1GeneratorError) as exc:
        _ = generate_gs1_datamatrix(
            bad_barcode_text["test_string"], **good_generation_params
        )

    assert bad_barcode_text["expect_string_in_exception"] in str(exc)


def test_bad_generation_params(good_barcode_text, bad_generation_params: dict):
    test_params = bad_generation_params["test_params"]
    with pytest.raises(Gs1GeneratorError) as exc:
        bmp_data = generate_gs1_datamatrix(good_barcode_text, **test_params)

    assert bad_generation_params["expect_string_in_exception"] in str(exc)


def get_mem_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss  # unit of measurement is platform-dependent


def test_memory_isnt_leaky():
    current_mem_usage = get_mem_usage()
    print(f"current mem usage:{current_mem_usage}")

    for _ in range(10000):
        bmp_output = generate_gs1_datamatrix(
            "(01)94210325403182(30)2(3922)0460(93)TQ",
            **{
                "dm_rows": 22,
                "dm_cols": 22,
                "x_undercut": 0,
                "y_undercut": 0,
                "scaling": {"resolution": dpi, "target_x_dim": module_x_dim_inches},
            },
        )
        assert bmp_output

    new_mem_usage = get_mem_usage()
    print(f"new mem usage: {new_mem_usage}.")
    print(f"mem usage delta: {new_mem_usage-current_mem_usage}")

    assert get_mem_usage() < current_mem_usage * 1.2, "Likely memory leak"
