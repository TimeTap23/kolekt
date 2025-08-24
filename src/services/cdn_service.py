#!/usr/bin/env python3
"""
CDN Service for ThreadStorm
Handles static asset optimization and CDN integration
"""

import logging
import hashlib
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import aiofiles
from src.core.config import settings

logger = logging.getLogger(__name__)


class CDNService:
    """CDN service for static asset optimization"""
    
    def __init__(self):
        self.enabled = True
        self.cdn_url = settings.CDN_URL if hasattr(settings, 'CDN_URL') else None
        self.static_dir = Path("web/static")
        self.cache_dir = Path("web/static/cache")
        self.asset_manifest: Dict[str, str] = {}
        
        # Asset optimization settings
        self.minify_css = True
        self.minify_js = True
        self.compress_images = True
        self.version_assets = True
        
        # Cache settings
        self.cache_ttl = 86400  # 24 hours
        self.max_cache_size = 100 * 1024 * 1024  # 100MB
        
        # Initialize cache directory
        self.cache_dir.mkdir(exist_ok=True)
    
    async def optimize_static_assets(self):
        """Optimize static assets for production"""
        try:
            logger.info("🔄 Optimizing static assets...")
            
            # Optimize CSS files
            await self._optimize_css_files()
            
            # Optimize JavaScript files
            await self._optimize_js_files()
            
            # Optimize images
            await self._optimize_images()
            
            # Generate asset manifest
            await self._generate_asset_manifest()
            
            logger.info("✅ Static assets optimized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error optimizing static assets: {e}")
    
    async def _optimize_css_files(self):
        """Optimize CSS files"""
        css_files = list(self.static_dir.rglob("*.css"))
        
        for css_file in css_files:
            try:
                # Read original CSS
                async with aiofiles.open(css_file, 'r') as f:
                    content = await f.read()
                
                # Basic CSS minification (remove comments, whitespace)
                optimized = self._minify_css(content)
                
                # Create versioned filename
                versioned_name = self._create_versioned_filename(css_file.name, optimized)
                versioned_path = css_file.parent / versioned_name
                
                # Write optimized CSS
                async with aiofiles.open(versioned_path, 'w') as f:
                    await f.write(optimized)
                
                # Update manifest
                self.asset_manifest[css_file.name] = versioned_name
                
                logger.debug(f"Optimized CSS: {css_file.name} -> {versioned_name}")
                
            except Exception as e:
                logger.error(f"Error optimizing CSS file {css_file}: {e}")
    
    async def _optimize_js_files(self):
        """Optimize JavaScript files"""
        js_files = list(self.static_dir.rglob("*.js"))
        
        for js_file in js_files:
            try:
                # Read original JS
                async with aiofiles.open(js_file, 'r') as f:
                    content = await f.read()
                
                # Basic JS minification (remove comments, whitespace)
                optimized = self._minify_js(content)
                
                # Create versioned filename
                versioned_name = self._create_versioned_filename(js_file.name, optimized)
                versioned_path = js_file.parent / versioned_name
                
                # Write optimized JS
                async with aiofiles.open(versioned_path, 'w') as f:
                    await f.write(optimized)
                
                # Update manifest
                self.asset_manifest[js_file.name] = versioned_name
                
                logger.debug(f"Optimized JS: {js_file.name} -> {versioned_name}")
                
            except Exception as e:
                logger.error(f"Error optimizing JS file {js_file}: {e}")
    
    async def _optimize_images(self):
        """Optimize image files"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(self.static_dir.rglob(f"*{ext}"))
        
        for image_file in image_files:
            try:
                # For now, just copy images (real optimization would use Pillow)
                # In production, you'd want to compress and convert to WebP
                versioned_name = self._create_versioned_filename(image_file.name, image_file.read_bytes())
                versioned_path = image_file.parent / versioned_name
                
                # Copy file
                import shutil
                shutil.copy2(image_file, versioned_path)
                
                # Update manifest
                self.asset_manifest[image_file.name] = versioned_name
                
                logger.debug(f"Optimized image: {image_file.name} -> {versioned_name}")
                
            except Exception as e:
                logger.error(f"Error optimizing image file {image_file}: {e}")
    
    def _minify_css(self, content: str) -> str:
        """Basic CSS minification"""
        import re
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _minify_js(self, content: str) -> str:
        """Basic JavaScript minification"""
        import re
        
        # Remove single-line comments (but not URLs)
        content = re.sub(r'(?<!:)\/\/.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _create_versioned_filename(self, filename: str, content: bytes) -> str:
        """Create a versioned filename based on content hash"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Create hash
        hash_obj = hashlib.md5(content)
        hash_hex = hash_obj.hexdigest()[:8]
        
        # Split filename and extension
        name, ext = os.path.splitext(filename)
        
        return f"{name}.{hash_hex}{ext}"
    
    async def _generate_asset_manifest(self):
        """Generate asset manifest file"""
        manifest_path = self.static_dir / "asset-manifest.json"
        
        manifest_data = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "assets": self.asset_manifest,
            "cdn_url": self.cdn_url
        }
        
        import json
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest_data, indent=2))
        
        logger.info(f"Generated asset manifest: {manifest_path}")
    
    def get_asset_url(self, filename: str) -> str:
        """Get the CDN URL for an asset"""
        if not self.enabled or not self.cdn_url:
            return f"/static/{filename}"
        
        # Get versioned filename from manifest
        versioned_name = self.asset_manifest.get(filename, filename)
        
        return f"{self.cdn_url.rstrip('/')}/{versioned_name}"
    
    async def preload_critical_assets(self) -> List[str]:
        """Get list of critical assets to preload"""
        critical_assets = [
            "css/style.css",
            "js/main.js",
            "images/Kolekt_icon.png"
        ]
        
        preload_urls = []
        for asset in critical_assets:
            url = self.get_asset_url(asset)
            preload_urls.append(url)
        
        return preload_urls
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get CDN cache statistics"""
        try:
            cache_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
            
            return {
                "enabled": self.enabled,
                "cdn_url": self.cdn_url,
                "cache_size_bytes": cache_size,
                "cache_size_mb": cache_size / (1024 * 1024),
                "asset_count": len(self.asset_manifest),
                "optimization_enabled": {
                    "css_minification": self.minify_css,
                    "js_minification": self.minify_js,
                    "image_compression": self.compress_images,
                    "asset_versioning": self.version_assets
                }
            }
        except Exception as e:
            logger.error(f"Error getting CDN cache stats: {e}")
            return {"enabled": False, "error": str(e)}
    
    async def clear_cache(self):
        """Clear CDN cache"""
        try:
            # Remove cached files
            for cache_file in self.cache_dir.rglob('*'):
                if cache_file.is_file():
                    cache_file.unlink()
            
            # Clear asset manifest
            self.asset_manifest.clear()
            
            logger.info("✅ CDN cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing CDN cache: {e}")
    
    async def health_check(self) -> bool:
        """Health check for CDN service"""
        try:
            # Check if static directory exists
            if not self.static_dir.exists():
                return False
            
            # Check if we can read asset manifest
            manifest_path = self.static_dir / "asset-manifest.json"
            if manifest_path.exists():
                async with aiofiles.open(manifest_path, 'r') as f:
                    await f.read()
            
            return True
            
        except Exception as e:
            logger.error(f"CDN health check failed: {e}")
            return False


# Global CDN service instance
cdn_service = CDNService()
