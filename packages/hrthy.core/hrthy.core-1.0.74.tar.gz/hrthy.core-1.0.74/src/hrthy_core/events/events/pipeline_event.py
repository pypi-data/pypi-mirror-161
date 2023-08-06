from uuid import UUID

from hrthy_core.events.events.base_event import BaseEvent, CompanyBasePayload


class PipelineCreatedPayload(CompanyBasePayload):
    name: str


class PipelineUpdatedPayload(PipelineCreatedPayload):
    pass


class PipelineDeletedPayload(CompanyBasePayload):
    pass


class PipelineCandidateAssignedPayload(CompanyBasePayload):
    candidate_id: UUID


class PipelineCandidateUnassignedPayload(CompanyBasePayload):
    candidate_id: UUID


class PipelineCreatedEvent(BaseEvent):
    type = 'PipelineCreatedEvent'
    payload: PipelineCreatedPayload


class PipelineUpdatedEvent(BaseEvent):
    type = 'PipelineUpdatedEvent'
    payload: PipelineUpdatedPayload


class PipelineDeletedEvent(BaseEvent):
    type = 'PipelineDeletedEvent'
    payload: PipelineDeletedPayload


class PipelineCandidateAssignedEvent(BaseEvent):
    type = 'PipelineCandidateAssignedEvent'
    payload: PipelineCandidateAssignedPayload


class PipelineCandidateUnassignedEvent(BaseEvent):
    type = 'PipelineCandidateUnassignedEvent'
    payload: PipelineCandidateUnassignedPayload
