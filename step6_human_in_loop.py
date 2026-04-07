import os

# MUST BE FIRST (before any langchain import)there is a limit for langsmith free use so we set it false to avoid errors, you can remove this if you have langsmith tracing enabled
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""

from dotenv import load_dotenv
load_dotenv()

# Now import LangChain
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

print("="*70)
print("HUMAN-IN-THE-LOOP SQL AGENT")
print("="*70)

# ================= DATABASE =================
print("\nConnecting to database...")
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
print(f"Dialect: {db.dialect}")

# ================= MODEL =================
print("\nInitializing Ollama model...")
model = ChatOllama(
    model="qwen2.5",
    temperature=0,
    base_url="http://localhost:11434",
)
print("Model ready")

# ================= TOOLS =================
print("\nCreating tools...")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()
print(f" {len(tools)} tools ready")

# ================= SYSTEM PROMPT =================
system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer.

Always limit results to {top_k} unless specified.

Do NOT use INSERT, UPDATE, DELETE, DROP.

Always:
1. List tables
2. Check schema
3. Generate query
4. Double check query
""".format(
    dialect=db.dialect,
    top_k=5,
)

# ================= AGENT =================
print("\n Building agent with Human-in-the-Loop...")

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"sql_db_query": True},  # only pause here
            description_prefix="SQL Query needs approval",
        ),
    ],
    checkpointer=MemorySaver(),
)

print("Agent ready!")
print("="*70)

# ================= RUN =================
question = "Which genre on average has the longest tracks?"
config = {"configurable": {"thread_id": "1"}}

print(f"\nQuestion: {question}\n")
print("-"*70)

# ================= EXECUTION =================
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    config,
    stream_mode="values",
):

    #  If interrupted → ask user
    if "__interrupt__" in step:
        print("\n" + "="*70)
        print(" SQL QUERY NEEDS APPROVAL")
        print("="*70)

        interrupt = step["__interrupt__"][0]

        for req in interrupt.value["action_requests"]:
            print(f"\nTool: {req['name']}")
            print(f"Query:\n{req['args']['query']}")

        decision = input("\nApprove this query? (yes/no): ").strip().lower()

        if decision == "yes":
            resume = {"decisions": [{"type": "approve"}]}
        else:
            resume = {"decisions": [{"type": "reject"}]}

        # Resume execution
        for step in agent.stream(
            Command(resume=resume),
            config,
            stream_mode="values",
        ):
            if "messages" in step:
                step["messages"][-1].pretty_print()

    # Normal messages
    elif "messages" in step:
        step["messages"][-1].pretty_print()