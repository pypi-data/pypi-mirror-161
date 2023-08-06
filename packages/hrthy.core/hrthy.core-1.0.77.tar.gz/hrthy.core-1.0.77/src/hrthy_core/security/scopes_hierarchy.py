from hrthy_core.security.scopes import SCOPE_COMPANY_LIST, SCOPE_COMPANY_CREATE, SCOPE_COMPANY_UPDATE, \
    SCOPE_COMPANY_DELETE, SCOPE_COMPANY_RESTORE, SCOPE_USER_LIST, SCOPE_USER_CREATE, SCOPE_USER_UPDATE, \
    SCOPE_USER_DELETE, SCOPE_COMPANY_MY_UPDATE, SCOPE_USER_MY_LIST, \
    SCOPE_USER_MY_CREATE, SCOPE_USER_MY_UPDATE, SCOPE_USER_MY_DELETE, SCOPE_ROLE_LIST, SCOPE_ROLE_CREATE, \
    SCOPE_ROLE_UPDATE, SCOPE_ROLE_DELETE, SCOPE_ROLE_MY_LIST, SCOPE_CANDIDATE_LIST, SCOPE_CANDIDATE_CREATE, \
    SCOPE_CANDIDATE_UPDATE, SCOPE_CANDIDATE_DELETE, SCOPE_CANDIDATE_MY_LIST, \
    SCOPE_CANDIDATE_MY_CREATE, SCOPE_CANDIDATE_MY_UPDATE, SCOPE_CANDIDATE_MY_DELETE, SCOPE_PIPELINE_LIST, \
    SCOPE_PIPELINE_CREATE, SCOPE_PIPELINE_UPDATE, SCOPE_PIPELINE_DELETE, SCOPE_PIPELINE_MY_LIST, \
    SCOPE_PIPELINE_MY_CREATE, SCOPE_PIPELINE_MY_UPDATE, SCOPE_PIPELINE_MY_DELETE, SCOPE_PIPELINE_CANDIDATE_ASSIGN, \
    SCOPE_PIPELINE_CANDIDATE_UNASSIGN, SCOPE_PIPELINE_CANDIDATE_MY_ASSIGN, \
    SCOPE_PIPELINE_CANDIDATE_MY_UNASSIGN, SCOPE_ROLE_MY_CREATE, SCOPE_ROLE_MY_UPDATE, SCOPE_ROLE_MY_DELETE, \
    SCOPE_COMPANY_MY_DELETE, SCOPE_COMPANY_MY_RESTORE, SCOPE_ROLE_MY_ASSIGN_GLOBAL
from hrthy_core.security.types import ScopeType

# Scopes hierarchy:
# type -> Scope type from GLOBAL, COMPANY, PERSONAL
# includes -> List of lower permissions that are included in the selected one
# depends -> List of permissions that are mandatory to assign the selected one
# visible -> List of permissions already assigned to the user role, that are needed to show the selected one
HIERARCHY_SCOPES = {
    SCOPE_ROLE_MY_ASSIGN_GLOBAL: {'type': ScopeType.GLOBAL, 'includes': [], 'depends': [], 'visible': False},
    SCOPE_COMPANY_LIST: {'type': ScopeType.GLOBAL, 'includes': [], 'depends': [],
                         'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_COMPANY_CREATE: {'type': ScopeType.GLOBAL, 'includes': [], 'depends': [SCOPE_COMPANY_LIST],
                           'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_COMPANY_UPDATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_COMPANY_MY_UPDATE],
                           'depends': [SCOPE_COMPANY_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_COMPANY_DELETE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_COMPANY_MY_DELETE],
                           'depends': [SCOPE_COMPANY_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_COMPANY_RESTORE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_COMPANY_MY_RESTORE],
                            'depends': [SCOPE_COMPANY_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    SCOPE_USER_LIST: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_USER_MY_LIST], 'depends': [],
                      'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_USER_CREATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_USER_MY_CREATE], 'depends': [SCOPE_USER_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_USER_UPDATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_USER_MY_UPDATE], 'depends': [SCOPE_USER_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_USER_DELETE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_USER_MY_DELETE], 'depends': [SCOPE_USER_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    SCOPE_ROLE_LIST: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_ROLE_MY_LIST], 'depends': [],
                      'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_ROLE_CREATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_ROLE_MY_CREATE], 'depends': [SCOPE_ROLE_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_ROLE_UPDATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_ROLE_MY_UPDATE], 'depends': [SCOPE_ROLE_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_ROLE_DELETE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_ROLE_MY_DELETE], 'depends': [SCOPE_ROLE_LIST],
                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    SCOPE_CANDIDATE_LIST: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_ROLE_MY_LIST], 'depends': [],
                           'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_CANDIDATE_CREATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_CANDIDATE_MY_CREATE],
                             'depends': [SCOPE_CANDIDATE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_CANDIDATE_UPDATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_CANDIDATE_MY_UPDATE],
                             'depends': [SCOPE_CANDIDATE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_CANDIDATE_DELETE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_CANDIDATE_MY_DELETE],
                             'depends': [SCOPE_CANDIDATE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    SCOPE_PIPELINE_LIST: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_MY_LIST], 'depends': [],
                          'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_PIPELINE_CREATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_MY_CREATE],
                            'depends': [SCOPE_PIPELINE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_PIPELINE_UPDATE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_MY_UPDATE],
                            'depends': [SCOPE_PIPELINE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_PIPELINE_DELETE: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_MY_DELETE],
                            'depends': [SCOPE_PIPELINE_LIST], 'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    SCOPE_PIPELINE_CANDIDATE_ASSIGN: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_CANDIDATE_MY_ASSIGN],
                                      'depends': [SCOPE_PIPELINE_LIST, SCOPE_CANDIDATE_LIST],
                                      'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},
    SCOPE_PIPELINE_CANDIDATE_UNASSIGN: {'type': ScopeType.GLOBAL, 'includes': [SCOPE_PIPELINE_CANDIDATE_MY_UNASSIGN],
                                        'depends': [SCOPE_PIPELINE_LIST, SCOPE_CANDIDATE_LIST],
                                        'visible': [SCOPE_ROLE_MY_ASSIGN_GLOBAL]},

    # Company Roles
    SCOPE_COMPANY_MY_UPDATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': True},
    SCOPE_COMPANY_MY_DELETE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': False},
    SCOPE_COMPANY_MY_RESTORE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': False},

    SCOPE_USER_MY_LIST: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': True},
    SCOPE_USER_MY_CREATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_USER_MY_LIST], 'visible': True},
    SCOPE_USER_MY_UPDATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_USER_MY_LIST], 'visible': True},
    SCOPE_USER_MY_DELETE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_USER_MY_LIST], 'visible': True},

    SCOPE_ROLE_MY_LIST: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': True},
    SCOPE_ROLE_MY_CREATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_ROLE_MY_LIST], 'visible': True},
    SCOPE_ROLE_MY_UPDATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_ROLE_MY_LIST], 'visible': True},
    SCOPE_ROLE_MY_DELETE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_ROLE_MY_LIST], 'visible': True},

    SCOPE_CANDIDATE_MY_LIST: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': True},
    SCOPE_CANDIDATE_MY_CREATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_CANDIDATE_MY_LIST],
                                'visible': True},
    SCOPE_CANDIDATE_MY_UPDATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_CANDIDATE_MY_LIST],
                                'visible': True},
    SCOPE_CANDIDATE_MY_DELETE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_CANDIDATE_MY_LIST],
                                'visible': True},

    SCOPE_PIPELINE_MY_LIST: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [], 'visible': True},
    SCOPE_PIPELINE_MY_CREATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_PIPELINE_MY_LIST],
                               'visible': True},
    SCOPE_PIPELINE_MY_UPDATE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_PIPELINE_MY_LIST],
                               'visible': True},
    SCOPE_PIPELINE_MY_DELETE: {'type': ScopeType.COMPANY, 'includes': [], 'depends': [SCOPE_PIPELINE_MY_LIST],
                               'visible': True},

    SCOPE_PIPELINE_CANDIDATE_MY_ASSIGN: {'type': ScopeType.COMPANY, 'includes': [],
                                         'depends': [SCOPE_PIPELINE_MY_LIST, SCOPE_CANDIDATE_MY_LIST], 'visible': True},
    SCOPE_PIPELINE_CANDIDATE_MY_UNASSIGN: {'type': ScopeType.COMPANY, 'includes': [],
                                           'depends': [SCOPE_PIPELINE_MY_LIST, SCOPE_CANDIDATE_MY_LIST],
                                           'visible': True},
}
