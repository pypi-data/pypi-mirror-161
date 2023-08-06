from enum import Enum
from typing import Union

from armada_client.armada.event_pb2 import (
    JobSubmittedEvent,
    JobQueuedEvent,
    JobDuplicateFoundEvent,
    JobLeasedEvent,
    JobLeaseReturnedEvent,
    JobLeaseExpiredEvent,
    JobPendingEvent,
    JobRunningEvent,
    JobIngressInfoEvent,
    JobUnableToScheduleEvent,
    JobFailedEvent,
    JobSucceededEvent,
    JobUtilisationEvent,
    JobReprioritizingEvent,
    JobReprioritizedEvent,
    JobCancellingEvent,
    JobCancelledEvent,
    JobTerminatedEvent,
    JobUpdatedEvent
)


class EventType(Enum):
    """
    Enum for the event states.
    """

    submitted = "submitted"
    queued = "queued"
    duplicate_found = "duplicate_found"
    leased = "leased"
    lease_returned = "lease_returned"
    lease_expired = "lease_expired"
    pending = "pending"
    running = "running"
    unable_to_schedule = "unable_to_schedule"
    failed = "failed"
    succeeded = "succeeded"
    reprioritized = "reprioritized"
    cancelling = "cancelling"
    cancelled = "cancelled"
    terminated = "terminated"
    utilisation = "utilisation"
    ingress_info = "ingress_info"
    reprioritizing = "reprioritizing"
    updated = "updated"

# Union for the Job Event Types.
OneOfJobEvent = Union[
    JobSubmittedEvent,
    JobQueuedEvent,
    JobDuplicateFoundEvent,
    JobLeasedEvent,
    JobLeaseReturnedEvent,
    JobLeaseExpiredEvent,
    JobPendingEvent,
    JobRunningEvent,
    JobIngressInfoEvent,
    JobUnableToScheduleEvent,
    JobFailedEvent,
    JobSucceededEvent,
    JobUtilisationEvent,
    JobReprioritizingEvent,
    JobReprioritizedEvent,
    JobCancellingEvent,
    JobCancelledEvent,
    JobTerminatedEvent,
    JobUpdatedEvent
]
