import pytest
import base64

from pytoniq_core.tlb import (
    Transaction,
    TransactionOrdinary,
    CurrencyCollection,
    HashUpdate,
    TrStoragePhase,
    TrCreditPhase,
    TrComputePhase,
    TrActionPhase,
    TrBouncePhase,
)
from pytoniq_core.tlb.account import AccountStatus, StorageUsedShort
from pytoniq_core.tlb.transaction import AccStatusChange, ComputeSkipReason

from pytoniq_core.tlb.block import ExtraCurrencyCollection
from pytoniq_core.boc import Cell


def test_transaction_serialization():
    empty_cell = Cell.one_from_boc("b5ee9c72010101010002000000")
    tx = Transaction(
        account_addr=base64.urlsafe_b64decode(
            "EQDtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p4q2"
        ),
        lt=123456,
        prev_trans_hash=bytes.fromhex(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        ),
        prev_trans_lt=654321,
        now=111111,
        outmsg_cnt=0,
        orig_status=AccountStatus("active"),
        end_status=AccountStatus("active"),
        in_msg=None,
        out_msgs=[],
        total_fees=CurrencyCollection(1234),
        state_update=HashUpdate(
            bytes.fromhex(
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            ),
            bytes.fromhex(
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
            ),
        ),
        description=TransactionOrdinary(
            credit_first=True,
            storage_ph=TrStoragePhase(
                storage_fees_collected=2,
                storage_fees_due=3,
                status_change=AccStatusChange("unchanged"),
            ),
            credit_ph=TrCreditPhase(due_fees_collected=4, credit=CurrencyCollection(5)),
            compute_ph=TrComputePhase(
                type_="vm",
                reason=None,
                success=True,
                msg_state_used=True,
                account_activated=True,
                gas_fees=6,
                gas_used=7,
                gas_limit=8,
                gas_credit=9,
                mode=10,
                exit_code=11,
                exit_arg=12,
                vm_steps=13,
                vm_init_state_hash=bytes.fromhex(
                    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
                ),
                vm_final_state_hash=bytes.fromhex(
                    "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
                ),
            ),
            action=TrActionPhase(
                success=True,
                valid=True,
                no_funds=True,
                status_change=AccStatusChange("unchanged"),
                total_fwd_fees=14,
                total_action_fees=15,
                result_code=16,
                result_arg=17,
                tot_actions=18,
                spec_actions=19,
                skipped_actions=20,
                msgs_created=21,
                action_list_hash=bytes.fromhex(
                    "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
                ),
                tot_msg_size=StorageUsedShort(cells=1, bits=2),
            ),
            aborted=False,
            bounce=TrBouncePhase(
                type_="ok",
                msg_size=StorageUsedShort(cells=1, bits=2),
                req_fwd_fees=22,
                msg_fees=23,
                fwd_fees=24,
            ),
            destroyed=False,
        ),
        cell=empty_cell,
    )
    serialized = tx.serialize()
    # FIXME: deserialization fails :(
    Transaction.deserialize(serialized.to_slice())


@pytest.mark.parametrize("status", ["uninitialized", "frozen", "active", "nonexist"])
def test_account_status_serialization(status):
    account_status = AccountStatus(type_=status)
    serialized = account_status.serialize()
    deserialized = AccountStatus.deserialize(serialized.to_slice())
    assert account_status.type_ == deserialized.type_


def test_currency_collection_serialization():
    currency_collection = CurrencyCollection(grams=0, other=ExtraCurrencyCollection())
    serialized = currency_collection.serialize()
    deserialized = CurrencyCollection.deserialize(serialized.to_slice())
    assert currency_collection.grams == deserialized.grams


def test_hash_update_serialization():
    hash_update = HashUpdate(
        bytes.fromhex(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        ),
        bytes.fromhex(
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
        ),
    )
    serialized = hash_update.serialize()
    deserialized = HashUpdate.deserialize(serialized.to_slice())
    assert hash_update.new_hash == deserialized.new_hash
    assert hash_update.old_hash == deserialized.old_hash


def test_storage_phase_serialization():
    storage_phases = [
        TrStoragePhase(
            storage_fees_collected=1,
            storage_fees_due=None,
            status_change=AccStatusChange("unchanged"),
        ),
        TrStoragePhase(
            storage_fees_collected=1,
            storage_fees_due=2,
            status_change=AccStatusChange("unchanged"),
        ),
    ]
    for storage_phase in storage_phases:
        serialized = storage_phase.serialize()
        deserialized = TrStoragePhase.deserialize(serialized.to_slice())
        assert storage_phase.status_change.type_ == deserialized.status_change.type_
        assert (
            storage_phase.storage_fees_collected == deserialized.storage_fees_collected
        )
        assert storage_phase.storage_fees_due == deserialized.storage_fees_due


def test_credit_phase_serialization():
    credit_phases = [
        TrCreditPhase(
            due_fees_collected=None,
            credit=CurrencyCollection(grams=1),
        ),
        TrCreditPhase(
            due_fees_collected=2,
            credit=CurrencyCollection(grams=1),
        ),
    ]

    for credit_phase in credit_phases:
        serialized = credit_phase.serialize()
        deserialized = TrCreditPhase.deserialize(serialized.to_slice())
        assert credit_phase.credit.grams == deserialized.credit.grams
        assert credit_phase.due_fees_collected == deserialized.due_fees_collected


def test_compute_phase_serialization():
    compute_phases = [
        TrComputePhase(
            type_="skipped",
            reason=ComputeSkipReason("no_state"),
        ),
        TrComputePhase(
            type_="vm",
            reason=None,
            success=True,
            msg_state_used=True,
            account_activated=True,
            gas_fees=6,
            gas_used=7,
            gas_limit=8,
            gas_credit=9,
            mode=10,
            exit_code=11,
            exit_arg=12,
            vm_steps=13,
            vm_init_state_hash=bytes.fromhex(
                "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
            ),
            vm_final_state_hash=bytes.fromhex(
                "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
            ),
        ),
    ]
    for compute_phase in compute_phases:
        serialized = compute_phase.serialize()
        deserialized = TrComputePhase.deserialize(serialized.to_slice())
        assert compute_phase.type_ == deserialized.type_
        if compute_phase.type_ == "skipped":
            assert compute_phase.reason.type_ == deserialized.reason.type_
            continue
        assert compute_phase.success == deserialized.success
        assert compute_phase.msg_state_used == deserialized.msg_state_used
        assert compute_phase.account_activated == deserialized.account_activated
        assert compute_phase.gas_fees == deserialized.gas_fees
        assert compute_phase.gas_used == deserialized.gas_used
        assert compute_phase.gas_limit == deserialized.gas_limit
        assert compute_phase.gas_credit == deserialized.gas_credit
        assert compute_phase.mode == deserialized.mode
        assert compute_phase.exit_code == deserialized.exit_code
        assert compute_phase.exit_arg == deserialized.exit_arg
        assert compute_phase.vm_steps == deserialized.vm_steps
        assert compute_phase.vm_init_state_hash == deserialized.vm_init_state_hash
        assert compute_phase.vm_final_state_hash == deserialized.vm_final_state_hash


def test_action_phase_serialization():
    action_phase = TrActionPhase(
        success=True,
        valid=True,
        no_funds=True,
        status_change=AccStatusChange("unchanged"),
        total_fwd_fees=14,
        total_action_fees=15,
        result_code=16,
        result_arg=17,
        tot_actions=18,
        spec_actions=19,
        skipped_actions=20,
        msgs_created=21,
        action_list_hash=bytes.fromhex(
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
        ),
        tot_msg_size=StorageUsedShort(cells=1, bits=2),
    )

    serialized = action_phase.serialize()
    deserialized = TrActionPhase.deserialize(serialized.to_slice())
    assert action_phase.success == deserialized.success
    assert action_phase.valid == deserialized.valid
    assert action_phase.no_funds == deserialized.no_funds
    assert action_phase.status_change.type_ == deserialized.status_change.type_
    assert action_phase.total_fwd_fees == deserialized.total_fwd_fees
    assert action_phase.total_action_fees == deserialized.total_action_fees
    assert action_phase.result_code == deserialized.result_code
    assert action_phase.result_arg == deserialized.result_arg
    assert action_phase.tot_actions == deserialized.tot_actions
    assert action_phase.spec_actions == deserialized.spec_actions
    assert action_phase.skipped_actions == deserialized.skipped_actions
    assert action_phase.msgs_created == deserialized.msgs_created
    assert action_phase.action_list_hash == deserialized.action_list_hash
    assert action_phase.tot_msg_size.bits == deserialized.tot_msg_size.bits
    assert action_phase.tot_msg_size.cells == deserialized.tot_msg_size.cells


def test_transaction_ordinary_serialization():
    transaction_oridinary = TransactionOrdinary(
        credit_first=True,
        storage_ph=TrStoragePhase(
            storage_fees_collected=2,
            storage_fees_due=3,
            status_change=AccStatusChange("unchanged"),
        ),
        credit_ph=TrCreditPhase(due_fees_collected=4, credit=CurrencyCollection(5)),
        compute_ph=TrComputePhase(
            type_="vm",
            reason=None,
            success=True,
            msg_state_used=True,
            account_activated=True,
            gas_fees=6,
            gas_used=7,
            gas_limit=8,
            gas_credit=9,
            mode=10,
            exit_code=11,
            exit_arg=12,
            vm_steps=13,
            vm_init_state_hash=bytes.fromhex(
                "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
            ),
            vm_final_state_hash=bytes.fromhex(
                "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
            ),
        ),
        action=TrActionPhase(
            success=True,
            valid=True,
            no_funds=True,
            status_change=AccStatusChange("unchanged"),
            total_fwd_fees=14,
            total_action_fees=15,
            result_code=16,
            result_arg=17,
            tot_actions=18,
            spec_actions=19,
            skipped_actions=20,
            msgs_created=21,
            action_list_hash=bytes.fromhex(
                "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
            ),
            tot_msg_size=StorageUsedShort(cells=1, bits=2),
        ),
        aborted=False,
        bounce=TrBouncePhase(
            type_="ok",
            msg_size=StorageUsedShort(cells=1, bits=2),
            req_fwd_fees=22,
            msg_fees=23,
            fwd_fees=24,
        ),
        destroyed=False,
    )

    serialized = transaction_oridinary.serialize()
    TransactionOrdinary.deserialize(serialized.to_slice())
