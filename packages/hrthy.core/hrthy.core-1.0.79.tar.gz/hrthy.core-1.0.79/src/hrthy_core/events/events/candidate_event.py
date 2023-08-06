from hrthy_core.events.events.base_event import BaseEvent, CompanyBasePayload


class CandidateCreatedPayload(CompanyBasePayload):
    first_name: str = None
    last_name: str = None
    email: str


class CandidateInvitedPayload(CandidateCreatedPayload):
    invitation_id: str


class CandidateLoggedInPayload(CompanyBasePayload):
    session_duration: int
    pass


class CandidateLoggedOutPayload(CompanyBasePayload):
    pass


class CandidateLoginRefreshedPayload(CompanyBasePayload):
    session_duration: int
    pass


class CandidateUpdatedPayload(CandidateCreatedPayload):
    pass


class CandidateLoggedInEvent(BaseEvent):
    type = 'CandidateLoggedInEvent'
    payload: CandidateLoggedInPayload


class CandidateLoggedOutEvent(BaseEvent):
    type = 'CandidateLoggedOutEvent'
    payload: CandidateLoggedOutPayload


class CandidateLoginRefreshedEvent(BaseEvent):
    type = 'CandidateLoginRefreshedEvent'
    payload: CandidateLoginRefreshedPayload


class CandidateInvitedEvent(BaseEvent):
    type = 'CandidateInvitedEvent'
    payload: CandidateInvitedPayload


class CandidateCreatedEvent(BaseEvent):
    type = 'CandidateCreatedEvent'
    payload: CandidateCreatedPayload


class CandidateUpdatedEvent(BaseEvent):
    type = 'CandidateUpdatedEvent'
    payload: CandidateUpdatedPayload
