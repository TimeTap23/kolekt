"""
Threads App Formatter Service

Specialized formatter for Meta's Threads app that transforms long-form content
into engaging, digestible threadstorms optimized for the 500 character limit.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ThreadPost:
    """Represents a single post in a Threads thread"""
    content: str
    post_number: int
    total_posts: int
    character_count: int
    image_suggestion: Optional[str] = None
    is_hook: bool = False
    is_conclusion: bool = False


@dataclass
class ThreadstormResult:
    """Result of threadstorm formatting"""
    posts: List[ThreadPost]
    total_posts: int
    total_characters: int
    engagement_score: float
    suggestions: List[str]
    rendered_output: str


class ThreadsFormatter:
    """Specialized formatter for Meta's Threads app"""
    
    # Threads app limits
    MAX_CHARACTERS = 500
    OPTIMAL_CHARACTERS = (200, 300)  # Target range for readability
    MIN_CHARACTERS = 50  # Minimum post length
    
    def __init__(self):
        self.hook_patterns = [
            r"^(Did you know|Here's why|The truth about|I just discovered|Breaking|🚨|💡|🔥)",
            r"^(Imagine if|What if|Picture this|Think about)",
            r"^(I'm going to share|Let me tell you|You won't believe|This will change)",
        ]
        
        self.conclusion_patterns = [
            r"(In conclusion|To summarize|The bottom line|Key takeaway|Remember|💭|🎯|✨)",
            r"(What do you think|Agree\?|Thoughts\?|Comment below|Share your experience)",
            r"(Follow for more|Save this|Bookmark|Share with friends|Tag someone)",
        ]
    
    def format_threadstorm(
        self,
        content: Optional[str] = None,
        images: Optional[List[str]] = None,
        tone: str = "professional",
        include_numbering: bool = True,
    ) -> ThreadstormResult:
        """
        Format content and optional images into a Threads threadstorm
        - Handles text-only, images-only, and text+images flows
        """
        content = content or ""
        images = images or []

        # Clean and prepare content
        cleaned_content = self._clean_content(content)

        # Split into logical chunks
        chunks = self._split_into_chunks(cleaned_content) if cleaned_content else []

        posts: List[ThreadPost] = []

        # Case: images-only (no text)
        if not chunks and images:
            total_posts = len(images)
            for i, img in enumerate(images):
                post_number = i + 1
                numbering_suffix = self._make_numbering_suffix(post_number, total_posts) if include_numbering and total_posts > 1 else ""
                post_content = numbering_suffix.strip()
                post = ThreadPost(
                    content=post_content,
                    post_number=post_number,
                    total_posts=total_posts,
                    character_count=len(post_content),
                    image_suggestion=f"Image {post_number}: {img}",
                    is_hook=post_number == 1,
                    is_conclusion=post_number == total_posts,
                )
                posts.append(post)
        else:
            # Handle text content (with or without images)
            if not chunks and cleaned_content:
                # Single short post
                chunks = [cleaned_content]
            
            total_posts = max(1, len(chunks))
            for i, chunk in enumerate(chunks or [""]):
                post_number = i + 1
                post_content = self._format_post_content(
                    chunk=chunk,
                    post_number=post_number,
                    total_posts=total_posts,
                    include_numbering=include_numbering,
                )

                is_hook = self._is_hook(chunk, post_number)
                is_conclusion = self._is_conclusion(chunk, post_number, total_posts)

                image_suggestion = self._suggest_image_placement(
                    chunk, post_number, total_posts, images
                ) if images else None

                post = ThreadPost(
                    content=post_content,
                    post_number=post_number,
                    total_posts=total_posts,
                    character_count=len(post_content),
                    image_suggestion=image_suggestion,
                    is_hook=is_hook,
                    is_conclusion=is_conclusion,
                )
                posts.append(post)

        # Calculate engagement score and suggestions
        engagement_score = self._calculate_engagement_score(posts) if posts else 0.0
        suggestions = self._generate_suggestions(posts, tone) if posts else []

        rendered_output = self.render_posts(posts)

        return ThreadstormResult(
            posts=posts,
            total_posts=len(posts),
            total_characters=sum(p.character_count for p in posts),
            engagement_score=engagement_score,
            suggestions=suggestions,
            rendered_output=rendered_output,
        )
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        return content.strip()
    
    def _split_into_chunks(self, content: str) -> List[str]:
        """Split content into optimal chunks for Threads posts"""
        if not content.strip():
            return []
            
        chunks: List[str] = []
        paragraphs = content.split('\n\n')
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If paragraph is too long, split by sentences
            if len(paragraph) > self.OPTIMAL_CHARACTERS[1]:
                sentences = self._split_into_sentences(paragraph)
                for sentence in sentences:
                    test_chunk = current_chunk + "\n\n" + sentence if current_chunk else sentence
                    if len(test_chunk) <= self.OPTIMAL_CHARACTERS[1]:
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
            else:
                # Try to add paragraph to current chunk
                test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
                if len(test_chunk) <= self.OPTIMAL_CHARACTERS[1]:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # If no chunks were created, the content is short - create a single chunk
        if not chunks and content.strip():
            chunks = [content.strip()]

        chunks = self._merge_short_chunks(chunks)
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _merge_short_chunks(self, chunks: List[str]) -> List[str]:
        if len(chunks) <= 1:
            return chunks
        merged_chunks: List[str] = []
        i = 0
        while i < len(chunks):
            current_chunk = chunks[i]
            if len(current_chunk) < self.MIN_CHARACTERS and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                combined = current_chunk + "\n\n" + next_chunk
                if len(combined) <= self.OPTIMAL_CHARACTERS[1]:
                    merged_chunks.append(combined)
                    i += 2
                else:
                    merged_chunks.append(current_chunk)
                    i += 1
            else:
                merged_chunks.append(current_chunk)
                i += 1
        return merged_chunks

    def _make_numbering_suffix(self, post_number: int, total_posts: int) -> str:
        return f"\n\n{post_number}/{total_posts}"

    def _format_post_content(
        self,
        chunk: str,
        post_number: int,
        total_posts: int,
        include_numbering: bool,
    ) -> str:
        """Format a chunk into a Threads post ensuring hard 500-char limit including numbering"""
        numbering_suffix = self._make_numbering_suffix(post_number, total_posts) if include_numbering and total_posts > 1 else ""
        max_content_length = self.MAX_CHARACTERS - len(numbering_suffix)
        content = chunk
        if len(content) > max_content_length:
            # Reserve space for an ellipsis if we truncate
            reserve = 3 if max_content_length >= 3 else 0
            content = content[: max_content_length - reserve]
            if reserve:
                content += "..."
        content += numbering_suffix
        # Final guard (shouldn't be needed, but safe)
        if len(content) > self.MAX_CHARACTERS:
            content = content[: self.MAX_CHARACTERS]
        return content
    
    def _is_hook(self, chunk: str, post_number: int) -> bool:
        if post_number != 1:
            return False
        for pattern in self.hook_patterns:
            if re.search(pattern, chunk, re.IGNORECASE):
                return True
        first_sentence = chunk.split('.')[0].lower() if chunk else ""
        engaging_openers = [
            "here's", "this is", "let me", "i'm going", "you need to",
            "the secret", "the truth", "breaking", "just discovered",
        ]
        return any(opener in first_sentence for opener in engaging_openers)
    
    def _is_conclusion(self, chunk: str, post_number: int, total_posts: int) -> bool:
        if post_number != total_posts:
            return False
        for pattern in self.conclusion_patterns:
            if re.search(pattern, chunk, re.IGNORECASE):
                return True
        cta_phrases = [
            "what do you think", "agree", "thoughts", "comment", "share",
            "follow", "save", "bookmark", "tag", "let me know",
        ]
        return any(phrase in (chunk or "").lower() for phrase in cta_phrases)
    
    def _suggest_image_placement(
        self,
        chunk: str,
        post_number: int,
        total_posts: int,
        images: Optional[List[str]] = None,
    ) -> Optional[str]:
        if not images:
            return None
        if post_number == 1 and images:
            return f"Image 1: {images[0]}"
        if post_number > 1 and post_number < total_posts:
            image_index = post_number - 1
            if image_index < len(images):
                return f"Image {post_number}: {images[image_index]}"
        if post_number == total_posts and images:
            return f"Image {len(images)}: {images[-1]}"
        return None
    
    def _calculate_engagement_score(self, posts: List[ThreadPost]) -> float:
        if not posts:
            return 0.0
        score = 0.0
        for post in posts:
            if self.OPTIMAL_CHARACTERS[0] <= post.character_count <= self.OPTIMAL_CHARACTERS[1]:
                score += 0.2
            if post.is_hook:
                score += 0.3
            if post.is_conclusion:
                score += 0.2
            if post.image_suggestion:
                score += 0.1
            if post.character_count < self.MIN_CHARACTERS:
                score -= 0.1
            elif post.character_count > self.MAX_CHARACTERS:
                score -= 0.2
        return max(0.0, min(1.0, score / len(posts)))
    
    def _generate_suggestions(self, posts: List[ThreadPost], tone: str) -> List[str]:
        suggestions: List[str] = []
        if not any(p.is_hook for p in posts):
            suggestions.append("Consider adding a compelling hook to your first post")
        if not any(p.is_conclusion for p in posts):
            suggestions.append("Add a strong conclusion or call-to-action to your final post")
        short_posts = [p for p in posts if p.character_count < self.MIN_CHARACTERS]
        if short_posts:
            suggestions.append(f"Consider combining {len(short_posts)} short posts for better engagement")
        long_posts = [p for p in posts if p.character_count > self.OPTIMAL_CHARACTERS[1]]
        if long_posts:
            suggestions.append(f"Consider breaking down {len(long_posts)} long posts for better readability")
        if tone == "professional":
            suggestions.append("Consider adding industry-specific hashtags for better reach")
        elif tone == "casual":
            suggestions.append("Add emojis to make your posts more engaging")
        return suggestions

    def render_posts(self, posts: List[ThreadPost]) -> str:
        """Render posts as human-readable output with image placement notes.
        This text output is for copy/paste; image notes are guidance and are not part of the actual post content.
        """
        lines: List[str] = []
        for p in posts:
            lines.append(f"Post {p.post_number}/{p.total_posts}:")
            lines.append(p.content)
            if p.image_suggestion:
                lines.append(f"[Attach here] {p.image_suggestion}")
            lines.append("")
        return "\n".join(lines).strip()
