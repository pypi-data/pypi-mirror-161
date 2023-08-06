import pytest


from assembly_client.api.job_management import ContractErrorInJob
from assembly_client.api.types.error_types import ContractError


def test_executable_error_includes_job_id(
    network_client, published_data_contract, key_alias
):
    """Assert that the Job Id provided by an executable is in the error message."""
    job = network_client[key_alias].data["10-1.0.0"].run_executable_error()
    with pytest.raises(ContractErrorInJob, match=f"JobId: {job.job_id}"):
        job.start_waiting()


def test_clientside_error_includes_job_id(
    network_client, published_data_contract, key_alias
):
    """Assert that a Job Id is not in a clientside error."""
    try:
        network_client[key_alias].data["10-1.0.0"].run_clientside_error()
    except ContractError as e:
        assert "JobId" not in e.message
