import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma 
# from langchain_community.vectorstores import Chroma

# ==========================
# CONFIG
# ==========================
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL_NAME = "mistralai/mistral-7b-instruct:free"
DB_PATH = "./chroma"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://www.menstrual-health-chatbot.com",
    "X-Title": "menstrual-health-chatbot",
    "Content-Type": "application/json",
}

# ==========================
# VECTOR RETRIEVAL
# ==========================
def retrieve_context(query, k=4):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2")

    vectordb = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    docs = vectordb.similarity_search(query, k=k)

    context_text = "\n\n".join(
        f"- {doc.page_content}" for doc in docs
    )

    return context_text, docs


# ==========================
# OPENROUTER CALL
# ==========================
def call_openrouter(prompt):
    payload = {
        "model": MODEL_NAME,
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# ==========================
# MAIN LOOP
# ==========================
def main():
    print("🌙 Luna RAG system ready. Type 'exit' to quit.")

    while True:
        user_message = input("\nUser: ")
        if user_message.lower() == "exit":
            break

        # Example cycle info (replace with real backend output)
        cycle_info_text = (
            "Cycle context: The user is currently in her 25th day of the cycle, corresponding to the luteal phase"
        )

        retrieved_context, source_docs = retrieve_context(user_message)

        # ===== Final Prompt (Persona + RAG + Cycle Data) =====
        final_prompt = f"""
You are Luna, a compassionate AI health companion specializing in menstrual health and hormonal science.

Your role:
- Validate the user's experience emotionally
- Explain how symptoms may relate to hormonal cycles
- Be scientifically grounded but non-diagnostic
- Warm, supportive, and concise

{cycle_info_text}

Relevant background knowledge:
{retrieved_context}

User message:
{user_message}
"""

        try:
            answer = call_openrouter(final_prompt)

            print("\nAssistant:")
            print(answer)

            print("\nSources:")
            for doc in source_docs:
                print(f"- {doc.metadata.get('source')}")

        except Exception as e:
            print("❌ Error:", str(e))


if __name__ == "__main__":
    main()
