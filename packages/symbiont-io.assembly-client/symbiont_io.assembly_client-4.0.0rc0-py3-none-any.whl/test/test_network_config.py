def test_network_config(network_client):
    assert len(network_client.node_sessions) == 1
