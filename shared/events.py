from shared.models import EventLog
from shared.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
import json

class EventStore:
    @staticmethod
    async def append_event(store_id: int, event_type: str, aggregate_id: int, aggregate_type: str, event_data: dict, vector_clock: dict):
        async with async_session() as session:
            event = EventLog(
                store_id=store_id,
                event_type=event_type,
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                event_data=json.dumps(event_data),
                vector_clock=json.dumps(vector_clock)
            )
            session.add(event)
            await session.commit()

    @staticmethod
    async def get_events(store_id: int, after_sequence: int = 0):
        async with async_session() as session:
            result = await session.execute(
                select(EventLog).where(EventLog.store_id == store_id, EventLog.sequence_number > after_sequence).order_by(EventLog.sequence_number)
            )
            return result.scalars().all()

    @staticmethod
    async def replay_events(store_id: int):
        events = await EventStore.get_events(store_id)
        for event in events:
            # Apply event to state (simplified)
            if event.event_type == "STOCK_UPDATED":
                # Update inventory
                pass
            elif event.event_type == "SALE_COMPLETED":
                # Update transaction
                pass
        return len(events)

# Vector clock utilities
def increment_vector_clock(clock: dict, node: str) -> dict:
    clock = clock.copy()
    clock[node] = clock.get(node, 0) + 1
    return clock

def merge_vector_clocks(clock1: dict, clock2: dict) -> dict:
    merged = {}
    for key in set(clock1.keys()) | set(clock2.keys()):
        merged[key] = max(clock1.get(key, 0), clock2.get(key, 0))
    return merged

def compare_vector_clocks(clock1: dict, clock2: dict) -> int:
    # 1 if clock1 > clock2, -1 if clock1 < clock2, 0 if concurrent
    greater = False
    less = False
    for key in set(clock1.keys()) | set(clock2.keys()):
        c1 = clock1.get(key, 0)
        c2 = clock2.get(key, 0)
        if c1 > c2:
            greater = True
        elif c1 < c2:
            less = True
    if greater and not less:
        return 1
    elif less and not greater:
        return -1
    else:
        return 0