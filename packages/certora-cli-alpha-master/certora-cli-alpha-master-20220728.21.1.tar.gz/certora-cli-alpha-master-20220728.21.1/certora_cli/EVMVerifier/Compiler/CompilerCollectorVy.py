from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from EVMVerifier.Compiler.CompilerCollector import CompilerCollector, CompilerLang
from Shared.certoraUtils import Singleton


class CompilerLangVy(CompilerLang, metaclass=Singleton):
    """
    [CompilerLang] for Vyper.
    """

    @property
    def name(self) -> str:
        return "Vyper"


@dataclass
class CompilerCollectorVy(CompilerCollector):

    _compiler_version: str = "vyper"

    @property
    def smart_contract_lang(self) -> CompilerLangVy:
        return CompilerLangVy()

    @property
    def compiler_version(self) -> str:
        return self._compiler_version

    def normalize_func_hash(self, func_hash: str) -> str:
        try:
            return hex(int(func_hash, 16))
        except ValueError:
            raise Exception(f'{func_hash} is not convertible to hexadecimal')

    def normalize_file_compiler_path_name(self, file_abs_path: str) -> str:
        assert file_abs_path.startswith('/'), f'expected {file_abs_path} to begin with forwardslash'
        return file_abs_path[1:]

    def normalize_deployed_bytecode(self, deployed_bytecode: str) -> str:
        assert deployed_bytecode.startswith("0x"), f'expected {deployed_bytecode} to have hexadecimal prefix'
        return deployed_bytecode[2:]

    def get_contract_def_node_ref(self, contract_file_ast: Dict[int, Any], contract_file: str, contract_name: str) -> \
            int:
        # in vyper, "ContractDefinition" is "Module"
        contract_def_refs = list(filter(
            lambda node_id: contract_file_ast[node_id].get("ast_type") == "Module" and
            contract_file_ast[node_id].get("name") == contract_file, contract_file_ast))
        assert len(contract_def_refs) != 0, \
            f'Failed to find a "Module" ast node id for the file {contract_file}'
        assert len(contract_def_refs) == 1, f'Found multiple "Module" ast node ids for the same file' \
            f'{contract_file}: {contract_def_refs}'
        return contract_def_refs[0]

    def get_standard_json_filename(self, sdc_name: str, config_path: Path) -> Path:
        return config_path / f"{sdc_name}"
