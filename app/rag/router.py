from typing import Dict, Any, Literal
from app.core.logging import logger
from app.models.chat import IntentType


def get_llm_provider():
    from app.services.llm import get_llm_provider as _get_llm_provider
    return _get_llm_provider()


IntentLiteral = Literal["PRODUCT", "ORGANIZATION", "MULTI", "OUT_OF_SCOPE"]


ROUTER_PROMPT = """You are a query classifier for a QICDOCK automotive accessories chatbot.
QICDOCK sells vehicle-specific wireless phone chargers for cars.

Classify the user's question into exactly one of these categories:

1. PRODUCT - Questions about QICDOCK products:
   - Product prices, specifications, features
   - Compatibility with specific vehicles
   - Product availability, stock
   - Which product to buy for a specific car
   - Product comparisons
   - "What is the price of X?"
   - "Does this charger work with iPhone 15?"
   - "Which charger for Toyota Glanza?"

2. ORGANIZATION - Questions about the company:
   - Company information, mission, about us
   - Policies (returns, refunds, shipping, warranty, cancellation)
   - FAQs
   - Contact information
   - "What is your return policy?"
   - "How long does shipping take?"
   - "How can I contact support?"

3. MULTI - Questions that need BOTH product AND organization info:
   - "What is the price of X and what is your return policy?"
   - "Which charger for my car and how long is warranty?"
   - Combined questions needing both sources

4. OUT_OF_SCOPE - Unrelated questions:
   - General knowledge, weather, news
   - Other companies' products
   - Personal questions
   - "Who is the president?"
   - "What's the weather?"

Output ONLY a JSON object:
{"intent": "PRODUCT"} or {"intent": "ORGANIZATION"} or {"intent": "MULTI"} or {"intent": "OUT_OF_SCOPE"}"""


async def classify_intent(query: str) -> IntentType:
    llm = get_llm_provider()
    
    try:
        result = await llm.generate_structured(
            prompt=f"Question: {query}",
            schema={
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["PRODUCT", "ORGANIZATION", "MULTI", "OUT_OF_SCOPE"]
                    }
                },
                "required": ["intent"]
            },
            system_prompt=ROUTER_PROMPT
        )
        
        intent_str = result.get("intent", "OUT_OF_SCOPE")
        logger.info(f"Query classified as: {intent_str}")
        
        return IntentType(intent_str)
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return IntentType.OUT_OF_SCOPE


def classify_intent_simple(query: str) -> IntentType:
    query_lower = query.lower()
    
    product_keywords = ["price", "cost", "charger", "wireless", "charging", "compatible", "iphone", "android", "magSafe", "qi", "product", "buy", "purchase", "specification", "feature", "availability", "stock", "sku", "model", "vehicle", "car", "toyota", "mahindra", "maruti", "suzuki", "glanza", "swift", "dzire", "taisor", "xuv"]
    org_keywords = ["policy", "return", "refund", "shipping", "delivery", "warranty", "contact", "support", "company", "about", "faq", "question", "help", "customer", "service", "cancel", "payment", "order"]
    
    has_product = any(kw in query_lower for kw in product_keywords)
    has_org = any(kw in query_lower for kw in org_keywords)
    
    if has_product and has_org:
        return IntentType.MULTI
    elif has_product:
        return IntentType.PRODUCT
    elif has_org:
        return IntentType.ORGANIZATION
    else:
        return IntentType.OUT_OF_SCOPE