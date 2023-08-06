from hrthy_core.events.events.candidate_event import CandidateCreatedEvent, CandidateUpdatedEvent, \
    CandidateInvitedEvent, \
    CandidateLoggedInEvent, CandidateLoggedOutEvent, CandidateLoginRefreshedEvent
from hrthy_core.events.events.company_event import CompanyCreatedEvent, CompanyUpdatedEvent, CompanyDeletedEvent, \
    CompanyRestoredEvent
from hrthy_core.events.events.pipeline_event import PipelineCreatedEvent, PipelineUpdatedEvent, PipelineDeletedEvent, \
    PipelineCandidateAssignedEvent, PipelineCandidateUnassignedEvent
from hrthy_core.events.events.role_event import RoleCreatedEvent, RoleUpdatedEvent, RoleDeletedEvent
from hrthy_core.events.events.user_event import UserCreatedEvent, UserUpdatedEvent, UserDeletedEvent, \
    UserInvitedEvent, UserLoginRefreshedEvent, UserLoggedOutEvent, UserLoggedInEvent, UserAcceptedInvitationEvent, \
    UserRestoredEvent

event_mapping = {
    # Company
    'CompanyCreatedEvent': CompanyCreatedEvent,
    'CompanyUpdatedEvent': CompanyUpdatedEvent,
    'CompanyDeletedEvent': CompanyDeletedEvent,
    'CompanyRestoredEvent': CompanyRestoredEvent,
    # User
    'UserCreatedEvent': UserCreatedEvent,
    'UserUpdatedEvent': UserUpdatedEvent,
    'UserDeletedEvent': UserDeletedEvent,
    'UserInvitedEvent': UserInvitedEvent,
    'UserRestoredEvent': UserRestoredEvent,
    'UserAcceptedInvitationEvent': UserAcceptedInvitationEvent,
    # Role
    'RoleCreatedEvent': RoleCreatedEvent,
    'RoleUpdatedEvent': RoleUpdatedEvent,
    'RoleDeletedEvent': RoleDeletedEvent,
    # User Auth
    'UserLoggedInEvent': UserLoggedInEvent,
    'UserLoggedOutEvent': UserLoggedOutEvent,
    'UserLoginRefreshedEvent': UserLoginRefreshedEvent,
    # Candidate
    'CandidateCreatedEvent': CandidateCreatedEvent,
    'CandidateUpdatedEvent': CandidateUpdatedEvent,
    'CandidateInvitedEvent': CandidateInvitedEvent,
    # Candidate Auth
    'CandidateLoggedInEvent': CandidateLoggedInEvent,
    'CandidateLoggedOutEvent': CandidateLoggedOutEvent,
    'CandidateLoginRefreshedEvent': CandidateLoginRefreshedEvent,
    # Pipeline
    'PipelineCreatedEvent': PipelineCreatedEvent,
    'PipelineUpdatedEvent': PipelineUpdatedEvent,
    'PipelineDeletedEvent': PipelineDeletedEvent,
    'PipelineCandidateAssignedEvent': PipelineCandidateAssignedEvent,
    'PipelineCandidateUnassignedEvent': PipelineCandidateUnassignedEvent
}
