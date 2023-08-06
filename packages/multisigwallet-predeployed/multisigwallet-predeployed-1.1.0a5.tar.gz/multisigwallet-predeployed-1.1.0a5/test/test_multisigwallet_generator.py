from web3.auto import w3

from multisigwallet_predeployed import MultiSigWalletGenerator, MULTISIGWALLET_ADDRESS
from .tools.test_solidity_project import TestSolidityProject


class TestMultiSigWalletGenerator(TestSolidityProject):
    ORIGINATOR_ADDRESS_0 = '0xd200000000000000000000000000000000000000'
    ORIGINATOR_ADDRESS_1 = '0xd200000000000000000000000000000000000000'
    ZERO_ADDRESS = '0x'+'0'*40
    MAX_OWNER_COUNT = 50

    def get_multisig_abi(self):
        return self.get_abi('MultiSigWallet')

    def prepare_genesis(self):
        multisigwallet_generator = MultiSigWalletGenerator()

        return self.generate_genesis(multisigwallet_generator.generate_allocation(
            MULTISIGWALLET_ADDRESS,
            originator_addresses=[self.ORIGINATOR_ADDRESS_0]))

    def test_max_owner_count(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            multisig = w3.eth.contract(address=MULTISIGWALLET_ADDRESS, abi=self.get_multisig_abi())
            assert multisig.functions.MAX_OWNER_COUNT().call() == self.MAX_OWNER_COUNT

    def test_is_owner(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            multisig = w3.eth.contract(address=MULTISIGWALLET_ADDRESS, abi=self.get_multisig_abi())
            assert multisig.functions.isOwner(self.ORIGINATOR_ADDRESS_0).call()

    def test_owners(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            multisig = w3.eth.contract(address=MULTISIGWALLET_ADDRESS, abi=self.get_multisig_abi())
            assert multisig.functions.owners(0).call() == self.ORIGINATOR_ADDRESS_0

    def test_default_required(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            multisig = w3.eth.contract(address=MULTISIGWALLET_ADDRESS, abi=self.get_multisig_abi())
            assert multisig.functions.required().call() == 1
    
    def test_required_and_is_owners(self, tmpdir):
        multisigwallet_generator = MultiSigWalletGenerator()

        genesis = self.generate_genesis(multisigwallet_generator.generate_allocation(
            MULTISIGWALLET_ADDRESS,
            originator_addresses=[self.ORIGINATOR_ADDRESS_0, self.ORIGINATOR_ADDRESS_1],
            required_confirmations=2))

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            multisig = w3.eth.contract(address=MULTISIGWALLET_ADDRESS, abi=self.get_multisig_abi())
            assert multisig.functions.required().call() == 2
            assert multisig.functions.isOwner(self.ORIGINATOR_ADDRESS_0).call()
            assert multisig.functions.isOwner(self.ORIGINATOR_ADDRESS_1).call()

    def test_meta_info(self):
        meta = MultiSigWalletGenerator().get_meta()
        assert meta['name'] == 'MultiSigWallet'
    