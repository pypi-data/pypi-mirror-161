import json
import os

from src.predeployed_generator.tools import ArtifactsHandler
from test.tools.custom_contract_generator import CustomContractGenerator
from test.tools.test_solidity_project import TestSolidityProject


class TestArtifactsHandler(TestSolidityProject):

    def prepare(self):
        self.hardhat_dir = os.path.join(self.get_artifacts_dir(), 'contracts')
        self.target_dir = os.path.join(self.hardhat_dir, '..', 'target')
        os.mkdir(self.target_dir)
        self.name = CustomContractGenerator.CONTRACT_NAME

    def test_prepare_artifacts(self):
        self.prepare()
        test_handler = ArtifactsHandler(self.hardhat_dir, self.target_dir)
        test_handler.prepare_artifacts(self.name)

        assert os.path.exists(os.path.join(self.target_dir, f'{self.name}.json'))
        assert os.path.exists(os.path.join(self.target_dir, f'{self.name}.meta.json'))

        with open(os.path.join(self.target_dir, f'{self.name}.meta.json')) as meta_file:
            meta = json.loads(meta_file.read())
            assert meta['name'] == self.name
