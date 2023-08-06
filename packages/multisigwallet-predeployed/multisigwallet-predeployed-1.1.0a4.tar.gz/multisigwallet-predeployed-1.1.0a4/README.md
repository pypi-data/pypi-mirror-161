# multisigwallet-predeployed

## Description

A tool for generating predeployed MultiSigWallet smart contract

## Installation

```console
pip install multisigwallet-predeployed
```

## Usage example

```python
from multisigwallet_predeployed import  MultiSigWalletGenerator, MULTISIGWALLET_ADDRESS

ORIGINATOR_ADDRESS = '0xd200000000000000000000000000000000000000'

multisigwallet_generator = MultiSigWalletGenerator()

genesis = {
    # genesis block parameters
    'alloc': {
        **multisigwallet_generator.generate_allocation(
            contract_address=MULTISIGWALLET_ADDRESS,
            originator_addresses=[ORIGINATOR_ADDRESS]
        )
    }
}

```