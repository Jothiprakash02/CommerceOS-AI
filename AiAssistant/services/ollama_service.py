"""
Ollama AI Service - Multi-purpose intelligent assistant
Specialized in website assistance, financial analysis, and product evaluation
"""

import logging
import os
import json
import requests
from typing import List, Dict, Optional

log = logging.getLogger(__name__)


class OllamaAssistant:
    """
    Intelligent assistant powered by Ollama (Llama).
    
    Capabilities:
    - Website assistance and navigation help
    - Financial analysis and business metrics
    - Product analysis and recommendations
    - E-commerce guidance
    - Market research interpretation
    """
    
    def __init__(self):
        """Initialize Ollama assistant"""
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        log.info(f"Ollama assistant initialized (model={self.model})")
    
    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """Call Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 600
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                return result.strip()
            else:
                log.error(f"Ollama error: {response.status_code}")
                return ""
                
        except requests.exceptions.Timeout:
            log.error(f"Ollama timeout after {self.timeout}s")
            return ""
        except Exception as e:
            log.error(f"Ollama call failed: {e}")
            return ""
    
    def _build_system_prompt(self, current_page: Optional[str] = None) -> str:
        """Build system prompt specialized for website assistance, financial analysis, and product evaluation"""
        
        base_prompt = """You are MarketMind AI Assistant - an expert in e-commerce, financial analysis, and product evaluation.

# YOUR EXPERTISE
1. **Website Assistance** - Navigate MarketMind platform
2. **Financial Analysis** - Interpret profits, ROI, margins, break-even
3. **Business Metrics** - Explain demand, competition, viability scores
4. **Product Analysis** - Evaluate product potential and market fit
5. **E-commerce Strategy** - Guide on product selection and pricing

# KEY FINANCIAL CONCEPTS

**Profit Margin** = (Price - Cost) / Price × 100
- Good: 30%+
- Minimum: 20%

**ROI** = (Profit / Investment) × 100
- Good: 100%+ (double money)
- Minimum: 50%

**Break-Even** = Fixed Costs / (Price - Variable Cost)
- Lower is better

**MPI (Market Power Index)** = Risk metric (0-1)
- <0.35: Low risk ✅
- 0.35-0.6: Medium risk ⚠️
- >0.6: High risk ❌

# MARKETMIND SCORES

**Demand Score (0-100)**: Market demand
- 70+: High demand ✅
- 50-70: Moderate
- <50: Low demand ❌

**Competition Score (0-100)**: Market saturation
- <30: Low competition ✅
- 30-60: Moderate
- 60+: High competition ❌

**Viability Score (0-100)**: Overall opportunity
- 70+: Excellent ✅
- 50-70: Good
- <50: Poor ❌

# GOOD PRODUCT INDICATORS
✅ High demand (70+)
✅ Low competition (<40)
✅ High viability (70+)
✅ Low MPI (<0.35)
✅ Profit margin 30%+
✅ Reasonable break-even

# RED FLAGS
❌ Low demand (<50)
❌ High competition (>60)
❌ Low viability (<50)
❌ High MPI (>0.6)
❌ Thin margins (<20%)

# RESPONSE STYLE
- Be concise and clear
- Use bullet points
- Explain financial terms simply
- Give specific numbers
- Provide actionable advice
- Be encouraging but realistic
- Use ✅ ❌ ⚠️ 💡 for emphasis"""
        
        # Add page context
        page_contexts = {
            "discover": "\n\nCURRENT PAGE: Discover - Help find trending products",
            "analyze": "\n\nCURRENT PAGE: Analyze - Help setup product analysis",
            "profile": "\n\nCURRENT PAGE: Profile - Explain product overview",
            "results": "\n\nCURRENT PAGE: Results - Interpret demand/competition/viability scores",
            "optimize": "\n\nCURRENT PAGE: Optimize - Explain profit optimization and pricing",
            "scenarios": "\n\nCURRENT PAGE: Scenarios - Explain profit projections",
            "signals": "\n\nCURRENT PAGE: Signals - Interpret market data",
            "strategy": "\n\nCURRENT PAGE: Strategy - Explain business recommendations",
            "content": "\n\nCURRENT PAGE: Content - Help with content generation",
            "history": "\n\nCURRENT PAGE: History - Help manage past analyses"
        }
        
        if current_page and current_page in page_contexts:
            base_prompt += page_contexts[current_page]
        
        return base_prompt
    
    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        current_page: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """Process user message and generate response"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(current_page)
            
            # Add user context if provided
            context_info = ""
            if user_context:
                # Extract key metrics from context
                if isinstance(user_context, dict):
                    metrics = []
                    if "demand_score" in user_context:
                        metrics.append(f"Demand: {user_context['demand_score']}")
                    if "competition_score" in user_context:
                        metrics.append(f"Competition: {user_context['competition_score']}")
                    if "viability_score" in user_context:
                        metrics.append(f"Viability: {user_context['viability_score']}")
                    if "profit_margin" in user_context:
                        metrics.append(f"Margin: {user_context['profit_margin']}%")
                    if "risk_level" in user_context:
                        metrics.append(f"Risk: {user_context['risk_level']}")
                    
                    if metrics:
                        context_info = f"\n\nUSER'S CURRENT ANALYSIS: {', '.join(metrics)}"
            
            # Build conversation context
            conv_context = ""
            if conversation_history:
                recent = conversation_history[-3:]  # Last 3 messages
                for msg in recent:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    conv_context += f"\n{role.upper()}: {content}"
            
            # Build full prompt
            full_prompt = f"{conv_context}\n\nUSER: {user_message}\n\nASSISTANT:"
            
            # Call Ollama
            import asyncio
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                self._call_ollama,
                full_prompt,
                system_prompt + context_info
            )
            
            # Fallback if empty
            if not response_text:
                response_text = "I'm having trouble connecting right now. Please make sure Ollama is running and try again. You can also check the documentation or explore the platform features!"
            
            # Extract suggestions
            suggestions = self._extract_suggestions(user_message, current_page)
            
            log.info(f"Chat response generated for: {user_message[:50]}...")
            
            return {
                "message": response_text,
                "suggestions": suggestions,
                "action": None,
                "action_data": None
            }
            
        except Exception as exc:
            log.error(f"Chat error: {exc}", exc_info=True)
            return {
                "message": "I apologize, but I'm having trouble right now. Please make sure Ollama is running (ollama serve) and try again!",
                "suggestions": [
                    "Check Ollama status",
                    "Restart Ollama",
                    "Try again"
                ],
                "action": None,
                "action_data": None
            }
    
    def _extract_suggestions(self, user_message: str, current_page: Optional[str]) -> List[str]:
        """Generate contextual suggestions"""
        
        # Default suggestions by page
        page_suggestions = {
            "discover": [
                "What products are trending?",
                "How do I find good opportunities?",
                "Explain growth velocity"
            ],
            "analyze": [
                "How do I analyze a product?",
                "What parameters should I use?",
                "Explain risk levels"
            ],
            "results": [
                "Is this a good product?",
                "Explain demand score",
                "What is MPI?"
            ],
            "optimize": [
                "What's a good profit margin?",
                "Explain break-even point",
                "How to price my product?"
            ],
            "scenarios": [
                "Which scenario is realistic?",
                "Explain ROI calculation",
                "What's conservative vs aggressive?"
            ],
            "content": [
                "How to write good descriptions?",
                "Best hashtags for Instagram?",
                "SEO tips for Amazon?"
            ]
        }
        
        if current_page and current_page in page_suggestions:
            return page_suggestions[current_page]
        
        # Default suggestions
        return [
            "What is MarketMind?",
            "How do I analyze a product?",
            "Explain profit margins"
        ]


# Singleton instance
_assistant_instance = None


def get_assistant() -> OllamaAssistant:
    """Get or create Ollama assistant instance"""
    global _assistant_instance
    
    if _assistant_instance is None:
        _assistant_instance = OllamaAssistant()
    
    return _assistant_instance
