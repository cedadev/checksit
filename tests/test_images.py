import pytest
from click.testing import CliRunner
from checksit import cli

@pytest.mark.parametrize(
    "image, error_level, number_errors",
    [
        ("ncas-cam-9_cao_20160510-134927_photo_v1.0.jpg", "NONE", 0),
        ("ncas-cam-9_cao_20160510-134927_photo_test-2_v1.0.jpg", "ERROR", 1),
        ("ncas-cam-9_cao_20160510-134927_photo_test-1_v1.0.jpg", "WARNING", 3),
    ],
)
def test_image_checks(image, error_level, number_errors):
    runner = CliRunner()
    result = runner.invoke(cli.check, ["-l", "compact", f"tests/test_images/{image}"])
    level_found, errors_found = [i.strip() for i in result.output.split("|")[2:4]]
    errors_found = int(errors_found)
    assert error_level == level_found
    assert number_errors == errors_found
