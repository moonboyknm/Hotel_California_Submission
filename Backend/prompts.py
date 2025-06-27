# prompts.py

PROMPT_TEMPLATES = {
    "risk_identification": [
        # Original Prompt 1: Focus on strict JSON output for risk analysis
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
        # New Prompts from your list - categorized under risk_identification
        # --- General Risk & Dependency Prompts ---
        (
            "Analyze this clause and assign it a risk level—Low, Medium, or High—based on ambiguity, potential liability, and bias:\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Given Clause A and Clause B, explain how they depend on or amplify each other’s risks:\n\n"
            "* Clause A: \"\"\"{{clause_a_text}}\"\"\"\n"
            "* Clause B: \"\"\"{{clause_b_text}}\"\"\""
        ),
        (
            "Scan this section (Clauses 1.1–1.5) and list any ‘red-flag’ clauses that could impose hidden obligations or carve-outs:\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Within the following excerpt, identify any combinations of clauses that, when interpreted together, create higher-than-apparent risk:\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "For each numbered clause below, output a JSON mapping to pixel-grid colors (Green/Yellow/Red) based on risk:\n\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Produce a list of directed edges showing which clauses reference or depend upon which others (e.g., “Clause 2 → Clause 5”).\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Does this provision introduce any unfair advantage or bias toward one party? Explain your reasoning.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Compare the risk profile of Clause X vs. Clause Y, and state which is riskier and why.\n\n"
            "* Clause X: \"\"\"{{clause_x_text}}\"\"\"\n"
            "* Clause Y: \"\"\"{{clause_y_text}}\"\"\""
        ),
        (
            "Given these five clauses with individual risk scores, generate a 2×3 pixel grid heatmap layout (with one blank pixel), labeling each pixel by clause number and color."
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "List every external statute or regulation this clause refers to, and flag if the references are ambiguous or outdated.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Identify all exception-type clauses (e.g., ‘unless’, ‘except if’) and assess whether they create loopholes.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Assign each clause a numeric risk score from 0–100, and briefly justify scores above 75.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "This clause refers to Clause 12, which itself refers to Clause 3. Unpack and explain the full chain of obligations:\n"
            "\"\"\"{{clause_12_text}}\"\"\" plus relevant text."
        ),
        (
            "Check this contract excerpt for contradictory clauses, and detail any conflicts found.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Highlight any clause that could behave differently under California vs. Delaware law, and explain potential divergence.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Rank these ten clauses from most to least critical, based on potential legal and financial impact.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Generate a checklist of five questions a human reviewer should ask when verifying the risk assessment of this section.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        # --- Prompts for Identifying Vague and Ambiguous Terms ---
        (
            "Analyze the provided legal clause for any vague or ambiguous terms. List each vague term found and explain why it is considered vague in this context, providing a plain language interpretation of its potential meanings. Use an objective and neutral tone.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Identify all instances of the words 'reasonable', 'material', 'substantially', 'promptly', and 'good faith' in the following contract excerpt. For each instance, determine if its usage introduces problematic ambiguity or serves a legitimate purpose (e.g., flexibility, risk allocation). Explain your determination.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Given the following legal text, identify any terms that are susceptible to 'borderline cases' or whose meaning is heavily 'a function of the circumstances'. For each identified term, provide a concise explanation of the ambiguity.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Extract all phrases that introduce an 'objective standard' or 'qualify' another phrase in the following legal document. For each, assess if the qualification is clear or if it introduces problematic vagueness.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        # --- Prompts for Recognizing Biased Language ---
        (
            "Review the following legal text for gender-biased language, specifically focusing on generic masculine pronouns ('he', 'his') and gendered nouns ('man', 'mankind', 'policeman'). List all instances found and suggest a gender-neutral alternative for each.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Analyze the provided policy for any language that might implicitly or explicitly project discriminatory distinctions based on gender, race, color, ethnic background, or handicap. If found, identify the problematic phrase and explain its potential impact on fairness or inclusion.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Rewrite the following legal paragraph to eliminate all forms of biased language, ensuring it is inclusive and gender-neutral. Focus on replacing gendered pronouns and nouns with appropriate alternatives.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        # --- Prompts for Characteristics of Complex Legal Structures (can identify structural "risks") ---
        (
            "Identify and explain the function of any 'preamble' or 'savings clause' present in the following bill draft. Assess whether these elements contribute to clarity or potential confusion for a non-expert audience.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Deconstruct the following complex legal sentence. Identify any 'conditional logic' (if-then statements) and 'nested dependencies' (clauses within clauses). Explain how these structures contribute to the sentence's overall complexity.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Analyze the provided legal document for structural elements that increase its length, wordiness, or technicality. Specifically, identify instances of excessive cross-references, redundant phrasing, or overly detailed definitions that could hinder comprehension for a general citizen.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        # --- Prompts for Identifying Inter-Clause Dependencies (can be seen as a form of risk discovery) ---
        (
            "For the following legal sentence, first segment it into individual clauses. Then, identify the grammatical relationship between each clause pair using dependency labels (e.g., 'conj:and', 'advcl', 'nsubj'). Present the relationships in a structured list.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Given the following contract excerpt, identify all instances where one clause governs or modifies another clause. For each identified dependency, specify the two clauses involved and describe the nature of their interrelation (e.g., 'Clause A sets a condition for Clause B').\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Extract all 'adverbial clauses' (advcl) from the provided legal text. For each, identify the main clause it modifies and explain how the adverbial clause impacts the obligations or rights defined in the main clause.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Analyze the following legal provision and its surrounding context. Identify any clauses that establish 'conditions precedent' or 'contingencies' that must be met before other obligations or rights become effective. Explain the dependency.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        # --- Prompts for Detecting Red-Flag Clauses ---
        (
            "Review the following contract for clauses that could be considered 'red flags' for a service provider client. Specifically look for provisions related to intellectual property transfer, payment safeguards, termination rights, liability limitations, and deliverable definitions. For each identified red flag, explain why it poses a risk.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Identify any clause in the provided agreement that could lead to a client taking on 'disproportionate risk', considering a typical small business operating in the technology sector. Explain what makes the risk disproportionate.\n"
            "\"\"\"{{chunk}}\"\"\""
        ),
        (
            "Extract all clauses related to 'limitation of liability' and 'indemnification' from the following contract. Assess whether these clauses