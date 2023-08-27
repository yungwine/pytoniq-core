# pytoniq-core

[![PyPI version](https://badge.fury.io/py/pytoniq-core.svg)](https://badge.fury.io/py/pytoniq-core) 
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytoniq-core)](https://pypi.org/project/pytoniq-core/)
![](https://pepy.tech/badge/pytoniq-core) 
[![Downloads](https://static.pepy.tech/badge/pytoniq-core)](https://pepy.tech/project/pytoniq-core) 
[![](https://img.shields.io/badge/%F0%9F%92%8E-TON-grey)](https://ton.org)

## Installation

```bash
pip install pytoniq-core
```

## Examples

You can find them in the [/examples](/examples) folder.

## Donations

TON - `EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`

## Structure

### boc

* Cell
* Slice
* Builder
* Hashmap
* Address
* Exotic cells

### crypto

* Cryptography for ADNL
* Native fast crc functions 
* Keys, Mnemonics generation
* Signatures creation and verifying 

### proof

* Merkle proofs verifying - [article](https://docs.ton.org/develop/data-formats/proofs)

### tl

* [TL](https://core.telegram.org/mtproto/TL) automatic (de)serialization

### tl-b

* Almost all wrappers for schemes from [block.tlb](https://github.com/ton-blockchain/ton/blob/master/crypto/block/block.tlb)
* Classes for popular custom tlb schemes
