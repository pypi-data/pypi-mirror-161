'''Module for generaration of MultiSigWallet predeployed smart contract'''

from os.path import dirname, join
from typing import Dict

from predeployed_generator.contract_generator import ContractGenerator

class MultiSigWalletGenerator(ContractGenerator):
    '''Generates MultiSigWallet
    '''

    ARTIFACT_FILENAME = 'MultiSigWallet.json'
    META_FILENAME = 'MultiSigWallet.meta.json'
    MAX_OWNER_COUNT = 50
    ZERO_ADDRESS = '0x'+'0'*40

     # ---------- storage ----------
    # -------MultiSigWallet-------
    # 0: transactions
    # 1: confirmations
    # 2: isOwner
    # 3: owners
    # 4: required
    # 5: transactionCount

    TRANSACTIONS_SLOT = 0
    CONFIRMATIONS_SLOT = ContractGenerator.next_slot(TRANSACTIONS_SLOT)
    IS_OWNER_SLOT = ContractGenerator.next_slot(CONFIRMATIONS_SLOT)
    OWNERS_SLOT = ContractGenerator.next_slot(IS_OWNER_SLOT)
    REQUIRED_SLOT = ContractGenerator.next_slot(OWNERS_SLOT)
    TRANSACTIONS_COUNT_SLOT = ContractGenerator.next_slot(REQUIRED_SLOT)

    def __init__(self):
        generator = MultiSigWalletGenerator.from_hardhat_artifact(
            join(dirname(__file__), 'artifacts', self.ARTIFACT_FILENAME),
            join(dirname(__file__), 'artifacts', self.META_FILENAME))
        super().__init__(bytecode=generator.bytecode, abi=generator.abi, meta=generator.meta)

    @classmethod
    def generate_storage(cls, **kwargs) -> Dict[str, str]:

        '''Generate smart contract storage.

        Arguments:
            - originator_addresses (list)

        Optional arguments:
            - required_confirmations (int)

        Returns an object in format:
        {
            "0x00": "0x5",
            "0x01": "0x13"
        }
        '''
        originator_addresses = kwargs['originator_addresses']
        required_confirmations = kwargs.get('required_confirmations', 1)

        if len(originator_addresses) > cls.MAX_OWNER_COUNT:
            raise Exception('Number of originators must not be more than 50')
        if required_confirmations > len(originator_addresses):
            raise Exception('Number of required confirmations must be less'
                            'or equal than number of originators')

        storage: Dict[str, str] = {}
        for originator_address in originator_addresses:
            if originator_address == cls.ZERO_ADDRESS:
                raise Exception('Originator address must not be zero')
            is_owner_value_slot = cls.calculate_mapping_value_slot(
                cls.IS_OWNER_SLOT,
                originator_address,
                'address')
            cls._write_uint256(storage, is_owner_value_slot, 1)
        cls._write_addresses_array(storage, cls.OWNERS_SLOT, originator_addresses)
        cls._write_uint256(storage, cls.REQUIRED_SLOT, required_confirmations)
        return storage
