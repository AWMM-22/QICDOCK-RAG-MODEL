import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chat_service import chat_service, ConversationMemory
from app.models.chat import ChatRequest, IntentType


def test_conversation_memory():
    memory = ConversationMemory(max_messages=5)
    session_id = "test-session"
    
    memory.add_message(session_id, "user", "Hello")
    memory.add_message(session_id, "assistant", "Hi there!")
    
    history = memory.get_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    
    # Test max messages limit
    for i in range(10):
        memory.add_message(session_id, "user", f"Message {i}")
    
    history = memory.get_history(session_id)
    assert len(history) == 5


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
async def test_product_question():
    request = ChatRequest(
        message="What is the price of the Mahindra XUV 3XO wireless charger?",
        session_id="test-product-1"
    )
    response = await chat_service.process_chat(request)
    
    assert response.intent in [IntentType.PRODUCT, IntentType.MULTI]
    assert len(response.answer) > 0
    assert response.session_id == "test-product-1"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
async def test_organization_question():
    request = ChatRequest(
        message="What is your return policy?",
        session_id="test-org-1"
    )
    response = await chat_service.process_chat(request)
    
    assert response.intent in [IntentType.ORGANIZATION, IntentType.MULTI]
    assert len(response.answer) > 0


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
async def test_out_of_scope_question():
    request = ChatRequest(
        message="Who is the president of the USA?",
        session_id="test-oos-1"
    )
    response = await chat_service.process_chat(request)
    
    assert response.intent == IntentType.OUT_OF_SCOPE
    assert "QICDOCK" in response.answer or "cannot" in response.answer.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
async def test_follow_up_question():
    # First question
    request1 = ChatRequest(
        message="What is the price of the Toyota Glanza wireless charger?",
        session_id="test-followup-1"
    )
    response1 = await chat_service.process_chat(request1)
    
    # Follow-up question
    request2 = ChatRequest(
        message="Does it support iPhone 15?",
        session_id="test-followup-1"
    )
    response2 = await chat_service.process_chat(request2)
    
    assert response2.session_id == "test-followup-1"
    assert len(response2.answer) > 0