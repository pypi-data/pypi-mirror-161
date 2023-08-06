from typing import List

from hrthy_core.security.constants import DEFAULT_SCOPES
from hrthy_core.security.exceptions import WrongScopesConfigurationScopeNotFound, WrongScopesConfigurationHiddenScope, \
    WrongScopesConfigurationMissingDependency
from hrthy_core.security.scopes_hierarchy import HIERARCHY_SCOPES


class ScopesConfiguration:
    scopes: List[str] = []

    def __init__(self, scopes: List[str], current_scopes: List[str]):
        super().__init__()
        self.scopes = ScopesConfiguration._check_configuration_permission(scopes, current_scopes)
        self.scopes = ScopesConfiguration._add_default_scopes(self.scopes)

    @classmethod
    def _check_configuration_permission(cls, scopes: List[str], current_scopes: List[str]) -> List[str]:
        for scope in scopes:
            if scope not in HIERARCHY_SCOPES.keys():
                raise WrongScopesConfigurationScopeNotFound(scope)
            scope_to_check = HIERARCHY_SCOPES.get(scope.strip().lower())
            # Check visibility. If false, this scope cannot be assigned
            if scope_to_check['visible'] is False:
                raise WrongScopesConfigurationHiddenScope(scope)
            # If not true, we need to check if the scopes defined are already assigned
            if scope_to_check['visible'] is not True:
                for visible_scope in scope_to_check['visible']:
                    # If the scope is not in the list of my scopes already assigned, return false
                    if visible_scope not in current_scopes:
                        raise WrongScopesConfigurationHiddenScope(scope)

            # If not true, we need to check if the scopes defined are already assigned
            if scope_to_check['depends']:
                for dependent_scope in scope_to_check['depends']:
                    # If the scope is not in the list of my scopes already assigned, return false
                    if dependent_scope not in scopes:
                        raise WrongScopesConfigurationMissingDependency(scope, dependent_scope)
        return scopes

    @classmethod
    def _add_default_scopes(cls, scopes: List[str]) -> List[str]:
        return scopes + DEFAULT_SCOPES
