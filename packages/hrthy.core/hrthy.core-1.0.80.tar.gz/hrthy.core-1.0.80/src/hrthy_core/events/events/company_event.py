from hrthy_core.events.events.base_event import BasePayload, BaseEvent


class CompanyCreatedPayload(BasePayload):
    name: str
    email: str
    active: bool


class CompanyUpdatedPayload(CompanyCreatedPayload):
    pass


class CompanyDeletedPayload(BasePayload):
    pass


class CompanyRestoredPayload(BasePayload):
    pass


class CompanyCreatedEvent(BaseEvent):
    type = 'CompanyCreatedEvent'
    payload: CompanyCreatedPayload


class CompanyUpdatedEvent(BaseEvent):
    type = 'CompanyUpdatedEvent'
    payload: CompanyUpdatedPayload


class CompanyDeletedEvent(BaseEvent):
    type = 'CompanyDeletedEvent'
    payload: CompanyDeletedPayload


class CompanyRestoredEvent(BaseEvent):
    type = 'CompanyRestoredEvent'
    payload: CompanyRestoredPayload
