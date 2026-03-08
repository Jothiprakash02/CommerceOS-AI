"""
Gemini AI Service - Multi-purpose intelligent assistant
"""

import logging
import os
import json
from typing import List, Dict, Optional, Tuple
from google import genai
from google.genai import types

log = logging.getLogger(__name__)


class GeminiAssistant:
    """
    Intelligent assistant powered by Google Gemini.
    
    Capabilities:
    - Answer questions about MarketMind features
    - Explain e-commerce terminology
    - Guide users through workflows
    - Provide product analysis insights
    - Suggest next steps
    - Context-aware responses based on current page
    """
    
    def __init__(self, api_key: str):
        """Initialize Gemini with API key"""
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.client = genai.Client(api_key=api_key)
        # Use gemini-1.5-flash for better free tier quota
        self.model_name = "models/gemini-1.5-flash"
        log.info("Gemini assistant initialized successfully (model=%s)", self.model_name)
    
    def _build_system_prompt(self, current_page: Optional[str] = None) -> str:
        """
        Build comprehensive system prompt for the assistant.
        This is the core of the assistant's intelligence.
        """
        
        base_prompt = """You are MarketMind AI Assistant, an intelligent helper for the MarketMind platform - an AI-powered commerce intelligence platform for beginner digital sellers.

# YOUR ROLE
You help users:
1. Understand MarketMind features and capabilities
2. Learn e-commerce terminology and concepts
3. Navigate the platform effectively
4. Interpret analysis results
5. Make informed business decisions
6. Troubleshoot issues

# PLATFORM OVERVIEW
MarketMind has these main features:

**🔍 Discover (TrendScout)**
- Scans Google Trends, Amazon Movers & Shakers, Reddit
- Finds emerging product opportunities BEFORE users have an idea
- Shows trending products, categories, and seasonal spikes

**⚡ Analyze**
- Full product analysis pipeline
- Analyzes demand, competition, viability
- Provides profit forecasts and risk assessment
- Generates AI strategy recommendations

**📊 Market Results**
- Shows demand score, competition score, viability score
- Displays market signals (search volume, seller count, reviews)
- Provides pricing recommendations

**🎯 Optimize**
- Profit optimization engine
- Calculates optimal pricing
- Shows break-even analysis
- Provides margin recommendations

**📈 Scenarios**
- Conservative, Expected, Aggressive profit scenarios
- Monthly sales and revenue projections
- ROI calculations

**📡 Signals**
- Raw market data and signals
- Trend analysis, seasonality, competition metrics
- Keyword research data

**♟ Strategy**
- AI-generated business strategy (powered by Llama3)
- Risk assessment and recommendations
- Market entry advice

**🕐 History**
- Past analyses saved for reference
- Star/favorite important analyses
- Export and re-analyze features

# KEY TERMINOLOGY YOU SHOULD EXPLAIN

**E-commerce Terms:**
- BSR (Best Seller Rank): Amazon's ranking system
- CPC (Cost Per Click): Advertising cost
- ROI (Return on Investment): Profit percentage
- Margin: Profit after costs
- Platform Fee: Marketplace commission (e.g., 15% on Amazon)
- Supplier Cost: Product sourcing cost
- Break-even: Sales needed to cover costs

**MarketMind Metrics:**
- Demand Score (0-100): How much people want this product
- Competition Score (0-100): How many sellers compete
- Viability Score (0-100): Overall business opportunity
- MPI (Market Power Index): Competition intensity (0-1, lower is better)
- Risk Level: Low/Medium/High business risk
- Trend Strength: How strong the trend is (0-100)
- Growth Velocity: High/Medium/Low trend growth

**Analysis Concepts:**
- Profit Scenarios: Different sales outcomes (conservative/expected/aggressive)
- Seasonality: Products that sell more in certain seasons
- Trend Analysis: Understanding if demand is growing or declining
- Supplier Pricing: Cost to source products from manufacturers

# RESPONSE GUIDELINES

1. **Be Conversational**: Talk like a helpful friend, not a robot
2. **Be Concise**: Keep responses focused and actionable
3. **Use Examples**: Explain with real scenarios
4. **Suggest Actions**: Guide users to next steps
5. **Context-Aware**: Reference what page they're on
6. **Educational**: Teach concepts, don't just answer
7. **Encouraging**: Support beginners, celebrate progress

# RESPONSE FORMAT

Always structure responses as:
1. Direct answer to their question
2. Brief explanation if needed
3. Actionable next step or suggestion
4. (Optional) Related tip or insight

# EXAMPLE INTERACTIONS

User: "What is demand score?"
You: "Demand Score (0-100) measures how much people want a product. It's calculated from search volume, trend growth, and review velocity. Higher is better!

For example, a score of 85+ means strong demand - lots of people are searching and buying. Below 50 means weak demand.

💡 Tip: Look for products with 70+ demand score and low competition for best opportunities."

User: "Should I sell this product?"
You: "I can help you decide! Let me check your analysis results...

Based on your data:
- Demand Score: [X] - [interpretation]
- Competition: [Y] - [interpretation]  
- Risk Level: [Z] - [interpretation]

My recommendation: [Clear yes/no with reasoning]

Next step: [Specific action to take]"

# IMPORTANT RULES

- Never make up data or numbers
- If you don't have context, ask for it
- Always be honest about limitations
- Encourage users to run analyses for accurate data
- Reference specific MarketMind features when relevant
- Use emojis sparingly for emphasis (✅ ❌ 💡 🎯 📊)
"""
        
        # Add page-specific context
        page_context = {
            "discover": "\n\n# CURRENT PAGE: Discover\nUser is exploring trending products. Help them understand trends, suggest products to analyze, explain growth velocity and trend strength.",
            
            "analyze": "\n\n# CURRENT PAGE: Analyze\nUser is setting up a product analysis. Help them choose good parameters (country, budget, risk level). Explain what each field means.",
            
            "profile": "\n\n# CURRENT PAGE: Profile\nUser is viewing their seller profile. Explain the profile settings and how they affect analysis.",
            
            "results": "\n\n# CURRENT PAGE: Market Results\nUser is viewing analysis results. Help interpret scores, explain what the numbers mean, suggest if this is a good opportunity.",
            
            "optimize": "\n\n# CURRENT PAGE: Optimize\nUser is viewing profit optimization. Explain pricing strategy, margins, break-even point. Help them understand profitability.",
            
            "scenarios": "\n\n# CURRENT PAGE: Scenarios\nUser is viewing profit scenarios. Explain conservative/expected/aggressive projections. Help them plan for different outcomes.",
            
            "signals": "\n\n# CURRENT PAGE: Signals\nUser is viewing raw market data. Help interpret the signals, explain what each metric means, identify patterns.",
            
            "strategy": "\n\n# CURRENT PAGE: Strategy\nUser is viewing AI strategy recommendations. Help them understand the strategy, explain risk assessment, suggest implementation steps.",
            
            "history": "\n\n# CURRENT PAGE: History\nUser is viewing past analyses. Help them compare analyses, identify patterns, decide what to analyze next."
        }
        
        if current_page and current_page in page_context:
            base_prompt += page_context[current_page]
        
        return base_prompt
    
    def _format_conversation_history(
        self,
        history: List[Dict[str, str]]
    ) -> List[types.Content]:
        """Format conversation history for Gemini SDK"""
        formatted = []
        for msg in history[-10:]:  # Keep last 10 messages for context
            role = "user" if msg["role"] == "user" else "model"
            formatted.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )
        return formatted
    
    def _extract_suggestions(self, response_text: str) -> List[str]:
        """Extract follow-up suggestions from response"""
        suggestions = []
        
        # Common follow-up patterns
        if "demand score" in response_text.lower():
            suggestions.append("What about competition score?")
        
        if "analyze" in response_text.lower() or "analysis" in response_text.lower():
            suggestions.append("How do I run an analysis?")
        
        if "profit" in response_text.lower():
            suggestions.append("How do I calculate profit margins?")
        
        if "risk" in response_text.lower():
            suggestions.append("What makes a product high risk?")
        
        # Generic helpful suggestions
        if not suggestions:
            suggestions = [
                "Tell me more",
                "What should I do next?",
                "Can you explain that differently?"
            ]
        
        return suggestions[:3]  # Max 3 suggestions
    
    def _detect_action(
        self,
        user_message: str,
        response_text: str
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """Detect if user wants to perform an action"""
        
        user_lower = user_message.lower()
        
        # Navigation actions
        if any(word in user_lower for word in ["go to", "show me", "open", "navigate"]):
            if "discover" in user_lower or "trends" in user_lower:
                return ("navigate_to", {"page": "discover"})
            elif "analyze" in user_lower:
                return ("navigate_to", {"page": "analyze"})
            elif "history" in user_lower:
                return ("navigate_to", {"page": "history"})
        
        # Analysis actions
        if any(word in user_lower for word in ["analyze", "check", "evaluate"]):
            if "product" in user_lower:
                return ("navigate_to", {"page": "analyze"})
        
        return (None, None)
    
    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        current_page: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message and generate intelligent response.
        
        Parameters
        ----------
        user_message : str
            User's message
        conversation_history : List[Dict], optional
            Previous conversation for context
        current_page : str, optional
            Current page user is on
        user_context : Dict, optional
            Additional context (analysis data, etc.)
        
        Returns
        -------
        Dict
            Response with message, suggestions, and optional action
        """
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(current_page)
            
            # Add user context if provided
            context_info = ""
            if user_context:
                context_info = f"\n\n# USER CONTEXT\n{json.dumps(user_context, indent=2)}"
            
            # Prepare conversation
            chat_history = []
            if conversation_history:
                chat_history = self._format_conversation_history(conversation_history)

            # Use sync client in a thread to avoid uvicorn event loop conflicts
            import asyncio
            loop = asyncio.get_event_loop()

            def _sync_chat():
                chat = self.client.chats.create(
                    model=self.model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=f"{system_prompt}{context_info}",
                        temperature=0.7,
                        max_output_tokens=1024,
                    ),
                    history=chat_history,
                )
                return chat.send_message(user_message)

            response = await loop.run_in_executor(None, _sync_chat)
            response_text = response.text
            
            # Extract suggestions
            suggestions = self._extract_suggestions(response_text)
            
            # Detect actions
            action, action_data = self._detect_action(user_message, response_text)
            
            log.info(f"Chat response generated for message: {user_message[:50]}...")
            
            return {
                "message": response_text,
                "suggestions": suggestions,
                "action": action,
                "action_data": action_data
            }
            
        except Exception as exc:
            log.error(f"Chat error: {exc}", exc_info=True)
            
            # Check if it's a quota error
            error_msg = str(exc)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                return {
                    "message": "⚠️ The chat assistant has reached its API quota limit. This happens when too many requests are made.\n\n"
                               "**Solutions:**\n"
                               "1. Wait a few minutes and try again (quota resets every minute)\n"
                               "2. Get a new API key from: https://aistudio.google.com/apikey\n"
                               "3. Update the GEMINI_API_KEY in your .env file\n\n"
                               "For now, you can still use all other MarketMind features. Check the documentation for help!",
                    "suggestions": [
                        "Check documentation",
                        "View API setup guide",
                        "Explore other features"
                    ],
                    "action": None,
                    "action_data": None
                }
            
            # Generic fallback response
            return {
                "message": "I apologize, but I'm having trouble processing your request right now. Please try again or rephrase your question. You can also check our documentation or contact support.",
                "suggestions": [
                    "What is MarketMind?",
                    "How do I analyze a product?",
                    "Explain demand score"
                ],
                "action": None,
                "action_data": None
            }


# Singleton instance
_assistant_instance = None


def get_assistant() -> GeminiAssistant:
    """Get or create Gemini assistant instance"""
    global _assistant_instance
    
    if _assistant_instance is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        _assistant_instance = GeminiAssistant(api_key)
    
    return _assistant_instance
