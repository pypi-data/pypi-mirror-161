class MissingPermissionException(Exception):
    pass


class WrongScopesConfigurationMissingDependency(Exception):
    scope: str
    parent_scope: str

    def __init__(self, scope: str, parent_scope: str) -> None:
        super().__init__()
        self.scope = scope
        self.parent_scope = parent_scope


class WrongScopesConfigurationHiddenScope(Exception):
    scope: str

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.scope = scope


class WrongScopesConfigurationScopeNotFound(Exception):
    scope: str

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.scope = scope
