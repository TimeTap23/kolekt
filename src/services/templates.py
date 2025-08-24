"""
Template Library for Kolekt

Pre-built kolekt templates for different industries and use cases.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class TemplateCategory(Enum):
    BUSINESS = "business"
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    MARKETING = "marketing"
    PERSONAL = "personal"


@dataclass
class Template:
    id: str
    name: str
    description: str
    category: TemplateCategory
    content: str
    tone: str
    tags: List[str]
    usage_count: int = 0
    is_featured: bool = False


class TemplateLibrary:
    """Template library for Kolekt"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> List[Template]:
        """Load all available templates"""
        return [
            # Business Templates
            Template(
                id="business-product-launch",
                name="Product Launch",
                description="Announce a new product or service with excitement",
                category=TemplateCategory.BUSINESS,
                content="🚀 BIG NEWS: We're launching something amazing!\n\nAfter months of hard work, we're finally ready to share [PRODUCT/SERVICE] with the world.\n\nHere's what makes it special:\n\n• [FEATURE 1]\n• [FEATURE 2]\n• [FEATURE 3]\n\nBut here's the best part: [UNIQUE VALUE PROPOSITION]\n\nWe've been testing this with [X] users and the results are incredible.\n\nWant to be among the first to try it? Drop a comment below!\n\n#ProductLaunch #Innovation #Business",
                tone="professional",
                tags=["launch", "product", "business", "announcement"],
                is_featured=True
            ),
            
            Template(
                id="business-lesson-learned",
                name="Business Lesson",
                description="Share a valuable business lesson or insight",
                category=TemplateCategory.BUSINESS,
                content="💡 The biggest lesson I learned in business this year:\n\n[LESSON TITLE]\n\nHere's what happened:\n\n[STORY/EXPERIENCE]\n\nWhat I learned:\n\n• [INSIGHT 1]\n• [INSIGHT 2]\n• [INSIGHT 3]\n\nThe result? [OUTCOME]\n\nThis changed everything for our business.\n\nWhat's the biggest lesson you've learned recently? Share below!\n\n#BusinessLessons #Growth #Entrepreneurship",
                tone="professional",
                tags=["lesson", "business", "insight", "growth"]
            ),
            
            # Tech Templates
            Template(
                id="tech-tutorial",
                name="Tech Tutorial",
                description="Break down a technical concept into digestible posts",
                category=TemplateCategory.TECH,
                content="🧠 Want to learn [TECHNICAL CONCEPT]?\n\nI'll break it down in simple terms.\n\nWhat is [CONCEPT]?\n\n[EXPLANATION]\n\nWhy does it matter?\n\n[IMPORTANCE]\n\nHere's how it works:\n\n• [STEP 1]\n• [STEP 2]\n• [STEP 3]\n\nReal-world example:\n\n[EXAMPLE]\n\nThat's it! Simple, right?\n\nWhat tech concept would you like me to explain next?\n\n#TechTutorial #Learning #Technology",
                tone="educational",
                tags=["tutorial", "tech", "learning", "explanation"],
                is_featured=True
            ),
            
            Template(
                id="tech-trend-analysis",
                name="Tech Trend Analysis",
                description="Analyze and discuss emerging technology trends",
                category=TemplateCategory.TECH,
                content="🔮 The future of [TECH TREND] is here.\n\nHere's what you need to know:\n\nCurrent state:\n\n[WHERE WE ARE NOW]\n\nWhat's changing:\n\n[TREND ANALYSIS]\n\nWhy it matters:\n\n[IMPACT]\n\nWhat's next:\n\n[PREDICTIONS]\n\nMy take:\n\n[OPINION]\n\nThis will reshape [INDUSTRY] in the next [TIMEFRAME].\n\nAgree? Disagree? Let's discuss!\n\n#TechTrends #Future #Innovation",
                tone="analytical",
                tags=["trends", "tech", "analysis", "future"]
            ),
            
            # Lifestyle Templates
            Template(
                id="lifestyle-morning-routine",
                name="Morning Routine",
                description="Share your morning routine for productivity and wellness",
                category=TemplateCategory.LIFESTYLE,
                content="☀️ My morning routine that changed everything:\n\n5:30 AM - Wake up\n\n[ACTIVITY 1]\n\n6:00 AM - [ACTIVITY 2]\n\n6:30 AM - [ACTIVITY 3]\n\n7:00 AM - [ACTIVITY 4]\n\nWhy this works:\n\n• [BENEFIT 1]\n• [BENEFIT 2]\n• [BENEFIT 3]\n\nThe result? [OUTCOME]\n\nYour morning routine can make or break your day.\n\nWhat's your secret to a great morning?\n\n#MorningRoutine #Productivity #Wellness",
                tone="casual",
                tags=["routine", "morning", "productivity", "wellness"]
            ),
            
            Template(
                id="lifestyle-book-review",
                name="Book Review",
                description="Share insights from a book you've read",
                category=TemplateCategory.LIFESTYLE,
                content="📚 Just finished reading [BOOK TITLE]\n\nHere are my key takeaways:\n\nThe main idea:\n\n[BOOK'S CORE MESSAGE]\n\n3 things that stuck with me:\n\n1. [TAKEAWAY 1]\n2. [TAKEAWAY 2]\n3. [TAKEAWAY 3]\n\nHow it changed my thinking:\n\n[IMPACT]\n\nWould I recommend it?\n\n[RECOMMENDATION]\n\nRating: [X]/5 stars\n\nWhat book should I read next?\n\n#BookReview #Reading #Learning",
                tone="conversational",
                tags=["book", "review", "reading", "learning"]
            ),
            
            # Education Templates
            Template(
                id="education-study-tips",
                name="Study Tips",
                description="Share effective study strategies and learning techniques",
                category=TemplateCategory.EDUCATION,
                content="🎓 Want to study smarter, not harder?\n\nHere are the study techniques that actually work:\n\n1. [TECHNIQUE 1]\n\nWhy it works: [EXPLANATION]\n\n2. [TECHNIQUE 2]\n\nWhy it works: [EXPLANATION]\n\n3. [TECHNIQUE 3]\n\nWhy it works: [EXPLANATION]\n\nPro tip: [ADVICE]\n\nThese methods helped me [ACHIEVEMENT].\n\nWhat's your favorite study technique?\n\n#StudyTips #Learning #Education",
                tone="educational",
                tags=["study", "learning", "education", "tips"]
            ),
            
            # Marketing Templates
            Template(
                id="marketing-case-study",
                name="Marketing Case Study",
                description="Share a successful marketing campaign or strategy",
                category=TemplateCategory.MARKETING,
                content="📈 How we [ACHIEVED RESULT] with [STRATEGY]:\n\nThe challenge:\n\n[PROBLEM]\n\nOur approach:\n\n[STRATEGY]\n\nThe execution:\n\n• [STEP 1]\n• [STEP 2]\n• [STEP 3]\n\nThe results:\n\n[RESULTS WITH NUMBERS]\n\nKey learnings:\n\n[INSIGHTS]\n\nWhat worked:\n\n[SUCCESS FACTORS]\n\nThis strategy can work for any [INDUSTRY].\n\nWant the full breakdown? Comment below!\n\n#Marketing #CaseStudy #Results",
                tone="professional",
                tags=["marketing", "case-study", "results", "strategy"],
                is_featured=True
            ),
            
            # Personal Templates
            Template(
                id="personal-achievement",
                name="Personal Achievement",
                description="Celebrate and share a personal milestone or achievement",
                category=TemplateCategory.PERSONAL,
                content="🎉 I did it! [ACHIEVEMENT]\n\nThis has been [TIMEFRAME] in the making.\n\nThe journey:\n\n[STORY]\n\nWhat I learned:\n\n• [LESSON 1]\n• [LESSON 2]\n• [LESSON 3]\n\nThe biggest challenge:\n\n[CHALLENGE]\n\nHow I overcame it:\n\n[SOLUTION]\n\nTo everyone who supported me: Thank you!\n\nYour turn: What are you celebrating today?\n\n#Achievement #Success #Gratitude",
                tone="personal",
                tags=["achievement", "success", "personal", "celebration"]
            ),
            
            Template(
                id="personal-reflection",
                name="Personal Reflection",
                description="Share a personal reflection or life lesson",
                category=TemplateCategory.PERSONAL,
                content="🤔 A thought that's been on my mind:\n\n[REFLECTION TOPIC]\n\nHere's why:\n\n[EXPLANATION]\n\nWhat I've realized:\n\n[INSIGHT]\n\nHow it's changed me:\n\n[IMPACT]\n\nThe lesson:\n\n[LEARNING]\n\nLife has a way of teaching us what we need to learn.\n\nWhat's been on your mind lately?\n\n#Reflection #Life #Growth",
                tone="personal",
                tags=["reflection", "life", "growth", "personal"]
            ),
        ]
    
    def get_templates(self, category: Optional[TemplateCategory] = None) -> List[Template]:
        """Get templates, optionally filtered by category"""
        if category:
            return [t for t in self.templates if t.category == category]
        return self.templates
    
    def get_featured_templates(self) -> List[Template]:
        """Get featured templates"""
        return [t for t in self.templates if t.is_featured]
    
    def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def search_templates(self, query: str) -> List[Template]:
        """Search templates by name, description, or tags"""
        query = query.lower()
        results = []
        
        for template in self.templates:
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def get_categories(self) -> List[Dict]:
        """Get all available categories with template counts"""
        categories = {}
        for template in self.templates:
            cat = template.category.value
            if cat not in categories:
                categories[cat] = {
                    "name": template.category.value.title(),
                    "count": 0,
                    "icon": self._get_category_icon(template.category)
                }
            categories[cat]["count"] += 1
        
        return list(categories.values())
    
    def _get_category_icon(self, category: TemplateCategory) -> str:
        """Get icon for category"""
        icons = {
            TemplateCategory.BUSINESS: "💼",
            TemplateCategory.TECH: "💻",
            TemplateCategory.LIFESTYLE: "🌟",
            TemplateCategory.EDUCATION: "🎓",
            TemplateCategory.MARKETING: "📈",
            TemplateCategory.PERSONAL: "👤"
        }
        return icons.get(category, "📝")
    
    def increment_usage(self, template_id: str):
        """Increment usage count for a template"""
        template = self.get_template_by_id(template_id)
        if template:
            template.usage_count += 1
