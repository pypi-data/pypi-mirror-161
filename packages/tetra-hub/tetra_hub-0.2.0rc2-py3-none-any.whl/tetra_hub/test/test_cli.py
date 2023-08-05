import pytest
from tetra_hub._cli import configure
import tempfile
import configparser


@pytest.fixture
def config_data():
    config_data = {
        "api": {
            "api_token": "API_TOKEN_fbajc",
            "api_url": "https://staging.tetra.ai",
            "web_url": "https://staging.tetra.ai",
        }
    }
    return config_data


def validate_good_configuration(config):
    assert config.sections() == ["api"]
    assert config.get("api", "api_url") == "https://staging.tetra.ai"
    assert config.get("api", "web_url") == "https://staging.tetra.ai"
    assert config.get("api", "api_token") == "API_TOKEN_fbajc"
    assert set(config["api"].keys()) == set(["api_url", "web_url", "api_token"])


def test_good_configuration(config_data):
    ini_path = tempfile.NamedTemporaryFile(suffix="config.ini").name
    configure(config_data, ini_path)

    # Now read the configuration back
    config = configparser.ConfigParser()
    config.read(ini_path)

    # Validate
    validate_good_configuration(config)


def test_backup_config(config_data):
    ini_path = tempfile.NamedTemporaryFile(suffix="config.ini").name
    configure(config_data, ini_path)
    config_data["api"]["api_token"] = "NEW_API_TOKEN_fbajc"
    configure(config_data, ini_path)

    # Now read the configuration back
    config_bak = configparser.ConfigParser()
    config_bak.read(f"{ini_path}.bak")
    validate_good_configuration(config_bak)

    # Validate
    config = configparser.ConfigParser()
    config.read(ini_path)
    assert config.get("api", "api_token") == "NEW_API_TOKEN_fbajc"
