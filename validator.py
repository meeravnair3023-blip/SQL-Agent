from langchain_ollama import ChatOllama

validator_llm = ChatOllama(model="llama3")

def validate_and_fix(question, answer):
    prompt = f"""
You are a strict evaluator.

Question: {question}
Answer: {answer}

Reply ONLY in this format:

YES
or
NO

Do NOT add any explanation.
"""

    response = validator_llm.invoke(prompt).content.strip().upper()

    if "YES" in response:
        print("VALIDATOR: YES")   # ✅ terminal only
        return True, answer
    else:
        print("VALIDATOR: NO")    # ✅ terminal only
        return False, answer