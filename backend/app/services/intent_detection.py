"""
Intent detection service using Google Gemini API.
Classifies user messages into actionable intents with confidence scores.
Falls back to keyword matching if Gemini API is unavailable.
"""
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("intent_detection")

# Try to import Gemini
gemini_model = None
try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-pro")
        logger.info("Gemini API configured successfully")
    else:
        logger.warning("No Gemini API key configured — using keyword fallback")
except ImportError:
    logger.warning("google-generativeai not installed — using keyword fallback")
except Exception as e:
    logger.warning(f"Failed to configure Gemini: {e} — using keyword fallback")


# Supported intents
INTENTS = {
    "vpn_issue": {
        "description": "VPN connectivity, configuration, or troubleshooting",
        "keywords": ["vpn", "globalprotect", "remote access", "connect remotely", "vpn error",
                     "vpn not working", "can't connect vpn", "vpn timeout", "split tunnel",
                     "vpn slow", "vpn setup", "vpn install"],
    },
    "faq": {
        "description": "General IT questions that can be answered from the knowledge base",
        "keywords": ["how do i", "how to", "what is", "where can", "help me",
                     "password", "reset", "email", "setup", "install", "printer",
                     "wifi", "network", "access", "mfa", "two-factor", "phishing",
                     "software", "teams", "outlook", "onboarding", "offboarding"],
    },
    "ticket_request": {
        "description": "Creating a new ticket or checking ticket status",
        "keywords": ["create ticket", "new ticket", "open ticket", "submit ticket",
                     "ticket status", "check ticket", "my ticket", "track ticket",
                     "update ticket", "close ticket", "ticket number"],
    },
    "escalation": {
        "description": "User explicitly requests human assistance",
        "keywords": ["talk to human", "human agent", "real person", "escalate",
                     "speak to someone", "transfer", "not helpful", "supervisor",
                     "manager", "live agent", "connect me to", "talk to agent"],
    },
    "general": {
        "description": "Greetings, thanks, unclear intent, or general conversation",
        "keywords": ["hello", "hi", "hey", "thanks", "thank you", "bye",
                     "good morning", "good afternoon", "ok", "sure", "yes", "no"],
    },
}


async def detect_intent_gemini(message: str, conversation_context: str = "") -> Dict[str, Any]:
    """Use Gemini API to detect intent from user message."""
    if not gemini_model:
        return None

    prompt = f"""You are an IT support intent classifier. Analyze the user's message and classify it into one of these intents:

1. "vpn_issue" - VPN connectivity, configuration, setup, or troubleshooting problems
2. "faq" - General IT questions (password, email, software, hardware, network, security)
3. "ticket_request" - User wants to create, check, or update a support ticket
4. "escalation" - User explicitly wants to talk to a human agent
5. "general" - Greetings, thanks, unclear, or casual conversation

Conversation context (if any): {conversation_context}

User message: "{message}"

Respond in JSON format ONLY (no markdown, no code blocks):
{{"intent": "<intent_name>", "confidence": <0.0-1.0>, "entities": {{"topic": "<detected_topic>", "urgency": "<low/medium/high>"}}, "reasoning": "<brief_explanation>"}}"""

    try:
        response = await gemini_model.generate_content_async(prompt)
        response_text = response.text.strip()

        # Clean up response — remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        result = json.loads(response_text)
        logger.info(f"Gemini intent detection: {result.get('intent')} (confidence: {result.get('confidence')})")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Gemini response: {e}")
        return None
    except Exception as e:
        logger.warning(f"Gemini intent detection failed: {e}")
        return None


def detect_intent_keywords(message: str) -> Dict[str, Any]:
    """Fallback keyword-based intent detection."""
    message_lower = message.lower().strip()
    scores = {}

    for intent, config in INTENTS.items():
        score = 0
        matched_keywords = []
        for keyword in config["keywords"]:
            if keyword in message_lower:
                score += 1
                matched_keywords.append(keyword)
        if score > 0:
            scores[intent] = {
                "score": score,
                "matched": matched_keywords,
                "total_keywords": len(config["keywords"]),
            }

    if not scores:
        return {
            "intent": "general",
            "confidence": 0.3,
            "entities": {"topic": "unknown", "urgency": "low"},
            "reasoning": "No keywords matched — defaulting to general",
        }

    # Find best match
    best_intent = max(scores, key=lambda k: scores[k]["score"])
    best_data = scores[best_intent]
    confidence = min(0.9, best_data["score"] / max(3, best_data["total_keywords"]) + 0.3)

    # Determine urgency from keywords
    urgency = "low"
    urgent_words = ["urgent", "critical", "asap", "emergency", "broken", "can't work", "blocked"]
    if any(w in message_lower for w in urgent_words):
        urgency = "high"
    elif any(w in message_lower for w in ["important", "need help", "not working", "error"]):
        urgency = "medium"

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "entities": {
            "topic": best_data["matched"][0] if best_data["matched"] else "general",
            "urgency": urgency,
        },
        "reasoning": f"Matched keywords: {', '.join(best_data['matched'])}",
    }


async def detect_intent(message: str, conversation_context: str = "") -> Dict[str, Any]:
    """
    Detect intent from a user message.
    Tries Gemini first, falls back to keyword matching.
    """
    # Try Gemini first
    result = await detect_intent_gemini(message, conversation_context)

    if result and result.get("intent") in INTENTS:
        result["method"] = "gemini"
        return result

    # Fallback to keyword matching
    result = detect_intent_keywords(message)
    result["method"] = "keyword"
    return result
