import os
import psycopg2
from psycopg2 import sql
import openai
import textwrap

# Load secrets from environment (do NOT hardcode in source)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "summarizer")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # must be set in environment

API_KEY = os.getenv("OPENROUTER_API_KEY")  # must be set in env
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-3.5-turbo")

if not DB_PASSWORD or not API_KEY:
    raise RuntimeError("Set DB_PASSWORD and OPENROUTER_API_KEY environment variables")

openai.api_key = API_KEY
openai.api_base = BASE_URL

CSV_TABLES = [
    ("Sales", "sales", "public"),
    ("Customer Reviews", "customer_reviews", "public"),
]

TABLE_CONFIGS = []
for label, table_name, schema in CSV_TABLES:
    # Use explicit column name if you have a natural sort column (here using ORDER BY 1 as fallback)
    query = f"SELECT * FROM {schema}.{table_name} ORDER BY 1 ASC LIMIT 5"
    TABLE_CONFIGS.append({"table_label": label, "query": query})

def fetch_data(query, timeout_seconds=10):
    """Safely fetch rows using context managers. Returns list of rows or [] on error."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            connect_timeout=timeout_seconds
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return rows
    except Exception as e:
        print(f"⚠️ DB fetch error for query [{query}]: {e}")
        return []

def safe_get_content_from_response(resp):
    """Return string content of a chat completion response safely."""
    try:
        # Some SDKs return nested dicts; access safely
        choice = resp.get("choices", [None])[0] if isinstance(resp, dict) else getattr(resp.choices[0], "message", None)
        if isinstance(choice, dict):
            return choice.get("message", {}).get("content") or choice.get("message", {}).get("content")
        # Fallbacks
        return getattr(choice, "message", {}).get("content", None) or getattr(choice, "message", None)
    except Exception:
        # Last resort: try standard attribute access
        try:
            return resp.choices[0].message.content
        except Exception:
            return None

def call_model(prompt, max_tokens=256, temperature=0.2):
    """Call model and return string or raise/return None on failure."""
    try:
        resp = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=30
        )
        # Avoid printing entire resp (may contain meta). Only return text.
        content = None
        # resp may be a dict or an object--handle both
        if hasattr(resp, "choices"):
            # try attribute style
            try:
                content = resp.choices[0].message.content
            except Exception:
                content = safe_get_content_from_response(resp.__dict__)
        else:
            content = safe_get_content_from_response(resp)
        if not content:
            print("⚠️ No content returned from model.")
            return None
        return content.strip()
    except Exception as e:
        print(f"⚠️ Model call failed: {e}")
        return None

def summarize_combined_data(combined_text):
    if not combined_text.strip():
        return "No data available from any table for summarization."
    # Simple truncation to limit tokens; better: summarize per-table first.
    MAX_CHARS = 8000
    if len(combined_text) > MAX_CHARS:
        combined_text = combined_text[:MAX_CHARS] + "\n\n[TRUNCATED]"
    prompt = textwrap.dedent(f"""
        Analyze the following data extracted from multiple sources.
        Provide a concise summary of key trends, insights, and areas of interest (about 50 words).

        Data:
        {combined_text}
    """)
    return call_model(prompt, max_tokens=200)

def generate_follow_up_questions(summary_text):
    if not summary_text or not summary_text.strip():
        return "No summary available to generate follow-up questions."
    prompt = textwrap.dedent(f"""
        Based on the following summary, generate three clear follow-up analysis questions to explore the data further:

        Summary:
        {summary_text}

        Follow-up questions:
    """)
    return call_model(prompt, max_tokens=150)

def process_all_tables():
    combined_text = ""
    for cfg in TABLE_CONFIGS:
        label = cfg["table_label"]
        query = cfg["query"]
        print(f"\n🔄 Processing table: {label}")
        rows = fetch_data(query)
        if rows:
            formatted_rows = [", ".join(str(item) for item in row) for row in rows]
            table_text = f"{label} Data:\n" + "\n".join(formatted_rows) + "\n"
            combined_text += table_text
        else:
            combined_text += f"No data available from {label}.\n"

    summary = summarize_combined_data(combined_text) or "Summary not available."
    print(f"\n📢 Summary:\n{summary}")

    follow_up = generate_follow_up_questions(summary) or "Follow-up questions not available."
    print(f"\n❓ Follow-Up Questions:\n{follow_up}")
    return summary, follow_up

if __name__ == "__main__":
    process_all_tables()
