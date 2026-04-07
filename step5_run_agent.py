from step4_agent_create import agent
print("="*70)
print("RUNNING AGENT")
print("="*70)

question = "Which genre on average has the longest tracks?"

print(f"\nQuestion: {question}\n")
print("-"*70)

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()