from enum import Enum


class Topic(Enum):
    RETRY_V1 = 'hrthy.retry.v1'
    COMPANY_V1 = 'hrthy.company.v1'
    USER_V1 = 'hrthy.user.v1'
    USER_AUTH_V1 = 'hrthy.user.auth.v1'
    ROLE_V1 = 'hrthy.role.v1'
    CANDIDATE_V1 = 'hrthy.candidate.v1'
    CANDIDATE_AUTH_V1 = 'hrthy.candidate.auth.v1'
    PIPELINE_V1 = 'hrthy.pipeline.v1'


class TopicGroup(Enum):
    COMPANY = 'company'
    CANDIDATE = 'candidate'
    USER = 'user'
    PIPELINE = 'pipeline'
