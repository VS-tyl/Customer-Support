from typing import List, Callable, Any
from langchain.agents import initialize_agent, Tool
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

class HybridAgentFactory:
    def __init__(self, llm=None, vectorstore=None, tools: List[Tool]=None, memory=None, system_prompt:str=None, k:int=3):
        """
        llm: LangChain LLM instance
        vectorstore: LangChain VectorStore instance (e.g., FAISS, Supabase, Pinecone)
        tools: List of LangChain Tool instances
        memory: LangChain Memory instance (default: ConversationBufferMemory)
        system_prompt: String guiding agent behavior
        k: number of documents to retrieve in RAG
        """
        self.llm = llm
        self.vectorstore = vectorstore
        self.memory = memory or ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.k = k
        self.user_tools = tools or []
        self.system_prompt = system_prompt 

    def _create_rag_tool(self) -> Tool:
        """Wrap the RAG chain as a tool so the agent can call it dynamically."""
        if not self.vectorstore:
            raise ValueError("VectorStore must be provided for RAG tool")

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.k})
        rag_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True
        )

        def rag_func(query: str) -> str:
            result = rag_chain({"question": query})
            return result["answer"]

        return Tool(
            name="DocumentQA",
            func=rag_func,
            description="Use this tool to answer questions using enterprise documents. Only use if question relates to stored knowledge or company data."
        )

    def create_hybrid_agent(self) -> Any:
        """Return a single agent combining RAG + tools + memory."""
        # Combine user-provided tools with RAG tool (only if vectorstore exists)
        all_tools = list(self.user_tools)
        if self.vectorstore:
            all_tools.append(self._create_rag_tool())

        tool_instructions = "Available tools: " + "; ".join([f"{t.name}: {t.description}" for t in all_tools])
        prompt = PromptTemplate.from_template(self.system_prompt)

        agent = initialize_agent(
            tools=all_tools,
            llm=self.llm,
            agent="conversational-react-description",
            memory=self.memory,
            verbose=True,
            prompt=prompt
        )

        return agent


