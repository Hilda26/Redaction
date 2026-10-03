import pytest

pytestmark = pytest.mark.integration


def test_deployed_schema_exposes_redaction_bounty_surface(deployed_contract):
    # Lightweight smoke test for a deployed address. Full lifecycle integration
    # should be run after deployment when StudioNet RPC is stable.
    assert int(deployed_contract.bounty_count(args=[]).call()) >= 0
    assert int(deployed_contract.submission_count_total(args=[]).call()) >= 0
