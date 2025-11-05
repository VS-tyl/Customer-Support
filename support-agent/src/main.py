from pendulum import now
from tools.airtable_tools import search_user, create_ticket, ticket_status
from langchain.agents import Tool
from tools.factory import HybridAgentFactory
from tools.supabase_vector import get_vectorstore
try:
    from llm.groq_llm import llm
except Exception as e:
    llm = None
    import sys
    print(f"Warning: failed to import llm from llm.groq_llm: {e}")

airtable_tools = [
    Tool(name="SearchUser", func=search_user, description='''
         Use tool when:
1. When customer wants to create a ticket. In this case we need to make sure customer exists, by asking and verifying user_id.
2. Customer wants to escalate issue. In this case, we need to make sure customer exists, by asking and verifying user_id.'''),

    Tool(name="CreateTicket", func=create_ticket, description='''
Use tool when:
Client faces a problem and needs help of support team.

IMPORTANT:
Before using 'Create Ticket' use tool 'Search User' and make sure user exists in database. If not - don't use it and say 'Sorry to inform, but this user doesnot exist'''),

    Tool(name="TicketStatus", func=ticket_status, description='''
         Use tool when:
1. Customer wants to check the status for his tickets. Before this you must ask the user_id to check if customer exists in database.
If there are multiple tickets, then respond to all.

Note: If you don't find anything then reply that "Sorry, No such ticket exists".''')
]

def get_agent(llm):
    if llm is None:
        print("Error: LLM is not configured. Set up GROQ_API_KEY or provide a working `llm.groq_llm.llm` instance and try again.")
        raise SystemExit(1)
    try:
        vectorstore = get_vectorstore()
    except Exception:
        vectorstore = None

    factory = HybridAgentFactory(
        llm=llm,
        vectorstore=vectorstore,
        tools=airtable_tools,
        system_prompt=f'''
        You are a helpful customer support assistant. 
1. You help answer questions about our services with the knowledge base

IMPORTANT: If you can't find any proper answer for user's query, remind customer that we can create a support ticket too

2. You process customer inquires: you'll create support tickets(when user creates a ticket, let him know that "The ticket has been created and the support team will work on that") in database and help user knowing the status of their tickets(when user wants to check the status of ticket, output only the status of ticket and reason, in the form 
Reason: <the reason>, Status:<status of ticket>) 

Today is: {now()}

Important Rules
Never guess answers. Never make anything up. Always use the tools when needed.
Keep all responses short (under 50 tokens).'''
    )
    agent = factory.create_hybrid_agent()
    return agent

if __name__ == "__main__":
    agent = get_agent(llm)
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = agent.run(user_input)
        print(f"Agent: {response}")
