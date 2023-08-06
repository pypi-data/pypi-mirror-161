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
    SCOPE_COMPANY_MY_DELETE, SCOPE_COMPANY_MY_RESTORE, SCOPE_ROLE_MY_ASSIGN_GLOBAL, SCOPE_ROLE_MYSELF_GET

DESCRIPTIONS_SCOPES = {
    SCOPE_ROLE_MY_ASSIGN_GLOBAL: 'User can assign global permissions to the role',
    SCOPE_COMPANY_LIST: 'User can list all the companies',
    SCOPE_COMPANY_CREATE: 'User can create a new company',
    SCOPE_COMPANY_UPDATE: 'User can update a company',
    SCOPE_COMPANY_DELETE: 'User can delete a company',
    SCOPE_COMPANY_RESTORE: 'User can restore a company',

    SCOPE_USER_LIST: 'User can list all the users in other companies',
    SCOPE_USER_CREATE: 'User can create a new user in other companies',
    SCOPE_USER_UPDATE: 'User can update a user in other companies',
    SCOPE_USER_DELETE: 'User can delete a user in other companies',

    SCOPE_ROLE_LIST: 'User can list all the roles in other companies',
    SCOPE_ROLE_CREATE: 'User can create a new role in other companies',
    SCOPE_ROLE_UPDATE: 'User can update a role in other companies',
    SCOPE_ROLE_DELETE: 'User can delete a role in other companies',

    SCOPE_CANDIDATE_LIST: 'User can list all the candidates in other companies',
    SCOPE_CANDIDATE_CREATE: 'User can create a new candidate in other companies',
    SCOPE_CANDIDATE_UPDATE: 'User can update a candidate in other companies',
    SCOPE_CANDIDATE_DELETE: 'User can delete a candidate in other companies',

    SCOPE_PIPELINE_LIST: 'User can list all the pipelines in other companies',
    SCOPE_PIPELINE_CREATE: 'User can create a new pipeline in other companies',
    SCOPE_PIPELINE_UPDATE: 'User can update a pipeline in other companies',
    SCOPE_PIPELINE_DELETE: 'User can delete a pipeline in other companies',

    SCOPE_PIPELINE_CANDIDATE_ASSIGN: 'User can assign a candidate to a pipeline in other companies',
    SCOPE_PIPELINE_CANDIDATE_UNASSIGN: 'User can unassign a candidate from a pipeline in other companies',

    # Company Roles
    SCOPE_COMPANY_MY_UPDATE: 'User can update its company',
    SCOPE_COMPANY_MY_DELETE: 'User can delete its company',
    SCOPE_COMPANY_MY_RESTORE: 'User can restore its company',

    SCOPE_USER_MY_LIST: 'User can list all the users in its company',
    SCOPE_USER_MY_CREATE: 'User can create a new user its its company',
    SCOPE_USER_MY_UPDATE: 'User can update a user in its company',
    SCOPE_USER_MY_DELETE: 'User can delete a user in its company',

    SCOPE_ROLE_MY_LIST: 'User can list all the roles in its company',
    SCOPE_ROLE_MY_CREATE: 'User can create a new role in its company',
    SCOPE_ROLE_MY_UPDATE: 'User can update a role in its company',
    SCOPE_ROLE_MY_DELETE: 'User can delete a role in its company',
    SCOPE_ROLE_MYSELF_GET: 'User can retrieve the role assigned to it',

    SCOPE_CANDIDATE_MY_LIST: 'User can list all the candidates in its company',
    SCOPE_CANDIDATE_MY_CREATE: 'User can create a new candidate in its company',
    SCOPE_CANDIDATE_MY_UPDATE: 'User can update a candidate in its company',
    SCOPE_CANDIDATE_MY_DELETE: 'User can delete a candidate in its company',

    SCOPE_PIPELINE_MY_LIST: 'User can list all the pipelines in its company',
    SCOPE_PIPELINE_MY_CREATE: 'User can create a new pipeline in its company',
    SCOPE_PIPELINE_MY_UPDATE: 'User can update a pipeline in its company',
    SCOPE_PIPELINE_MY_DELETE: 'User can delete a pipeline in its company',

    SCOPE_PIPELINE_CANDIDATE_MY_ASSIGN: 'User can assign a candidate to a pipeline in its company',
    SCOPE_PIPELINE_CANDIDATE_MY_UNASSIGN: 'User can unassign a candidate from a pipeline in its company',
}
