from pytoniq_core import Cell
from pytoniq_core.tlb.block import Block

# Header proof of mainnet masterchain block 105263077 (dest_proof of a getBlockProof forward step, 2026-11-13).
# Liteservers prune prev_ref in such proofs.
DEST_PROOF = bytes.fromhex(
    'b5ee9c720102070100011f0009460336ed5d48f88ab58c19bac439c7cac5822e8b1b027afa56e2b01b39a6c895d0d300'
    '1601241011ef55aaffffff110203040521a09bc7a98700000000040106462fe50000000100ffffffff00000000000000'
    '006af78c45000069f0a1a4ce40000069f0a1a4ce4470dcc812000d756f06462fe206459bcec400000011000000000000'
    '03ee0628480101352bcc75b563b2258d9f84e65cfeed3f0e21899128f3ef3fcdf7e6e8c988b16600032848010178be16'
    '805e837ae31945dbd256761a802343039b689e38d37e4facc07feb9eb0001528480101d42954d5b265abd6dba1c327ea'
    'ca0b4fb28f157def4a6f0974a1e5aad95e5efd000728480101ff26163e5e56e42a23583eebac5b4930492a2d94cf2695'
    '1f3e3d4174d0c0255c0000'
)


def test_block_header_proof_with_pruned_prev_ref():
    block = Block.deserialize(Cell.one_from_boc(DEST_PROOF)[0].begin_parse())

    assert block.info.seqno == 105263077
    assert block.info.not_master == 0
    assert block.info.prev_ref is None  # pruned branch, not readable
