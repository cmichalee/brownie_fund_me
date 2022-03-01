from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me

# the exceptions package in brownie tells our test what exception were expecting to see
from brownie import network, accounts, exceptions
import pytest


def test_can_fund_and_withdraw():
    # Arrange
    account = get_account()
    fund_me = deploy_fund_me()
    # add a lil bit more to entrance fee in case we need it for whatever reason
    entrance_fee = fund_me.getEntranceFee() + 100

    # Act (fund then wait for 1 confirmation)
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)

    # Assert (make sure we funded the entrance fee)
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee

    # Act (withdraw then wait 1 confirmation)
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)

    # Assert (amount funded should reset since everything should be withdrawn)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    # use pytest.skip to make sure that this test is only run in local environments
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")

    # Arrange
    fund_me = deploy_fund_me()
    # add a new account, different from owner, who will try to withdraw
    bad_actor = accounts.add()
    # We want an error here so we use pytest with exceptions
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor})
