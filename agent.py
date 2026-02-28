"""
agent.py
LangChain ReAct agent with two tools:
  1. VectorSearchTool  — retrieves relevant transcript chunks from ChromaDB
  2. LinkedInSearchTool — enriches lead data with simulated LinkedIn profiles

The agent reasons over transcript signals and LinkedIn data to rank leads
by likelihood of closing within the next month.
"""

from typing import Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
from langchain.schema import Document

from vectorstore import get_vectorstore, similarity_search, get_all_lead_names
from linkedin_tool import lookup_linkedin_profile, format_linkedin_result
from utils import format_context_for_prompt


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

def vector_search_tool_fn(query: str) -> str:
    """
    Search the ChromaDB vectorstore for transcript chunks relevant to the query.
    Returns formatted context grouped by lead name.
    """
    try:
        vectorstore = get_vectorstore()
        docs: list[Document] = similarity_search(query, vectorstore=vectorstore, k=10)
        if not docs:
            return "No relevant transcript data found."
        return format_context_for_prompt(docs)
    except Exception as e:
        return f"Vector search failed: {str(e)}"


def linkedin_search_tool_fn(lead_name: str) -> str:
    """
    Retrieve a simulated LinkedIn profile for the given lead name.
    Input should be the full name of the lead (e.g. 'Sarah Johnson').
    """
    lead_name = lead_name.strip().strip('"').strip("'")
    if not lead_name:
        return "Please provide a lead name to search."
    profile = lookup_linkedin_profile(lead_name)
    return format_linkedin_result(profile)


VECTOR_SEARCH_TOOL = Tool(
    name="VectorSearchTool",
    func=vector_search_tool_fn,
    description=(
        "Search sales call transcripts stored in ChromaDB. "
        "Use this to find buying signals, objections, budget mentions, timelines, "
        "and decision-maker indicators from actual sales conversations. "
        "Input: a natural language query about leads or buying intent."
    ),
)

LINKEDIN_SEARCH_TOOL = Tool(
    name="LinkedInSearchTool",
    func=linkedin_search_tool_fn,
    description=(
        "Look up a lead's LinkedIn profile to get their job title, seniority, "
        "company size, industry, and whether they are a decision-maker. "
        "Input: the full name of the lead (e.g. 'Sarah Johnson'). "
        "Use this AFTER identifying lead names from transcript search."
    ),
)


# ---------------------------------------------------------------------------
# Scoring prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert sales analyst. Your job is to analyze sales call transcripts and rank leads by their likelihood of purchasing within the next month.

You have access to these tools:
- VectorSearchTool: Search actual sales transcript data
- LinkedInSearchTool: Get professional background on any lead

Your analysis process:
1. Use VectorSearchTool to retrieve all relevant transcript data about leads and buying intent
2. Identify all lead names from the transcripts
3. For each lead, use LinkedInSearchTool to enrich their profile
4. Score and rank each lead from 0-100 based on:
   - Buying intent phrases ("we need this by", "ready to move forward", "when can we start")
   - Budget mentions (explicit amounts, "budget approved", "we have funds")
   - Timeline urgency ("next quarter", "by end of month", "ASAP")
   - Objections vs positive signals (ratio matters)
   - Decision-maker authority (C-suite > Director > Manager > IC)
   - Company size (larger = bigger deal but longer cycle)

Output format — you MUST use exactly this structure:
1. [Lead Name] - Score: [0-100]
- [Key signal 1 from transcript]
- [Key signal 2 from transcript]  
- [LinkedIn insight]
- [Summary of why they will/won't buy soon]

2. [Lead Name] - Score: [0-100]
...

Be specific. Quote actual phrases from transcripts when possible."""


def build_agent() -> AgentExecutor:
    """
    Build and return a LangChain ReAct agent with vector search and LinkedIn tools.
    Uses the standard ReAct prompt from LangChain hub.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=False,
    )

    tools = [VECTOR_SEARCH_TOOL, LINKEDIN_SEARCH_TOOL]

    # Pull the standard ReAct prompt and prepend our system instructions
    react_prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )

    return executor


def analyze_leads(question: str = None) -> str:
    """
    Run the agent to analyze leads and answer a manager's question.

    Args:
        question: Manager's query (defaults to standard ranking question).

    Returns:
        Agent's final text response with ranked leads.
    """
    if question is None:
        question = "Which leads are most likely to buy in the next month? Rank them with scores and explain why."

    agent = build_agent()

    # Inject system context into the user query
    full_query = f"{SYSTEM_PROMPT}\n\nManager's question: {question}"

    result = agent.invoke({"input": full_query})
    return result.get("output", "No analysis could be generated.")


if __name__ == "__main__":
    from utils import load_environment
    load_environment()
    output = analyze_leads()
    print("\n" + "=" * 60)
    print("AGENT OUTPUT")
    print("=" * 60)
    print(output)
