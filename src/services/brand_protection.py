#!/usr/bin/env python3
"""
Brand Protection Service for ThreadStorm
Ensures brand independence and trademark compliance
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BrandProtectionService:
    """Brand protection and trademark compliance service"""
    
    def __init__(self):
        # Brand guidelines
        self.brand_name = "ThreadStorm"
        self.brand_owner = "Martek Labs LLC"
        self.brand_description = "AI-powered content formatting and publishing platform"
        
        # Trademark status
        self.trademark_status = {
            'threadstorm': {
                'status': 'pending',
                'application_date': '2024-01-01',
                'class': '9, 42',  # Software and services
                'jurisdiction': 'US'
            }
        }
        
        # Prohibited terms and phrases
        self.prohibited_terms = [
            'threads app',
            'threads by meta',
            'meta threads',
            'instagram threads',
            'facebook threads',
            'official threads',
            'threads official',
            'threads platform',
            'threads social media',
            'threads network'
        ]
        
        # Required disclaimers
        self.disclaimers = {
            'meta_affiliation': "ThreadStorm is not affiliated with, endorsed by, or sponsored by Meta Platforms, Inc., Instagram, or Facebook.",
            'threads_trademark': "Threads is a trademark of Meta Platforms, Inc.",
            'independent_service': "ThreadStorm is an independent third-party service for content formatting and publishing.",
            'user_responsibility': "Users are responsible for ensuring their content complies with Meta's Platform Terms and Community Guidelines."
        }
        
        # Brand usage guidelines
        self.brand_guidelines = {
            'logo_usage': {
                'minimum_size': '32px',
                'clear_space': 'equal to logo height',
                'background': 'dark or light with sufficient contrast',
                'prohibited': ['distortion', 'recoloring', 'modification']
            },
            'naming': {
                'preferred': 'ThreadStorm',
                'acceptable': ['ThreadStorm', 'threadstorm'],
                'prohibited': ['ThreadsStorm', 'Thread-Storm', 'Thread Storm']
            },
            'taglines': {
                'approved': [
                    'Transform your content into engaging threads',
                    'AI-powered thread formatting',
                    'Smart content optimization for social media',
                    'Professional thread creation made easy'
                ],
                'prohibited': [
                    'The official Threads formatter',
                    'Threads by ThreadStorm',
                    'Meta Threads formatter',
                    'Instagram Threads tool'
                ]
            }
        }
    
    def check_brand_compliance(self, content: str, context: str = "general") -> Dict:
        """Check content for brand compliance"""
        try:
            issues = []
            warnings = []
            recommendations = []
            
            # Check for prohibited terms
            prohibited_found = self._check_prohibited_terms(content)
            if prohibited_found:
                issues.extend(prohibited_found)
            
            # Check for trademark violations
            trademark_issues = self._check_trademark_violations(content)
            if trademark_issues:
                issues.extend(trademark_issues)
            
            # Check brand usage
            brand_issues = self._check_brand_usage(content)
            if brand_issues:
                warnings.extend(brand_issues)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(content, context)
            
            return {
                'compliant': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'score': self._calculate_compliance_score(issues, warnings)
            }
            
        except Exception as e:
            logger.error(f"Brand compliance check failed: {e}")
            return {
                'compliant': False,
                'issues': [f"Brand compliance check failed: {str(e)}"],
                'warnings': [],
                'recommendations': ['Review content manually for brand compliance'],
                'score': 0
            }
    
    def _check_prohibited_terms(self, content: str) -> List[str]:
        """Check for prohibited terms and phrases"""
        issues = []
        content_lower = content.lower()
        
        for term in self.prohibited_terms:
            if term in content_lower:
                issues.append(f"Prohibited term found: '{term}' - suggests affiliation with Meta")
        
        return issues
    
    def _check_trademark_violations(self, content: str) -> List[str]:
        """Check for potential trademark violations"""
        issues = []
        
        # Check for misuse of "Threads" trademark
        threads_patterns = [
            r'\bthreads\s+(?:app|platform|network|social)\b',
            r'\bofficial\s+threads\b',
            r'\bthreads\s+official\b',
            r'\bmeta\s+threads\b',
            r'\binstagram\s+threads\b'
        ]
        
        for pattern in threads_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(f"Potential trademark violation: '{matches[0]}' - avoid suggesting affiliation")
        
        return issues
    
    def _check_brand_usage(self, content: str) -> List[str]:
        """Check brand usage guidelines"""
        warnings = []
        
        # Check for incorrect brand name variations
        incorrect_variations = [
            'ThreadsStorm',
            'Thread-Storm', 
            'Thread Storm',
            'threadstorm',
            'THREADSTORM'
        ]
        
        for variation in incorrect_variations:
            if variation in content:
                warnings.append(f"Incorrect brand name variation: '{variation}' - use 'ThreadStorm'")
        
        # Check for prohibited taglines
        for tagline in self.brand_guidelines['taglines']['prohibited']:
            if tagline.lower() in content.lower():
                warnings.append(f"Prohibited tagline: '{tagline}' - suggests official affiliation")
        
        return warnings
    
    def _generate_recommendations(self, content: str, context: str) -> List[str]:
        """Generate brand compliance recommendations"""
        recommendations = []
        
        # Add appropriate disclaimers based on context
        if context == "marketing":
            recommendations.append("Include disclaimer: 'ThreadStorm is not affiliated with Meta Platforms, Inc.'")
        
        if context == "documentation":
            recommendations.append("Add trademark notice: 'Threads is a trademark of Meta Platforms, Inc.'")
        
        if context == "user_interface":
            recommendations.append("Use approved taglines only")
            recommendations.append("Maintain clear brand separation from Meta products")
        
        # General recommendations
        recommendations.extend([
            "Use 'ThreadStorm' consistently as the brand name",
            "Avoid suggesting official affiliation with Meta",
            "Include appropriate disclaimers where necessary",
            "Follow brand usage guidelines for logos and visual elements"
        ])
        
        return recommendations
    
    def _calculate_compliance_score(self, issues: List[str], warnings: List[str]) -> int:
        """Calculate brand compliance score (0-100)"""
        base_score = 100
        
        # Deduct points for issues (more severe)
        issue_penalty = len(issues) * 20
        warning_penalty = len(warnings) * 5
        
        score = max(0, base_score - issue_penalty - warning_penalty)
        return score
    
    def get_required_disclaimers(self, context: str = "general") -> List[str]:
        """Get required disclaimers for specific context"""
        disclaimers = []
        
        if context in ["marketing", "public"]:
            disclaimers.append(self.disclaimers['meta_affiliation'])
            disclaimers.append(self.disclaimers['independent_service'])
        
        if context in ["documentation", "legal"]:
            disclaimers.append(self.disclaimers['threads_trademark'])
            disclaimers.append(self.disclaimers['user_responsibility'])
        
        return disclaimers
    
    def validate_brand_assets(self, asset_type: str, asset_data: Dict) -> Dict:
        """Validate brand assets for compliance"""
        try:
            issues = []
            warnings = []
            
            if asset_type == "logo":
                issues.extend(self._validate_logo(asset_data))
            elif asset_type == "tagline":
                issues.extend(self._validate_tagline(asset_data))
            elif asset_type == "color_scheme":
                issues.extend(self._validate_color_scheme(asset_data))
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"Brand asset validation failed: {e}")
            return {
                'valid': False,
                'issues': [f"Validation failed: {str(e)}"],
                'warnings': []
            }
    
    def _validate_logo(self, logo_data: Dict) -> List[str]:
        """Validate logo usage"""
        issues = []
        
        # Check minimum size
        if 'size' in logo_data:
            size = logo_data['size']
            if size < 32:
                issues.append(f"Logo size {size}px is below minimum requirement of 32px")
        
        # Check background contrast
        if 'background' in logo_data:
            background = logo_data['background']
            if background not in ['dark', 'light']:
                issues.append(f"Logo background should be 'dark' or 'light' for proper contrast")
        
        return issues
    
    def _validate_tagline(self, tagline_data: Dict) -> List[str]:
        """Validate tagline"""
        issues = []
        tagline = tagline_data.get('text', '')
        
        # Check if tagline is approved
        if tagline not in self.brand_guidelines['taglines']['approved']:
            issues.append(f"Tagline '{tagline}' is not in approved list")
        
        # Check for prohibited terms
        for prohibited in self.brand_guidelines['taglines']['prohibited']:
            if prohibited.lower() in tagline.lower():
                issues.append(f"Tagline contains prohibited term: '{prohibited}'")
        
        return issues
    
    def _validate_color_scheme(self, color_data: Dict) -> List[str]:
        """Validate color scheme"""
        issues = []
        
        # Check for Meta brand colors (avoid confusion)
        meta_colors = ['#1877F2', '#42A5F5', '#1DA1F2']  # Facebook blue, etc.
        
        for color in color_data.get('colors', []):
            if color.upper() in meta_colors:
                issues.append(f"Color {color} is too similar to Meta brand colors")
        
        return issues
    
    def generate_brand_guidelines(self) -> Dict:
        """Generate comprehensive brand guidelines"""
        return {
            'brand_identity': {
                'name': self.brand_name,
                'owner': self.brand_owner,
                'description': self.brand_description,
                'trademark_status': self.trademark_status
            },
            'usage_guidelines': self.brand_guidelines,
            'disclaimers': self.disclaimers,
            'prohibited_terms': self.prohibited_terms,
            'compliance_checklist': [
                "Use 'ThreadStorm' consistently as brand name",
                "Avoid suggesting affiliation with Meta",
                "Include appropriate disclaimers",
                "Follow logo usage guidelines",
                "Use approved taglines only",
                "Maintain brand independence",
                "Respect Meta's trademarks",
                "Ensure clear user responsibility disclaimers"
            ]
        }
    
    def check_trademark_availability(self, term: str, jurisdiction: str = "US") -> Dict:
        """Check trademark availability (placeholder for real service)"""
        # This would integrate with a real trademark search service
        # For now, return placeholder response
        
        return {
            'term': term,
            'jurisdiction': jurisdiction,
            'available': True,  # Placeholder
            'similar_marks': [],  # Placeholder
            'recommendation': 'Consult with trademark attorney for comprehensive search',
            'search_date': datetime.now().isoformat()
        }


# Global brand protection service instance
brand_protection = BrandProtectionService()


# Brand compliance middleware
async def brand_compliance_middleware(request, call_next):
    """Middleware to check brand compliance in requests"""
    try:
        # Check request content for brand compliance
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                try:
                    import json
                    data = json.loads(body)
                    
                    # Check content fields for brand compliance
                    for field in ['content', 'description', 'title', 'message']:
                        if field in data and isinstance(data[field], str):
                            compliance = brand_protection.check_brand_compliance(
                                data[field], 
                                context="user_content"
                            )
                            
                            if not compliance['compliant']:
                                logger.warning(f"Brand compliance issues in {field}: {compliance['issues']}")
                                
                except json.JSONDecodeError:
                    pass  # Not JSON content
        
        # Process request
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Brand compliance middleware error: {e}")
        return await call_next(request)
