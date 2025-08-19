from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
from typing import List

from src.services.curation import curation_service, ContentItem


curation_router = APIRouter()


class ManualIngestItem(BaseModel):
    title: str
    url: str | None = None
    raw: str


@curation_router.post("/ingest/manual")
async def ingest_manual(user_id: str = Query(...), items: List[ManualIngestItem] = Body(...)):
    ids = curation_service.ingest_manual(
        user_id=user_id,
        items=[ContentItem(title=i.title, url=i.url, raw=i.raw) for i in items]
    )
    queued = curation_service.score_and_enqueue(user_id, ids)
    return {"inserted": ids, "queued": queued}


@curation_router.post("/drafts/threads")
async def drafts_threads(user_id: str = Query(...), item_id: str = Query(...), variants: int = Query(2)):
    drafts = curation_service.draft_threads_variants(user_id, item_id, variants)
    return {"drafts": drafts}


@curation_router.get("/review-queue")
async def get_review_queue(user_id: str = Query(...)):
    """Get items in review queue for a user"""
    items = curation_service.get_review_queue(user_id)
    return {"items": items}


@curation_router.post("/review-queue/{item_id}/approve")
async def approve_item(item_id: str, user_id: str = Body(...)):
    """Approve an item in the review queue"""
    result = curation_service.approve_item(user_id, item_id)
    return {"success": result}


@curation_router.post("/review-queue/{item_id}/reject")
async def reject_item(item_id: str, user_id: str = Body(...)):
    """Reject an item in the review queue"""
    result = curation_service.reject_item(user_id, item_id)
    return {"success": result}


