import os
import pytest
from assembly_client.api.network_client import NetworkClient


import os
import posixpath
from assembly_client.api.contracts import ContractRef


DATA = ContractRef("data", "1.0.0", 10)


DEFAULT_PATH = os.path.expanduser(
    "~/.symbiont/assembly-dev/dev-network/default/network-config.json"
)


CONTRACT_PATH = posixpath.join(os.path.dirname(os.path.realpath(__file__)), "contracts")


@pytest.fixture
def network_client():
    client = NetworkClient.from_network_config_file(DEFAULT_PATH, [CONTRACT_PATH])
    client.reset(txe_protocol=13, sympl_version=10)
    return client


@pytest.fixture
def published_data_contract(network_client):
    network_client.publish([DATA])


@pytest.fixture
def key_alias(network_client):
    return network_client.register_key_alias()
