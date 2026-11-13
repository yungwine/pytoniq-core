import copy

import pytest

from pytoniq_core.proof.check_proof import ProofError, check_block_signature_set, simplex_signed_data
from pytoniq_core.crypto.signature import verify_sign
from pytoniq_core.tl.block import BlockIdExt
from pytoniq_core.tlb.config import SigPubKey, ValidatorDescr

# A real Simplex consensus signature set from a mainnet getBlockProof forward step (2026-11-13), with one of its
# signatures and the signer's public key from config param 34.
BLOCK = {
    "workchain": -1,
    "shard": -9223372036854775808,
    "seqno": 105266746,
    "root_hash": "21e9279f3ed33be690a395e0825f1e5269d8ffd46766dd31a3c852fbc4f58a4b",
    "file_hash": "6c34f3dac39b4bff1f6252d48d42bbb10fec9ffcf1c35fe438d755013304662a",
    "@type": "tonNode.blockIdExt"
}
SIGNATURE_SET = {
    "@type": "liteServer.signatureSet.simplex",
    "cc_seqno": 882037,
    "validator_set_hash": 1759636817,
    "session_id": "d82799c18186884b4646a10b2e356bd37f6cb89f51a6e40f0747e3e16e9a30cb",
    "slot": 532,
    "candidate": {
        "@type": "consensus.candidateHashDataOrdinary",
        "block": {
            "workchain": -1,
            "shard": -9223372036854775808,
            "seqno": 105266746,
            "root_hash": "21e9279f3ed33be690a395e0825f1e5269d8ffd46766dd31a3c852fbc4f58a4b",
            "file_hash": "6c34f3dac39b4bff1f6252d48d42bbb10fec9ffcf1c35fe438d755013304662a",
            "@type": "tonNode.blockIdExt"
        },
        "collated_file_hash": "9bc3a6fa64feafeb1d9153eb4e3440c7dea90245bcaf5c9ba9b3fa9939cf9d40",
        "parent": {
            "@type": "consensus.candidateParent",
            "id": {
                "@type": "consensus.candidateId",
                "slot": 531,
                "hash": "9226043ece0bc1ec0fefeaa03a1f6324b423378328be6870efdf763ddd68d8d8"
            }
        }
    },
    "signatures": [
        {
            "node_id_short": "349b8d4ba00a99318f8cc5f2a40c98f9636cc41f1cc13fefa3fa78a7a59e4225",
            "signature": ("527b81b743a77247e743d4aec3f37af1096e005db1fd37de6c6cb310c1c1f449"
                          "75f55cc4216742cdeaf1243073897e1839c918172926644a22be7b712dfa870a")
        }
    ]
}
PUBLIC_KEY = bytes.fromhex("e8d423cd9c17d8a038dac1dc7632e187ef969b9a80df4ce4cbe4773ab7094992")


def signature_set():
    # as the liteserver delivers it: signatures as bytes
    result = copy.deepcopy(SIGNATURE_SET)
    for sig in result["signatures"]:
        sig["signature"] = bytes.fromhex(sig["signature"])
    return result


def validator():
    return ValidatorDescr("validator", SigPubKey(PUBLIC_KEY), 1)


def test_simplex_signed_data_matches_a_real_validator_signature():
    data = simplex_signed_data(SIGNATURE_SET, BlockIdExt.from_dict(BLOCK))
    assert verify_sign(PUBLIC_KEY, data, bytes.fromhex(SIGNATURE_SET["signatures"][0]["signature"]))


def test_simplex_signature_set_checks():
    check_block_signature_set([validator()], signature_set(), BlockIdExt.from_dict(BLOCK))


def test_simplex_signature_set_for_another_block_is_refused():
    other = dict(BLOCK, seqno=BLOCK["seqno"] + 1)
    with pytest.raises(ProofError):
        check_block_signature_set([validator()], signature_set(), BlockIdExt.from_dict(other))


def test_repeated_signature_does_not_count_twice():
    doubled = signature_set()
    doubled["signatures"] = doubled["signatures"] * 2
    with pytest.raises(ProofError, match="duplicate"):
        check_block_signature_set([validator()], doubled, BlockIdExt.from_dict(BLOCK))
