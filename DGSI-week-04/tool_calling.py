"""
LLM Tool-Calling Loop with Human-in-the-Loop Protection.

This script demonstrates how to use OpenAI function calling in a continuous
loop with two tools:
  - execute_sql: runs SQL against a local SQLite database.
  - wget: fetches a URL using the system `wget` command (requires user confirmation).
"""

import json
import os
import sqlite3
import subprocess

from dotenv import load_dotenv
from openai import OpenAI

# ── Load environment variables & create client ──────────────────────────────
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_ENDPOINT"),
)
MODEL  = os.getenv("MODEL")
DB     = "database.db"

# ── Tool implementations ────────────────────────────────────────────────────

def execute_sql(statement: str) -> str:
    """Execute a SQL statement against the local SQLite database."""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(statement)
        conn.commit()

        # If the statement returns rows, format them nicely
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows    = cursor.fetchall()
            result  = [dict(zip(columns, row)) for row in rows]
            return json.dumps(result, indent=2)

        return f"OK – {cursor.rowcount} row(s) affected."
    except Exception as e:
        return f"SQL ERROR: {e}"
    finally:
        conn.close()


def wget(url: str, args: str = "") -> str:
    """Fetch a URL using the system wget command (human-in-the-loop)."""
    cmd = f"wget {args} -qO- {url}"

    # ── Human-in-the-loop gate ──────────────────────────────────────────
    print(f"\n⚠️  The model wants to run:\n    {cmd}")
    approval = input("Allow? (y/n): ").strip().lower()

    if approval != "y":
        return "USER DENIED: command was not executed."

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return f"WGET ERROR (exit {result.returncode}): {result.stderr.strip()}"
        return result.stdout
    except Exception as e:
        return f"WGET ERROR: {e}"


# ── OpenAI tool schemas ────────────────────────────────────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": (
                "Run a SQL statement (DDL, DML, or query) against a local "
                "SQLite database file called database.db and return the result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "statement": {
                        "type": "string",
                        "description": "The SQL statement to execute.",
                    }
                },
                "required": ["statement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wget",
            "description": (
                "Fetch the contents of a URL using the system wget command. "
                "Returns the raw response body."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch.",
                    },
                    "args": {
                        "type": "string",
                        "description": "Optional extra arguments for wget.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]

# ── Dispatch dictionary mapping tool names → Python functions ───────────────

dispatch = {
    "execute_sql": lambda args: execute_sql(args["statement"]),
    "wget":        lambda args: wget(args["url"], args.get("args", "")),
}

# ── Main execution loop ────────────────────────────────────────────────────

def main():
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful data-engineering assistant. "
                "Use the provided tools to complete the user's request."
            ),
        },
        {
            "role": "user",
            "content": (
                "Fetch https://jsonplaceholder.typicode.com/users and store "
                "the id, name, email, and city of every user in a SQLite "
                "table called users. Show me the final contents of the table."
            ),
        },
    ]

    print("🚀 Starting tool-calling loop …\n")

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        choice = response.choices[0]

        # ── If the model made tool calls, execute them ──────────────────
        if choice.finish_reason == "tool_calls":
            # Append the assistant message (contains the tool_calls)
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                print(f"🔧 Calling {fn_name}({json.dumps(fn_args, indent=2)})")

                # Execute the matching function via the dispatch dictionary
                try:
                    result = dispatch[fn_name](fn_args)
                except Exception as e:
                    result = f"TOOL ERROR: {e}"

                print(f"   ↳ Result preview: {result[:120]}…\n" if len(result) > 120 else f"   ↳ Result: {result}\n")

                # Feed the result back to the model
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

        # ── Otherwise the model returned a final text answer ────────────
        else:
            print("✅ Final answer:\n")
            print(choice.message.content)
            break


if __name__ == "__main__":
    main()
