from langchain_ollama import ChatOllama

model = ChatOllama(
    model="qwen2.5",
    base_url="http://localhost:11434",
)

print("✓ Model ready")