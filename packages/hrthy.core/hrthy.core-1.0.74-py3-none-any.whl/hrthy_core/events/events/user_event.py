from uuid import UUID

from hrthy_core.events.events.base_event import BaseEvent, CompanyBasePayload


class UserCreatedPayload(CompanyBasePayload):
    first_name: str = None
    last_name: str = None
    email: str
    active: bool


class UserInvitedPayload(UserCreatedPayload):
    invitation_id: UUID


class UserRestoredPayload(UserCreatedPayload):
    invitation_id: UUID = None


class UserAcceptedInvitationPayload(UserCreatedPayload):
    pass


class UserLoggedInPayload(CompanyBasePayload):
    session_duration: int
    pass


class UserLoggedOutPayload(CompanyBasePayload):
    pass


class UserLoginRefreshedPayload(CompanyBasePayload):
    session_duration: int
    pass


class UserUpdatedPayload(UserCreatedPayload):
    pass


class UserDeletedPayload(CompanyBasePayload):
    pass


class UserAcceptedInvitationEvent(BaseEvent):
    type = 'UserAcceptedInvitationEvent'
    payload: UserAcceptedInvitationPayload


class UserLoggedInEvent(BaseEvent):
    type = 'UserLoggedInEvent'
    payload: UserLoggedInPayload


class UserLoggedOutEvent(BaseEvent):
    type = 'UserLoggedOutEvent'
    payload: UserLoggedOutPayload


class UserLoginRefreshedEvent(BaseEvent):
    type = 'UserLoginRefreshedEvent'
    payload: UserLoginRefreshedPayload


class UserInvitedEvent(BaseEvent):
    type = 'UserInvitedEvent'
    payload: UserInvitedPayload


class UserRestoredEvent(BaseEvent):
    type = 'UserRestoredEvent'
    payload: UserRestoredPayload


class UserCreatedEvent(BaseEvent):
    type = 'UserCreatedEvent'
    payload: UserCreatedPayload


class UserUpdatedEvent(BaseEvent):
    type = 'UserUpdatedEvent'
    payload: UserUpdatedPayload


class UserDeletedEvent(BaseEvent):
    type = 'UserDeletedEvent'
    payload: UserDeletedPayload
