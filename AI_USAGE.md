# AI Usage Disclosure

## AI-Assisted Development

This project was developed with AI assistance (Claude/Cursor) for:

- **Code generation**: FastAPI backend, retriever logic, memory system, and frontend UI
- **FAQ dataset creation**: Synthetic FAQ entries modeled after typical vendor services portals
- **Architecture design**: System design decisions for retrieval, memory, and prompt engineering

## AI in Production

The chatbot itself uses **OpenAI GPT-4o-mini** for:

- Generating natural language answers grounded in FAQ data
- Following strict prompt constraints to prevent hallucination
- Routing authentication queries to human support

A **template-based fallback** is included for when the LLM is unavailable, ensuring the system always functions.

## What AI Does NOT Do

- No real Epic Systems data is used
- No real user data is stored or processed
- The system does not make autonomous decisions — all answers are grounded in the FAQ dataset
- Authentication/login requests are always routed to human support, never answered with generated steps

## Retrieval vs. Generation

The system follows a **Retrieval-Augmented Generation (RAG)** pattern:
1. User query is matched against FAQ entries using keyword scoring
2. Top matches are injected into the LLM prompt as context
3. The LLM generates a response constrained to those FAQ entries
4. Sources are always cited in the response
