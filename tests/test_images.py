import pytest
from click.testing import CliRunner
from checksit import cli
import os

# quick test to make sure python is where I think it is
def test_where():
    loc = (os.listdir("tests"))
    assert "test_images" in loc


# photos from ncas named instruments
@pytest.mark.parametrize(
    "photo, error_level, number_errors",
    [
        ("ncas-cam-9_cao_20160510-134927_photo_v1.0.jpg", "NONE", 0),
        ("ncas-cam-9_cao_20160510-134927_photo_test-2_v1.0.jpg", "ERROR", 1),
        ("ncas-cam-9_cao_20160510-134927_photo_test-1_v1.0.jpg", "WARNING", 3),
        ("ncas-cam-9_cao_20160510-134927_photo_test-3_v1.0.jpg", "ERROR", 1),
        ("ncas-cam-9_cao_20160510-134927_photo_test-4_v1.0.jpg", "ERROR", 1),
        ("ncas-cam-9_cao_20160510-134927_photo_test-5_v1.0.jpg", "ERROR", 2),
        ("ncas-cam-9_cao_20160510-134927_photo_test-6_v1.0.jpg", "ERROR", 3),
        ("ncas-cam-9_cao_20160510-134927_photo_test-7_v1.0.jpg", "ERROR", 1),
    ],
)
def test_ncas_photo_checks(photo, error_level, number_errors):
    runner = CliRunner()
    result = runner.invoke(cli.check, ["-p", "-l", "compact", f"tests/test_images/{photo}"])
    level_found, errors_found = [i.strip() for i in result.output.split("|")[2:4]]
    errors_found = int(errors_found)
    assert error_level == level_found
    assert number_errors == errors_found

# plots from non-ncas named instruments
@pytest.mark.parametrize(
    "plot, error_level, number_errors",
    [
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_st300_wind.png", "ERROR", 1),
        ("radar-mst_capel-dewi_20230706_m300.png", "ERROR", 1),
        ("nerc-mstrf-met-sensors_capel-dewi_20230101_campbell-sci.png", "ERROR", 1),
        ("nerc-mstrf-met-sensors_capel-dewi_20160906_campbell-sci.png", "ERROR", 20),
        ("wind-sensors_frongoch_20090203.png", "ERROR", 13),
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_st300_wind_test-1_v1.0.png", "WARNING", 2),
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_plot_st300_wind_test-2_v1.0.png", "NONE", 0),
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_plot_st300_wind_test-3_v1.0.png", "ERROR", 1),
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_plot_st300_wind_test-4_v1.0.png", "ERROR", 1),
    ]
)
def test_other_plot_checks(plot, error_level, number_errors):
    runner = CliRunner()
    specs = "ncas-image-v1.0/amof-image-global-attrs,ncas-image-v1.0/amof-plot"
    result = runner.invoke(cli.check, ["-p", "-l", "compact", "-t", "off", "--specs", specs, f"tests/test_images/{plot}"])
    level_found, errors_found = [i.strip() for i in result.output.split("|")[2:4]]
    errors_found = int(errors_found)
    assert error_level == level_found
    assert number_errors == errors_found

# check error messages
@pytest.mark.parametrize(
    "plot, error_message",
    [
        ("nerc-mstrf-radar-mst_capel-dewi_20230809_st300_wind.png",
            (
                "[global-attributes:******:XMP-dc:Title]*** Value 'nerc-mstrf-radar-mst_capel-dewi_20230809_st300_wind.png'"
                " does not match regex rule: 'title'."
            ),
        ),
        ("nerc-mstrf-met-sensors_capel-dewi_20160906_campbell-sci.png",
            (
                "[global-attributes:**************:XMP-photoshop:Instructions]: "
                "Attribute 'XMP-photoshop:Instructions' does not exist."
            ),
        ),
    ]
)
def test_check_errors(plot, error_message):
    runner = CliRunner()
    specs = "ncas-image-v1.0/amof-image-global-attrs,ncas-image-v1.0/amof-plot"
    result = runner.invoke(cli.check, ["-p", "-l", "compact", "-t", "off", "--specs", specs, f"tests/test_images/{plot}"])
    message_found = result.output.split("|")[4].strip()
    assert error_message == message_found


