import gradio as gr
from step4_agent_create import agent
import ast           # Parse Python expressions .Convert strings → Python objects safely

# Extract only SQL
def extract_sql(text):
    import re

    # Strict SQL extraction
    match = re.search(
        r"(SELECT|INSERT|UPDATE|DELETE)\s.+?(?=;|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(0).strip()

    return None
# Convert DB output → Natural Language
def format_natural_language(query, rows):
    if not rows:
        return "No data found"

    query_lower = query.lower()

    if "artist" in query_lower:
        return "\n".join([f"The artist {row[1]} has ID {row[0]}." for row in rows if len(row) >= 2])

    elif "album" in query_lower:
        return "\n".join([f"The album '{row[0]}' is by {row[1]}." for row in rows if len(row) >= 2])

    elif "genre" in query_lower:
        return "\n".join([f"The genre is {row[0]}." for row in rows])

    elif "customer" in query_lower:
        return "\n".join([f"Customer: {row[0]} {row[1]}." for row in rows if len(row) >= 2])

    elif "song" in query_lower or "track" in query_lower:
        return "\n".join([f"The song is {row[0]}." for row in rows])

    return "\n".join([" | ".join(map(str, row)) for row in rows])


#  Main function
def run_query(user_input):
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        final_msg = result["messages"][-1].content

        if extract_sql(final_msg):
            from step2b_connect_db import db

            try:
                clean_sql = extract_sql(final_msg).strip()

                if not clean_sql:
                    return "Error: Could not generate valid SQL"

                if not clean_sql.endswith(";"):
                    clean_sql += ";"
                    if clean_sql.upper().startswith("DELETE") and "LIMIT" in clean_sql.upper():
                        clean_sql = clean_sql.split("LIMIT")[0].strip()
                        if not clean_sql.endswith(";"):
                             clean_sql += ";"



                # FIX: Auto-correct broken SQL
                if clean_sql.upper().startswith("SELECT"):

                    if "FROM" not in clean_sql.upper():

                        query_lower = user_input.lower()

                        if "album" in query_lower and "artist" in query_lower:
                            clean_sql = """
                            SELECT Album.Title, Artist.Name
                            FROM Album
                            JOIN Artist ON Album.ArtistId = Artist.ArtistId
                            LIMIT 5;
                            """

                        elif "customer" in query_lower:
                            clean_sql = """
                            SELECT FirstName, LastName
                            FROM Customer
                            LIMIT 5;
                            """

                        elif "genre" in query_lower:
                            clean_sql = "SELECT Name FROM Genre LIMIT 5;"

                        elif "artist" in query_lower:
                            clean_sql = "SELECT ArtistId, Name FROM Artist LIMIT 5;"

                        elif "song" in query_lower or "track" in query_lower:
                            clean_sql = "SELECT Name FROM Track LIMIT 5;"

                print("Executing SQL:", clean_sql)

                raw_result = db.run(clean_sql)

                # SELECT
                if clean_sql.upper().startswith("SELECT"):
                    if not raw_result:
                        return "No data found"

                    try:
                        if raw_result.strip().startswith("["):
                            query_result = ast.literal_eval(raw_result)
                        else:
                            lines = raw_result.strip().split("\n")
                            query_result = [(line.strip(),) for line in lines if line.strip()]

                        if not query_result:
                            return "No data found"

                        return format_natural_language(user_input, query_result)

                    except:
                        return raw_result

                elif clean_sql.upper().startswith("INSERT"):
                    return "The record has been successfully created."

                elif clean_sql.upper().startswith("UPDATE"):
                    return "The record has been successfully updated."

                elif clean_sql.upper().startswith("DELETE"):
                    return "The record has been successfully deleted."

            except Exception as e:
                return f"Execution Error: {str(e)}"

        return final_msg

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- UI ---------------- #

with gr.Blocks() as demo:
    gr.Markdown("## AI Database Assistant (CRUD + NLP)")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask: Create artist Vijay")

    def chat(user_message, history):
        if history is None:
            history = []

        history.append({"role": "user", "content": user_message})
        bot_response = run_query(user_message)
        history.append({"role": "assistant", "content": bot_response})

        return "", history

    msg.submit(chat, [msg, chatbot], [msg, chatbot])

demo.launch()