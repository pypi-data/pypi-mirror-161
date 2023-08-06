from uuid import UUID

from hrthy_core.events.events.base_event import BaseEvent, BasePayload


class RoleCreatedPayload(BasePayload):
    company_id: UUID = None
    name: str
    active: bool


class RoleUpdatedPayload(RoleCreatedPayload):
    pass


class RoleDeletedPayload(BasePayload):
    company_id: UUID = None


class RoleCreatedEvent(BaseEvent):
    type = 'RoleCreatedEvent'
    payload: RoleCreatedPayload


class RoleUpdatedEvent(BaseEvent):
    type = 'RoleUpdatedEvent'
    payload: RoleUpdatedPayload


class RoleDeletedEvent(BaseEvent):
    type = 'RoleDeletedEvent'
    payload: RoleDeletedPayload
