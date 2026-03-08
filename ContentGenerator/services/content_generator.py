"""
Content Generation Service using Ollama LLM
Generates SEO-optimized content, hashtags, and platform-specific posts
"""

import logging
import os
import json
import time
import requests
from typing import List, Dict, Optional, Tuple

log = logging.getLogger(__name__)


class ContentGeneratorService:
    """
    Generates SEO-optimized content for multiple platforms using Ollama
    """
    
    # Platform-specific guidelines
    PLATFORM_SPECS = {
        "instagram": {
            "max_chars": 2200,
            "hashtag_count": (20, 30),
            "style": "visual, engaging, emoji-friendly",
            "cta_style": "subtle, story-driven"
        },
        "twitter": {
            "max_chars": 280,
            "hashtag_count": (1, 3),
            "style": "concise, witty, trending",
            "cta_style": "direct, action-oriented"
        },
        "facebook": {
            "max_chars": 63206,
            "hashtag_count": (3, 5),
            "style": "conversational, community-focused",
            "cta_style": "friendly, engaging"
        },
        "linkedin": {
            "max_chars": 3000,
            "hashtag_count": (3, 5),
            "style": "professional, value-driven",
            "cta_style": "professional, benefit-focused"
        },
        "tiktok": {
            "max_chars": 2200,
            "hashtag_count": (5, 8),
            "style": "trendy, fun, viral-worthy",
            "cta_style": "exciting, FOMO-driven"
        },
        "pinterest": {
            "max_chars": 500,
            "hashtag_count": (5, 10),
            "style": "inspirational, descriptive",
            "cta_style": "aspirational, save-worthy"
        },
        "amazon": {
            "title_max": 200,
            "bullet_points": 5,
            "description_max": 2000,
            "style": "informative, keyword-rich, benefit-focused"
        },
        "etsy": {
            "title_max": 140,
            "tags": 13,
            "description_max": 5000,
            "style": "artisanal, story-driven, unique"
        },
        "shopify": {
            "title_max": 255,
            "description_max": 65535,
            "style": "brand-focused, conversion-optimized"
        }
    }
    
    def __init__(self):
        """Initialize content generator"""
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        log.info(f"ContentGenerator initialized (model={self.model})")
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Call Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # Creative but controlled
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            log.info(f"Calling Ollama with prompt length: {len(prompt)}")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            log.info(f"Ollama response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                log.info(f"Ollama response length: {len(result)}")
                if not result:
                    log.warning("Ollama returned empty response")
                return result
            else:
                log.error(f"Ollama error: {response.status_code} - {response.text}")
                return ""
                
        except requests.exceptions.Timeout:
            log.error(f"Ollama timeout after {self.timeout}s")
            return ""
        except Exception as e:
            log.error(f"Ollama call failed: {e}", exc_info=True)
            return ""
    
    def generate_content(
        self,
        product_name: str,
        product_description: Optional[str] = None,
        product_category: Optional[str] = None,
        target_audience: Optional[str] = None,
        key_features: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        platforms: List[str] = None,
        tone: str = "professional",
        length: str = "medium",
        variations: int = 3,
        include_emojis: bool = True,
        include_cta: bool = True,
        focus_seo: bool = True
    ) -> Dict:
        """
        Generate comprehensive content for multiple platforms
        """
        start_time = time.time()
        
        if platforms is None:
            platforms = ["instagram", "twitter", "facebook"]
        
        # Build context
        context = self._build_context(
            product_name, product_description, product_category,
            target_audience, key_features, keywords
        )
        
        # Generate universal content first
        universal_desc = self._generate_universal_description(context, tone, length)
        universal_hashtags = self._generate_universal_hashtags(context, keywords)
        seo_keywords = self._generate_seo_keywords(context, keywords)
        
        # Generate platform-specific content
        all_variations = []
        for var_num in range(1, variations + 1):
            platform_contents = []
            
            for platform in platforms:
                content = self._generate_platform_content(
                    platform=platform,
                    context=context,
                    tone=tone,
                    length=length,
                    include_emojis=include_emojis,
                    include_cta=include_cta,
                    variation_num=var_num
                )
                platform_contents.append(content)
            
            all_variations.append({
                "variation_number": var_num,
                "platforms": platform_contents
            })
        
        generation_time = time.time() - start_time
        
        return {
            "product_name": product_name,
            "generated_for": platforms,
            "tone": tone,
            "length": length,
            "variations": all_variations,
            "universal_description": universal_desc,
            "universal_hashtags": universal_hashtags,
            "seo_keywords": seo_keywords,
            "generation_time": round(generation_time, 2),
            "model_used": self.model,
            "success": True
        }
    
    def _build_context(
        self,
        product_name: str,
        product_description: Optional[str],
        product_category: Optional[str],
        target_audience: Optional[str],
        key_features: Optional[List[str]],
        keywords: Optional[List[str]]
    ) -> str:
        """Build context string for LLM"""
        parts = [f"Product: {product_name}"]
        
        if product_description:
            parts.append(f"Description: {product_description}")
        if product_category:
            parts.append(f"Category: {product_category}")
        if target_audience:
            parts.append(f"Target Audience: {target_audience}")
        if key_features:
            parts.append(f"Key Features: {', '.join(key_features)}")
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords)}")
        
        return "\n".join(parts)
    
    def _generate_universal_description(
        self,
        context: str,
        tone: str,
        length: str
    ) -> str:
        """Generate universal product description"""
        
        length_guide = {
            "short": "2-3 sentences",
            "medium": "4-6 sentences",
            "long": "8-10 sentences"
        }
        
        system_prompt = f"""You are an expert copywriter specializing in product descriptions.
Create compelling, SEO-optimized product descriptions that convert.
Tone: {tone}
Length: {length_guide.get(length, '4-6 sentences')}"""
        
        prompt = f"""{context}

Write a compelling product description that:
1. Highlights key benefits
2. Uses persuasive language
3. Includes relevant keywords naturally
4. Appeals to the target audience
5. Has a clear value proposition

Description:"""
        
        result = self._call_ollama(prompt, system_prompt).strip()
        
        # Fallback if empty
        if not result:
            log.warning("Empty description from Ollama, using fallback")
            product_name = context.split('\n')[0].replace('Product: ', '')
            result = f"{product_name} is a high-quality product designed to meet your needs. With excellent features and reliable performance, it offers great value for money. Perfect for anyone looking for a dependable solution."
        
        return result
    
    def _generate_universal_hashtags(
        self,
        context: str,
        keywords: Optional[List[str]]
    ) -> List[str]:
        """Generate universal hashtags"""
        
        system_prompt = """You are a social media expert specializing in hashtag strategy.
Generate relevant, trending, and niche-specific hashtags."""
        
        keyword_hint = f"\nFocus keywords: {', '.join(keywords)}" if keywords else ""
        
        prompt = f"""{context}{keyword_hint}

Generate 15 relevant hashtags that:
1. Mix popular and niche tags
2. Are relevant to the product
3. Help with discoverability
4. Follow best practices

Format: Return ONLY hashtags, one per line, with # symbol.
Example:
#ProductName
#Category
#Benefit

Hashtags:"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse hashtags
        hashtags = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                hashtag = line.split()[0]  # Get first word if multiple
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        # Fallback if empty
        if not hashtags:
            log.warning("Empty hashtags from Ollama, using fallback")
            product_name = context.split('\n')[0].replace('Product: ', '').replace(' ', '')
            hashtags = [
                f"#{product_name}",
                "#Product",
                "#Shopping",
                "#OnlineShopping",
                "#BestDeals",
                "#Quality",
                "#MustHave",
                "#NewArrival",
                "#TrendingNow",
                "#ShopNow"
            ]
        
        return hashtags[:15]
    
    def _generate_seo_keywords(
        self,
        context: str,
        provided_keywords: Optional[List[str]]
    ) -> List[str]:
        """Generate SEO keywords"""
        
        system_prompt = """You are an SEO expert. Generate high-value keywords for search optimization."""
        
        prompt = f"""{context}

Generate 10 SEO keywords that:
1. Have high search volume potential
2. Are relevant to the product
3. Include long-tail variations
4. Help with organic discovery

Format: Return ONLY keywords, one per line, no numbering.

Keywords:"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse keywords
        keywords = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 2:
                keywords.append(line)
        
        # Add provided keywords
        if provided_keywords:
            keywords.extend(provided_keywords)
        
        # Remove duplicates, keep order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)
        
        return unique_keywords[:15]
    
    def _generate_platform_content(
        self,
        platform: str,
        context: str,
        tone: str,
        length: str,
        include_emojis: bool,
        include_cta: bool,
        variation_num: int
    ) -> Dict:
        """Generate content for specific platform"""
        
        specs = self.PLATFORM_SPECS.get(platform, {})
        
        if platform in ["instagram", "twitter", "facebook", "linkedin", "tiktok", "pinterest"]:
            return self._generate_social_content(
                platform, context, tone, specs, include_emojis, include_cta, variation_num
            )
        elif platform in ["amazon", "etsy", "shopify"]:
            return self._generate_ecommerce_content(
                platform, context, tone, specs, variation_num
            )
        else:
            return {"platform": platform, "error": "Unsupported platform"}
    
    def _generate_social_content(
        self,
        platform: str,
        context: str,
        tone: str,
        specs: Dict,
        include_emojis: bool,
        include_cta: bool,
        variation_num: int
    ) -> Dict:
        """Generate social media post"""
        
        system_prompt = f"""You are a social media expert for {platform.upper()}.
Create engaging posts that drive engagement and conversions.
Platform style: {specs.get('style', 'engaging')}
Tone: {tone}
Max characters: {specs.get('max_chars', 2000)}"""
        
        emoji_instruction = "Use relevant emojis throughout." if include_emojis else "No emojis."
        cta_instruction = f"Include a {specs.get('cta_style', 'clear')} call-to-action." if include_cta else ""
        
        prompt = f"""{context}

Create a {platform} post (Variation #{variation_num}) that:
1. Captures attention immediately
2. Highlights key benefits
3. Matches {platform} best practices
4. {emoji_instruction}
5. {cta_instruction}
6. Stays under {specs.get('max_chars')} characters

Post:"""
        
        post = self._call_ollama(prompt, system_prompt).strip()
        
        # Fallback if empty
        if not post:
            log.warning(f"Empty post from Ollama for {platform}, using fallback")
            product_name = context.split('\n')[0].replace('Product: ', '')
            emoji = "✨ " if include_emojis else ""
            cta = " Check it out today!" if include_cta else ""
            post = f"{emoji}{product_name} - Quality you can trust.{cta}"
        
        # Generate hashtags for this platform
        hashtag_count = specs.get('hashtag_count', (5, 10))
        hashtags = self._generate_platform_hashtags(
            platform, context, hashtag_count[0], hashtag_count[1]
        )
        
        return {
            "platform": platform,
            "post": post,
            "hashtags": hashtags,
            "character_count": len(post)
        }
    
    def _generate_platform_hashtags(
        self,
        platform: str,
        context: str,
        min_count: int,
        max_count: int
    ) -> List[str]:
        """Generate platform-specific hashtags"""
        
        system_prompt = f"""Generate hashtags optimized for {platform.upper()}.
Follow {platform} hashtag best practices."""
        
        prompt = f"""{context}

Generate {max_count} hashtags for {platform} that:
1. Are trending and relevant
2. Mix popular and niche tags
3. Follow {platform} conventions
4. Help with discoverability

Format: Return ONLY hashtags with # symbol, one per line.

Hashtags:"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse hashtags
        hashtags = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                hashtag = line.split()[0]
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        return hashtags[:max_count]
    
    def _generate_ecommerce_content(
        self,
        platform: str,
        context: str,
        tone: str,
        specs: Dict,
        variation_num: int
    ) -> Dict:
        """Generate e-commerce content"""
        
        # Generate title
        title = self._generate_ecommerce_title(platform, context, specs, variation_num)
        
        # Generate description
        description = self._generate_ecommerce_description(platform, context, tone, specs)
        
        # Generate bullet points
        bullet_points = self._generate_bullet_points(context, specs.get('bullet_points', 5))
        
        # Generate meta description
        meta_description = self._generate_meta_description(context)
        
        # Generate SEO keywords
        seo_keywords = self._extract_keywords_from_context(context)
        
        result = {
            "platform": platform,
            "title": title,
            "description": description,
            "bullet_points": bullet_points,
            "meta_description": meta_description,
            "seo_keywords": seo_keywords
        }
        
        # Platform-specific additions
        if platform == "etsy":
            result["tags"] = self._generate_etsy_tags(context)
        
        return result
    
    def _generate_ecommerce_title(
        self,
        platform: str,
        context: str,
        specs: Dict,
        variation_num: int
    ) -> str:
        """Generate product title"""
        
        max_length = specs.get('title_max', 200)
        
        system_prompt = f"""Create SEO-optimized product titles for {platform.upper()}.
Max length: {max_length} characters
Style: {specs.get('style', 'informative')}"""
        
        prompt = f"""{context}

Create a product title (Variation #{variation_num}) that:
1. Includes key features
2. Uses relevant keywords
3. Is clear and descriptive
4. Stays under {max_length} characters
5. Follows {platform} best practices

Title:"""
        
        title = self._call_ollama(prompt, system_prompt).strip()
        return title[:max_length]
    
    def _generate_ecommerce_description(
        self,
        platform: str,
        context: str,
        tone: str,
        specs: Dict
    ) -> str:
        """Generate product description"""
        
        max_length = specs.get('description_max', 2000)
        
        system_prompt = f"""Create compelling product descriptions for {platform.upper()}.
Tone: {tone}
Style: {specs.get('style', 'informative')}"""
        
        prompt = f"""{context}

Write a detailed product description that:
1. Highlights benefits and features
2. Uses persuasive language
3. Includes relevant keywords naturally
4. Addresses customer pain points
5. Builds trust and credibility

Description:"""
        
        description = self._call_ollama(prompt, system_prompt).strip()
        return description[:max_length]
    
    def _generate_bullet_points(self, context: str, count: int) -> List[str]:
        """Generate bullet points"""
        
        system_prompt = """Create concise, benefit-focused bullet points for product listings."""
        
        prompt = f"""{context}

Generate {count} bullet points that:
1. Start with a benefit or feature
2. Are concise and scannable
3. Use action words
4. Highlight unique selling points

Format: Return ONLY bullet points, one per line, starting with •

Bullet points:"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse bullet points
        bullets = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                bullet = line.lstrip('•-* ').strip()
                if bullet:
                    bullets.append(bullet)
        
        return bullets[:count]
    
    def _generate_meta_description(self, context: str) -> str:
        """Generate meta description for SEO"""
        
        system_prompt = """Create SEO-optimized meta descriptions (150-160 characters)."""
        
        prompt = f"""{context}

Write a meta description that:
1. Summarizes the product
2. Includes primary keyword
3. Has a call-to-action
4. Is 150-160 characters

Meta description:"""
        
        meta = self._call_ollama(prompt, system_prompt).strip()
        return meta[:160]
    
    def _generate_etsy_tags(self, context: str) -> List[str]:
        """Generate Etsy tags"""
        
        system_prompt = """Generate Etsy tags (13 max, 20 characters each)."""
        
        prompt = f"""{context}

Generate 13 Etsy tags that:
1. Are specific and relevant
2. Include long-tail keywords
3. Help with search discovery
4. Are under 20 characters each

Format: Return ONLY tags, one per line, no # symbol.

Tags:"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse tags
        tags = []
        for line in response.split('\n'):
            line = line.strip().replace('#', '')
            if line and len(line) <= 20:
                tags.append(line)
        
        return tags[:13]
    
    def _extract_keywords_from_context(self, context: str) -> List[str]:
        """Extract keywords from context"""
        # Simple extraction - could be enhanced
        words = context.lower().split()
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]
        return list(set(keywords))[:10]
    
    def quick_generate(
        self,
        product_name: str,
        platform: str = "instagram",
        tone: str = "casual"
    ) -> Dict:
        """Quick generation with minimal input"""
        
        return self.generate_content(
            product_name=product_name,
            platforms=[platform],
            tone=tone,
            length="medium",
            variations=1,
            include_emojis=True,
            include_cta=True
        )
