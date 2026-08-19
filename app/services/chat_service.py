import uuid
from typing import List, Dict, Any, Optional
from app.models.chat import ChatRequest, ChatResponse, SourceInfo, IntentType, RetrievedDocument
from app.rag.retriever import get_retriever
from app.core.logging import logger


def get_router_functions():
    from app.rag.router import classify_intent, classify_intent_simple
    return classify_intent, classify_intent_simple


def get_context_functions():
    from app.rag.context import filter_relevant_documents, build_context, rewrite_query_with_history
    return filter_relevant_documents, build_context, rewrite_query_with_history


def get_generator_function():
    from app.rag.generator import generate_answer
    return generate_answer


class ConversationMemory:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._sessions.get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append({"role": role, "content": content})
        
        if len(self._sessions[session_id]) > self.max_messages:
            self._sessions[session_id] = self._sessions[session_id][-self.max_messages:]
    
    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


memory = ConversationMemory()


class ChatService:
    def __init__(self):
        self.retriever = get_retriever()
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request: session={session_id}, message={request.message[:100]}")
        
        history = memory.get_history(session_id)
        
        _, rewrite_query_with_history = get_context_functions()[2], get_context_functions()[2]
        rewritten_query = rewrite_query_with_history(request.message, history)
        
        _, classify_intent_simple = get_router_functions()
        intent = classify_intent_simple(rewritten_query)
        
        product_docs = []
        org_docs = []
        
        if intent in [IntentType.PRODUCT, IntentType.MULTI]:
            product_docs = self.retriever.retrieve_products(rewritten_query)
            filter_relevant_documents, _, _ = get_context_functions()
            product_docs = filter_relevant_documents(product_docs)
        
        if intent in [IntentType.ORGANIZATION, IntentType.MULTI]:
            org_docs = self.retriever.retrieve_organization(rewritten_query)
            filter_relevant_documents, _, _ = get_context_functions()
            org_docs = filter_relevant_documents(org_docs)
        
        if intent == IntentType.OUT_OF_SCOPE:
            answer = "I can help you with questions about QICDOCK products, services, policies, and organization. I don't have information about that topic."
            sources = []
        else:
            _, build_context, _ = get_context_functions()
            context = build_context(product_docs, org_docs, intent)
            generate_answer = get_generator_function()
            answer = await generate_answer(rewritten_query, context, intent.value, history)
            
            sources = []
            for doc in product_docs:
                sources.append(SourceInfo(
                    type="product",
                    product_name=doc.metadata.get("product_name"),
                    metadata=doc.metadata
                ))
            for doc in org_docs:
                sources.append(SourceInfo(
                    type="organization",
                    filename=doc.metadata.get("filename"),
                    metadata=doc.metadata
                ))
        
        memory.add_message(session_id, "user", request.message)
        memory.add_message(session_id, "assistant", answer)
        
        return ChatResponse(
            answer=answer,
            intent=intent,
            sources=sources,
            session_id=session_id
        )


chat_service = ChatService()