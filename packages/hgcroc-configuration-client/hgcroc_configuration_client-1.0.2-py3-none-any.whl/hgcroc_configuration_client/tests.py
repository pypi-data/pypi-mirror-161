from _pytest.monkeypatch import monkeypatch
import multiprocessing as mp
import pytest
import yaml
import logging

from client import Client
from hexacontroller_sc_server import server
from hexacontroller_sc_server import hexactrl_io
from hexacontroller_sc_server.mock_io import mock_Xil_gpio
from hexacontroller_sc_server.mock_io import MockSMBus
from hexacontroller_sc_server import Hexaboard
from hexacontroller_sc_server import i2c_utilities


def compose(start_addresses):
    responding_addresses = []
    for bus, address in zip(*start_addresses):
        responding_addresses += \
                list((bus, x) for x in list(range(address, address + 8)))

    return responding_addresses


i2c_test_peripherals = {}
peripherals = compose(([0, 1, 2], [0x20, 0x40, 0x60]))
for bus, peripherals in peripherals:
    i2c_test_peripherals[bus] = peripherals
MockSMBus.set_peripherals(i2c_test_peripherals)


@pytest.fixture
def patched_io(monkeypatch):
    def mock_find_links():
        with open("test_configs/test_hexaboard_description.yaml", "r") as f:
            description = yaml.safe_load(f)

        return ('ld_hexaboard', description)
    monkeypatch.setattr(hexactrl_io, "SMBus", MockSMBus)
    monkeypatch.setattr(Hexaboard, "Xil_gpio", mock_Xil_gpio)
    monkeypatch.setattr(hexactrl_io, "Xil_gpio", mock_Xil_gpio)
    monkeypatch.setattr(i2c_utilities, "find_links", mock_find_links)


def test_client(patched_io):
    with open("test_configs/board_test_config.yml", "r") as f:
        config = yaml.safe_load(f)

    def proc_run_server():
        logging.basicConfig(filename='roc_configuration.log')
        config_table = 'test_configs/HGCROC3_I2C_params_regmap.csv'
        socket = server.open_socket(5555)
        server.run(config_table, socket)

    proc = mp.Process(target=proc_run_server)
    proc.start()

    client = Client('localhost')
    client.set(config)
    response = client.get(config)
    assert response == config
    client.stop()

    return
