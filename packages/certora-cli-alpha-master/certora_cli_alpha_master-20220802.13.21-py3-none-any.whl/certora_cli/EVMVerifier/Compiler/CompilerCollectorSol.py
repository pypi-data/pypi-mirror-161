from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple, Dict

from EVMVerifier.Compiler.CompilerCollector import CompilerLang, CompilerCollector
from Shared.certoraUtils import Singleton


class CompilerLangSol(CompilerLang, metaclass=Singleton):
    """
    [CompilerLang] for Solidity.
    """

    @property
    def name(self) -> str:
        return "Solidity"


# This class is intended for calculations of compiler-settings related queries
@dataclass
class CompilerCollectorSol(CompilerCollector):

    _compiler_version: Tuple[int, int, int] = (0, 0, 0)

    @property
    def smart_contract_lang(self) -> CompilerLangSol:
        return CompilerLangSol()

    @property
    def compiler_version(self) -> Tuple[int, int, int]:
        return self._compiler_version

    @compiler_version.setter
    def compiler_version(self, version: Tuple[int, int, int]) -> None:
        self._compiler_version = version

    def get_contract_def_node_ref(self, contract_file_ast: Dict[int, Any], contract_file: str, contract_name: str) -> \
            int:
        contract_def_refs = list(filter(
            lambda node_id: contract_file_ast[node_id].get("nodeType") == "ContractDefinition" and
            contract_file_ast[node_id].get("name") == contract_name, contract_file_ast))
        assert len(contract_def_refs) != 0, \
            f'Failed to find a "ContractDefinition" ast node id for the contract {contract_name}'
        assert len(
            contract_def_refs) == 1, f'Found multiple "ContractDefinition" ast node ids for the same contract ' \
                                     f'{contract_name}: {contract_def_refs}'
        return contract_def_refs[0]

    def get_standard_json_filename(self, sdc_name: str, config_path: Path) -> Path:
        return config_path / f"{sdc_name}.standard.json.stdout"

    def normalize_storage(self, is_storage: bool, arg_name: str) -> str:
        if self._compiler_version == (0, 0, 0):
            raise Exception(
                "[self._compiler_version] should be set before calling the [supports_calldata_assembly] function")
        if not is_storage:
            return arg_name
        if self._compiler_version[0] == 0 and self._compiler_version[1] < 7:
            return arg_name + "_slot"
        else:
            return arg_name + ".slot"

    def supports_calldata_assembly(self, arg_name: str) -> bool:
        if self._compiler_version == (0, 0, 0):
            raise Exception(
                "[self._compiler_version] should be set before calling the [supports_calldata_assembly] function")
        return (self._compiler_version[1] > 7 or (
                self._compiler_version[1] == 7 and self._compiler_version[2] >= 5)) and arg_name != ""
