import json
from .chatbot import get_ai_shopping_list

def get_structured_shopping_list(preferences, budget):
    prompt = f"""
You are an AI assistant helping roommates create a smart grocery list.

Here are their preferences: {preferences}
Their budget level: {budget}

Generate a shopping list grouped by category, with items and approximate prices.

Respond ONLY with valid JSON in the following format:
{{
  "categories": [
    {{
      "name": "Produce",
      "items": [
        {{"name": "Apples", "price": 40}},
        {{"name": "Tomatoes", "price": 30}}
      ]
    }},
    {{
      "name": "Dairy",
      "items": [
        {{"name": "Milk", "price": 50}}
      ]
    }}
  ]
}}

- Prices must be approximate INR integers.
- No explanations. No markdown. Only valid JSON.
"""

    raw_output = get_ai_shopping_list(prompt)

    try:
        if "```" in raw_output:
            raw_output = raw_output.split("```")[1].strip("json").strip()

        parsed = json.loads(raw_output)
        return parsed.get("categories", [])
    except Exception as e:
        return {
            "error": "AI response was not valid JSON.",
            "rawOutput": raw_output
        }
