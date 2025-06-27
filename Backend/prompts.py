# prompts.py

PROMPT_TEMPLATES = {
    "risk_identification": [
        # Prompt 1: Focus on strict JSON output for risk analysis
        (
            "Your task is to analyze the following legal text and extract specific information in JSON format ONLY. "
            "Do not include any conversational text, explanations, or additional formatting outside the JSON object.\n"
            "Analyze for vague language, biased terms, unfair clauses, and potential liabilities. "
            "Provide a JSON object with these exact keys:\n"
            "1. 'risk_level': (string) 'High', 'Medium', 'Low', or 'Neutral'.\n"
            "2. 'simplified_explanation': (string) A concise, plain language explanation of the identified risks or key points.\n"
            "3. 'inter_clause_dependencies': (list of objects) A list where each object has 'clause_id' (string) and 'dependency_type' (string, e.g., 'modifies', 'contradicts', 'reinforces'). Provide an empty list if no dependencies.\n\n"
            "Legal Text Chunk to Analyze: \"\"\"{{chunk}}\"\"\""
            "\n\nOutput only the JSON object."
        ),
        # Add more prompts here for different risk analysis approaches:
        # Example Prompt 2: More detailed risk breakdown
        # (
        #     "For the given legal text, identify all potential legal risks, categorize them (e.g., contractual, regulatory, financial), "
        #     "and suggest a preliminary severity (low, medium, high). Provide this in a JSON array of risk objects, "
        #     "each with 'category', 'description', and 'severity'.\n\nText: \"\"\"{{chunk}}\"\"\"\n\nJSON Output:"
        # ),
    ],
    "jargon_simplification": [
        # Prompt 1: Current jargon simplification prompt
        (
            "Rephrase the following legal text into plain English, explaining any complex jargon. "
            "Provide a real-world example if it helps clarity. Return the rephrased text.\n\n"
            "Legal Text Chunk: \"\"\"{{chunk}}\"\"\""
        ),
        # Add more jargon simplification prompts:
        # Example Prompt 2: Focus on specific legal terms glossary
        # (
        #     "List all specific legal terms found in the following text and provide a simple, one-sentence explanation for each. "
        #     "Format your output as a bulleted list of 'Term: Definition' pairs.\n\nText: \"\"\"{{chunk}}\"\"\""
        # ),
    ],
    "overall_summary": [
        # Prompt 1: Current overall summary prompt
        (
            "Provide a concise overall summary of the risks and key points identified in the document. "
            "Focus on the most critical aspects. The document's analyzed chunks yielded these key points:\n\n"
            "{{summary_parts}}\n\n"
            "Original document start (for context if needed):\n\n\"\"\"{{raw_text_snippet}}\"\"\""
        ),
        # Add more overall summary prompts:
        # Example Prompt 2: Executive summary with action items
        # (
        #     "Based on the following key points from a legal document analysis, provide an executive summary "
        #     "that highlights the main legal implications, the overall risk assessment, and any recommended next steps or actions required. "
        #     "Keep it under 150 words.\n\n"
        #     "Key Analysis Points: {{summary_parts}}\n\nExecutive Summary:"
        # ),
    ]
}