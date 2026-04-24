import gradio as gr
import requests

def chat(user_message, history):
    if history is None:
        history = []

    try:
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"query": user_message}
        )

        bot_reply = response.json()["response"]

    except Exception as e:
        print("ERROR:", e)
        bot_reply = "Server error. Check FastAPI."

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_reply})

    return "", history


with gr.Blocks() as demo:
    gr.Markdown("## 🎵 AI Database Assistant")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask something...")

    msg.submit(chat, [msg, chatbot], [msg, chatbot])

demo.launch()