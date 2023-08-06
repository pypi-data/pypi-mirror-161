"""tools.py

The module stores helpers for work with predeployed contracts

Classes:
    ArtifactsHandler
"""

import json
import shutil
from os.path import normpath, join


class MetaNotFoundError(Exception):
    """Meta file does not exist"""


class ArtifactsHandler:
    """Generate and copy smart contract artifacts in pkg dir"""

    def __init__(self, hardhat_artifacts_dir, pkg_artifacts_dir):
        self.hardhat_artifacts_dir = hardhat_artifacts_dir
        self.pkg_artifacts_dir = pkg_artifacts_dir

    @staticmethod
    def get_build_info_path(contract_name, hardhat_contract_dir):
        """Get path to contract buildInfo"""
        with open(join(hardhat_contract_dir, f'{contract_name}.dbg.json'),
                  encoding='utf-8') as dbg_file:
            dbg = json.loads(dbg_file.read())
            return normpath(join(hardhat_contract_dir, dbg['buildInfo']))

    def get_hardhat_contract_dir(self, contract_name):
        """Get path to contract hardhat artifacts"""
        return normpath(join(self.hardhat_artifacts_dir, f'{contract_name}.sol'))

    def prepare_artifacts(self, contract_name):
        """Generates meta file and copy it and artifacts json to pkg dir"""
        hardhat_contract_dir = self.get_hardhat_contract_dir(contract_name)
        build_info_path = self.get_build_info_path(contract_name, hardhat_contract_dir)
        with open(build_info_path, encoding='utf-8') as info_file:
            info = json.loads(info_file.read())
            meta_data = {
                'name': contract_name,
                'solcVersion': info['solcVersion'],
                'solcLongVersion': info['solcLongVersion'],
                'input': info['input']
            }
        with open(join(self.pkg_artifacts_dir, f'{contract_name}.meta.json'),
                  mode='w',
                  encoding='utf-8') as meta:
            meta.write(json.dumps(meta_data, indent=4))
        shutil.copy(join(hardhat_contract_dir, f'{contract_name}.json'), self.pkg_artifacts_dir)
