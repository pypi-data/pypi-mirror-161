'''
Creates ContractGenerator based on hardhat artifact file from `artifacts` folder

classes:
    OpenzeppelinContractGenerator
'''

import os

from ..contract_generator import ContractGenerator

class OpenzeppelinContractGenerator(ContractGenerator):
    '''Creates contract generator based on hardhat artifact file from `artifacts` folder'''
    ARTIFACT_FILENAME: str = ''
    META_FILENAME: str = ''

    def __init__(self):
        if not self.get_artifact_filename():
            raise TypeError('ARTIFACT_FILENAME is not overloaded in the class')
        if not self.get_meta_filename():
            raise TypeError('META_FILENAME is not overloaded in the class')
        artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        artifacts_path = os.path.join(artifacts_dir, self.get_artifact_filename())
        meta_path = os.path.join(artifacts_dir, self.get_meta_filename())
        contract = ContractGenerator.from_hardhat_artifact(artifacts_path, meta_path)
        super().__init__(bytecode=contract.bytecode, abi=contract.abi, meta=contract.meta)

    def get_artifact_filename(self):
        '''Return filename of contract artifact'''
        return self.ARTIFACT_FILENAME

    def get_meta_filename(self):
        '''Return filename of contract artifact'''
        return self.META_FILENAME
