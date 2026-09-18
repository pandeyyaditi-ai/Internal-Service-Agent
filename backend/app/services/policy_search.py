"""
FAQ/Policy search service.
Searches the IT FAQ knowledge base using keyword matching
and synthesizes answers using Gemini API.
"""
import json
import os
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("policy_search")

# Load FAQ data
FAQ_DATA = None
FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "faqs", "it_faq.json")
POLICY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "policies")

# Try to import Gemini
gemini_model = None
try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-pro")
except Exception:
    pass


def load_faq_data() -> Dict[str, Any]:
    """Load FAQ data from JSON file."""
    global FAQ_DATA
    if FAQ_DATA is None:
        try:
            with open(FAQ_PATH, "r", encoding="utf-8") as f:
                FAQ_DATA = json.load(f)
            logger.info(f"Loaded {len(FAQ_DATA.get('faqs', []))} FAQ entries")
        except FileNotFoundError:
            logger.error(f"FAQ file not found: {FAQ_PATH}")
            FAQ_DATA = {"faqs": [], "categories": {}}
        except Exception as e:
            logger.error(f"Failed to load FAQ data: {e}")
            FAQ_DATA = {"faqs": [], "categories": {}}
    return FAQ_DATA


def search_faqs(query: str, category: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search FAQs using keyword matching.
    Returns top_k most relevant FAQ entries with relevance scores.
    """
    data = load_faq_data()
    faqs = data.get("faqs", [])
    query_lower = query.lower()
    query_words = set(query_lower.split())

    results = []
    for faq in faqs:
        # Filter by category if specified
        if category and faq.get("category") != category:
            continue

        score = 0.0

        # Check keyword matches
        keywords = faq.get("keywords", [])
        matched_keywords = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in query_lower:
                score += 2.0
                matched_keywords.append(keyword)
            elif any(word in keyword_lower for word in query_words):
                score += 0.5
                matched_keywords.append(keyword)

        # Check question similarity
        question_lower = faq.get("question", "").lower()
        question_words = set(question_lower.split())
        overlap = query_words.intersection(question_words)
        score += len(overlap) * 0.3

        # Check answer content
        answer_lower = faq.get("answer", "").lower()
        for word in query_words:
            if len(word) > 3 and word in answer_lower:
                score += 0.1

        if score > 0:
            results.append({
                "faq_id": faq["id"],
                "question": faq["question"],
                "answer": faq["answer"],
                "category": faq["category"],
                "relevance_score": round(min(1.0, score / 5.0), 2),
                "matched_keywords": matched_keywords,
                "related_policy": faq.get("related_policy"),
            })

    # Sort by relevance score
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:top_k]


def load_policy(policy_name: str) -> Optional[str]:
    """Load a policy document by name."""
    policy_file = os.path.join(POLICY_DIR, f"{policy_name}.txt")
    try:
        with open(policy_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Policy file not found: {policy_file}")
        return None
    except Exception as e:
        logger.error(f"Failed to load policy {policy_name}: {e}")
        return None


async def synthesize_answer_gemini(query: str, faq_results: List[Dict[str, Any]], policy_content: Optional[str] = None) -> str:
    """Use Gemini to synthesize a natural answer from FAQ results and policy content."""
    if not gemini_model:
        return None

    context_parts = []
    for result in faq_results:
        context_parts.append(f"Q: {result['question']}\nA: {result['answer']}")

    if policy_content:
        context_parts.append(f"\nRelevant Policy Document:\n{policy_content[:2000]}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a helpful IT support agent. Based on the following knowledge base entries and policy documents, provide a clear, concise answer to the user's question.

Knowledge Base Context:
{context}

User's Question: "{query}"

Instructions:
- Answer directly and helpfully
- Use bullet points or numbered steps when appropriate
- Reference the relevant policy if applicable
- Keep the response concise but complete
- If the knowledge base doesn't fully answer the question, say what you can and suggest contacting IT support for more details
- Do NOT make up information not present in the context"""

    try:
        response = await gemini_model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini answer synthesis failed: {e}")
        return None


async def search_and_respond(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Main search function: finds relevant FAQs, loads related policies,
    and synthesizes an answer.
    """
    # Search FAQs
    faq_results = search_faqs(query, category)

    if not faq_results:
        return {
            "answer": "I couldn't find a specific answer to your question in our knowledge base. Let me create a support ticket so our IT team can help you directly. Would you like me to do that?",
            "sources": [],
            "confidence": 0.2,
        }

    # Load related policy if available
    policy_content = None
    for result in faq_results:
        if result.get("related_policy"):
            policy_content = load_policy(result["related_policy"])
            if policy_content:
                break

    # Try Gemini synthesis
    synthesized = await synthesize_answer_gemini(query, faq_results, policy_content)

    if synthesized:
        answer = synthesized
    else:
        # Fallback: use the top FAQ answer directly
        top_result = faq_results[0]
        answer = top_result["answer"]

    # Build source references
    sources = []
    for result in faq_results:
        source = {
            "source_name": f"FAQ: {result['question']}",
            "source_type": "faq",
            "relevance_score": result["relevance_score"],
            "excerpt": result["answer"][:150] + "..." if len(result["answer"]) > 150 else result["answer"],
        }
        sources.append(source)

    if policy_content:
        policy_name = faq_results[0].get("related_policy", "policy")
        sources.append({
            "source_name": f"Policy: {policy_name.replace('_', ' ').title()}",
            "source_type": "policy",
            "relevance_score": 0.8,
            "excerpt": policy_content[:150] + "...",
        })

    return {
        "answer": answer,
        "sources": sources,
        "confidence": faq_results[0]["relevance_score"],
    }
