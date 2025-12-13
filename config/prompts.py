PARSE_QUERY_PROMPT = """Extract the city name from this travel query.

User query: "{user_query}"

Instructions:
- Normalize city names (NYC to New York, Paras to Paris)
- Handle misspellings and variations
- Extract date/time references if present
- If no city is clearly mentioned, set confidence < 0.5

Examples:
"Tell me about Paras" -> city_name: "Paris", confidence: 0.9
"What's the weather like in NYC next week?" ->  city_name: "New York", date_reference: "next week"
"Japan's capital" -> city_name: "Tokyo", confidence: 0.95
"""


VECTOR_SUMMARY_PROMPT = """Using ONLY the information provided below, write a comprehensive summary about {city}.

Information from knowledge base:
{context}

Write a well-structured summary (3-4 paragraphs) covering the most important aspects of this city.
Do not add any information not present in the provided context."""


WEB_SUMMARY_PROMPT = """You are writing a city summary based ONLY on the search results provided below.

CRITICAL RULES:
- Use ONLY information from the provided search results below
- Do NOT add any information from your training data or general knowledge
- If something is not mentioned in the search results, do not include it
- Write in a clear, informative, and engaging style
- Aim for 3-4 well structured paragraphs
- Focus on the most important and interesting aspects mentioned in the sources

City: {city}

Search Results:
{context}

Write a comprehensive summary of {city} using ONLY the information provided above."""

