from __future__ import annotations

"""
Curation and drafting pipeline for Kolekt.

This module provides a minimal, composable pipeline:
- fetch_source_items: adapters pull raw text metadata
- normalize_content: basic cleaning
- compute_embeddings: optional semantic vectorization
- score_items: rule-based scoring with optional ML hooks
- enqueue_for_review: create review queue entries
- draft_variants: format per channel using existing Threads formatter service

All steps are synchronous for simplicity; integrate background workers later.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterable
import re

from src.services.supabase import supabase_service
from src.services.templates import TemplateLibrary
from src.services.threads_formatter import ThreadsFormatter


@dataclass
class ContentItem:
    title: str
    url: Optional[str]
    raw: str
    author: Optional[str] = None
    published_at: Optional[str] = None
    lang: Optional[str] = None
    metadata: Dict[str, Any] = None


class CurationService:
    def __init__(self):
        self.template_library = TemplateLibrary()
        self.formatter = ThreadsFormatter()

    # --- Ingestion (minimal RSS-like hook) ---
    def ingest_manual(self, user_id: str, items: Iterable[ContentItem]) -> List[str]:
        """Insert provided items into content_items, return item IDs."""
        inserted_ids: List[str] = []
        for it in items:
            normalized = self._normalize(it.raw)
            res = supabase_service.client.table("content_items").insert({
                "user_id": user_id,
                "title": it.title,
                "author": it.author,
                "url": it.url,
                "published_at": it.published_at,
                "lang": it.lang or self._detect_lang(it.raw),
                "raw": it.raw,
                "normalized": normalized,
                "metadata": it.metadata or {},
            }).execute()
            if res.data:
                inserted_ids.append(res.data[0]["id"])
        return inserted_ids

    # --- Scoring / Curation ---
    def score_and_enqueue(self, user_id: str, item_ids: List[str]) -> List[Dict[str, Any]]:
        """Simple heuristic scoring and enqueue into review_queue."""
        queued: List[Dict[str, Any]] = []
        for item_id in item_ids:
            item_resp = supabase_service.client.table("content_items").select("title, normalized, metadata").eq("id", item_id).single().execute()
            if not item_resp.data:
                continue
            text = item_resp.data.get("normalized") or ""
            score, reasons = self._score(text)
            q = supabase_service.client.table("review_queue").insert({
                "user_id": user_id,
                "item_id": item_id,
                "score": score,
                "reasons": reasons,
                "status": "pending"
            }).execute()
            if q.data:
                queued.append(q.data[0])
        return queued

    # --- Drafting ---
    def draft_threads_variants(self, user_id: str, item_id: str, variants: int = 2) -> List[Dict[str, Any]]:
        """Create N draft variants for Threads using the existing formatter."""
        item = supabase_service.client.table("content_items").select("title, normalized").eq("id", item_id).single().execute().data
        if not item:
            return []
        base = item.get("normalized") or item.get("title") or ""
        results: List[Dict[str, Any]] = []
        for i in range(variants):
            formatted = self.formatter.format_threadstorm(content=base, images=None, tone="professional", include_numbering=True)
            draft_payload = {
                "user_id": user_id,
                "item_id": item_id,
                "channel": "threads",
                "variant": i + 1,
                "content": {
                    "posts": [p.content for p in formatted.posts],
                    "suggestions": formatted.suggestions,
                    "engagement_score": formatted.engagement_score,
                },
                "quality": {"total_characters": formatted.total_characters}
            }
            ins = supabase_service.client.table("channel_drafts").insert(draft_payload).execute()
            if ins.data:
                results.append(ins.data[0])
        return results

    # --- Utils ---
    def _normalize(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text or "").strip()
        text = text.replace("\u00a0", " ")
        return text

    def _detect_lang(self, text: str) -> str:
        # lightweight heuristic
        return "en"

    def _score(self, text: str) -> (float, List[str]):
        reasons: List[str] = []
        score = 0.5
        length = len(text)
        if 400 < length < 4000:
            score += 0.2
        if any(k in text.lower() for k in ["guide", "insights", "how to", "analysis"]):
            score += 0.15
            reasons.append("keywords")
        if text.count("http") <= 2:
            score += 0.05
        score = max(0.0, min(1.0, score))
        return score, reasons

    def get_review_queue(self, user_id: str) -> List[Dict]:
        """Get items in review queue for a user"""
        try:
            result = supabase_service.client.table("review_queue").select(
                "*, content_items(*)",
                count="exact"
            ).eq("user_id", user_id).eq("status", "pending").order("score", desc=True).execute()
            
            items = []
            if result.data:
                for queue_item in result.data:
                    content_item = queue_item.get("content_items", {})
                    items.append({
                        "id": queue_item["id"],
                        "item_id": queue_item["item_id"],
                        "score": queue_item["score"],
                        "reasons": queue_item.get("reasons", []),
                        "title": content_item.get("title"),
                        "normalized": content_item.get("normalized"),
                        "url": content_item.get("url"),
                        "created_at": queue_item["created_at"]
                    })
            
            return items
        except Exception as e:
            print(f"Error fetching review queue: {e}")
            return []

    def approve_item(self, user_id: str, item_id: str) -> bool:
        """Approve an item in the review queue"""
        try:
            result = supabase_service.client.table("review_queue").update({
                "status": "approved",
                "updated_at": "now()"
            }).eq("id", item_id).eq("user_id", user_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error approving item: {e}")
            return False

    def reject_item(self, user_id: str, item_id: str) -> bool:
        """Reject an item in the review queue"""
        try:
            result = supabase_service.client.table("review_queue").update({
                "status": "rejected",
                "updated_at": "now()"
            }).eq("id", item_id).eq("user_id", user_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error rejecting item: {e}")
            return False


curation_service = CurationService()


