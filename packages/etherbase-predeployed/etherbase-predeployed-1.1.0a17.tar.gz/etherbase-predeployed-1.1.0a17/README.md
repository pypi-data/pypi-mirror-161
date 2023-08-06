# etherbase-predeployed

## Description

A tool for generating predeployed etherbase smart contract

## Installation

```console
pip install etherbase-predeployed
```

## Usage example

```python
from etherbase_predeployed import  UpgradeableEtherbaseUpgradeableGenerator, ETHERBASE_ADDRESS, ETHERBASE_IMPLEMENTATION_ADDRESS

OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
PROXY_ADMIN_ADDRESS = '0xd200000000000000000000000000000000000001'

etherbase_generator = UpgradeableEtherbaseUpgradeableGenerator()

genesis = {
    # genesis block parameters
    'alloc': {
        **etherbase_generator.generate_allocation(
            contract_address=ETHERBASE_ADDRESS,
            implementation_address=ETHERBASE_IMPLEMENTATION_ADDRESS,
            schain_owner=OWNER_ADDRESS,
            proxy_admin_address=PROXY_ADMIN_ADDRESS
        )
    }
}

```