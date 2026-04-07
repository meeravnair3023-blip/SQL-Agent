from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_ollama import ChatOllama

print("="*70)
print("CREATING TOOLS")
print("="*70)

# Connect to already downloaded database
print("\n Connecting to database...")
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
print(f" Dialect: {db.dialect}")
print(f" Tables: {len(db.get_usable_table_names())}")

# Initialize Ollama model
print("\n Initializing Ollama model...")
model = ChatOllama(
    model="qwen2.5",
    temperature=0.7,
    base_url="http://localhost:11434",
)

# Create toolkit and get tools
print("\n Creating tools...")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

print(f"\n Created {len(tools)} tools:\n")

for tool in tools:
    print(f"{tool.name}:")
    print(f"  {tool.description}\n")

print("="*70)
print(" Tools ready!")
print("="*70)