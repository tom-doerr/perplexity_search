"""System prompts for the Perplexity Search agent."""

SEARCH_AGENT_PROMPT = '''Create a powerful and efficient query for a technical search tool leveraging Perplexity AI, aiming to retrieve precise technical information, code examples, and documentation. Follow these steps to construct a well-structured search query:

1. **Define Search Query Parameters:** Provide a clear and concise search query focusing on the specific technical concept, problem, or functionality. Be as specific as possible to improve result relevance.

2. **Specify Result Type:** Indicate the desired type of results:
   - `"code"`: Primarily code examples and snippets.
   - `"docs"`: Primarily documentation and explanations.
   - `"mixed"`: A combination of code and documentation.

3. Refine your search by specifying filters such as programming language, framework, or date range. This helps narrow down the search space and retrieve more targeted results.

4. **Construct the Search Query:** Use the provided query as the base. Ensure the query is clear, concise, and focuses on the specific technical concept, problem, or functionality. If the query seems vague or too broad, consider ways to make it more specific based on the context provided.

5. **Specification of the Result Type:** Use the provided result_type as is. Do not modify or interpret it.

6. **Set the Maximum Number of Results:** Use the provided max_results value as is. Do not modify or interpret it.'''

def format_prompt(query: str, result_type: str = "mixed", max_results: int = 5, **filters) -> str:
    """
    Generate a technical search prompt.
    
    Args:
        query: The technical search query
        result_type: Type of results ("code", "docs", or "mixed")
        max_results: Maximum number of results
        **filters: Technical domain filters (language, framework, etc.)
    
    Returns:
        str: The formatted prompt
    """
    prompt_parts = [
        SEARCH_AGENT_PROMPT,
        f"\nQuery: {query}",
        f"Result Type: {result_type}",
        f"Max Results: {max_results}"
    ]
    
    if filters:
        filters_str = "\n".join(f"{k}: {v}" for k, v in sorted(filters.items()))
        prompt_parts.append(f"Filters:\n{filters_str}")
    
    return "\n".join(prompt_parts)
