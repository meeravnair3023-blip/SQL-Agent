from step4_agent_create import agent
import ast
from validator import validate_and_fix
import re
from step2b_connect_db import db


# 🔥 Extract SQL
def extract_sql(text):
    
    match = re.search(
        r"(SELECT|INSERT|UPDATE|DELETE)\s.+?(?=;|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    return match.group(0).strip() if match else None


# 🔥 Format output
def format_natural_language(query, rows):
    if not rows:
        return "No data found"

    query_lower = query.lower()

    # Album + Artist
    if "album" in query_lower and "artist" in query_lower:
        return "\n".join([
            f"Album: '{row[0]}' | Artist: {row[1]}"
            for row in rows if len(row) >= 2
        ])

    # Album
    elif "album" in query_lower:
        return "\n".join([
            f"Album: '{row[0]}'"
            for row in rows
        ])

    # Artist
    elif "artist" in query_lower:
        return "\n".join([
            f"The artist {row[1]} has ID {row[0]}"
            for row in rows if len(row) >= 2
        ])

    # Customer
    elif "customer" in query_lower:
        return "\n".join([
            f"Customer: {row[0]} {row[1]}"
            for row in rows if len(row) >= 2
        ])

    # Genre
    elif "genre" in query_lower:
        return "\n".join([
            f"The genre is {row[0]}"
            for row in rows
        ])

    # Track
    elif "track" in query_lower or "song" in query_lower:
        return "\n".join([
            f"The song is {row[0]}"
            for row in rows
        ])

    return str(rows)


def is_sql_response(text):
    return any(k in text.upper() for k in ["SELECT", "INSERT", "UPDATE", "DELETE"])


# 🔥 MAIN EXECUTION
def run_query(user_input):
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        final_msg = result["messages"][-1].content
        print("LLM OUTPUT:", final_msg)

        sql = extract_sql(final_msg)

        if not sql:
            return "Sorry, I couldn't generate SQL."

        sql = sql.strip()
        if not sql.endswith(";"):
            sql += ";"

        print("Executing SQL:", sql)

        # 🔥 REAL DB EXECUTION
        raw_result = db.run(sql)

        # ---------------- SELECT ----------------
        if sql.upper().startswith("SELECT"):
            if not raw_result:
                return "No data found"
            return format_natural_language(user_input, raw_result)

        # ---------------- INSERT ----------------
        elif sql.upper().startswith("INSERT"):
            if raw_result == "OK":
                return "Record created successfully"
            return f"Insert failed: {raw_result}"

        # ---------------- UPDATE ----------------
        elif sql.upper().startswith("UPDATE"):
            if raw_result == "OK":
                return "Record updated successfully"
            return f"Update failed: {raw_result}"

        # ---------------- DELETE ----------------
        elif sql.upper().startswith("DELETE"):
            if raw_result == "OK":
                return "Record deleted successfully"
            return f"Delete failed: {raw_result}"

        return "Could not process request."

    except Exception as e:
        return f"Error: {str(e)}"


# 🔥 VALIDATOR LOOP
def run_query_with_full_validation(user_input, max_retries=1):
    result = run_query(user_input)

    # only validate FINAL OUTPUT, not SQL
    is_valid, _ = validate_and_fix(user_input, result)

    print("VALIDATOR:", "YES" if is_valid else "NO")

    return result

    return "Sorry, I couldn't generate a correct answer."