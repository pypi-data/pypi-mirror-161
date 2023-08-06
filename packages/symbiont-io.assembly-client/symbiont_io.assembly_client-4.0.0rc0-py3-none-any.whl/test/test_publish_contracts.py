def test_publish_contract(network_client, published_data_contract):
    assert len(network_client.list_contracts()) == 9
