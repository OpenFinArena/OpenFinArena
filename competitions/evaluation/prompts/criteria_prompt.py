CRITERIA_PROMPT = """As a financial professor, please create marking criteria for your standard answer. The total points should be 10 points:

Your standard answer:

<question>{question}</question>

<answer>{answer}</answer>

List your marking criteria in clear points and state clearly how to award a point. Wrap your response in <marking> block"""


S_Q_PROMPT = """Based on the given text, generate {min_num} to {max_num} closed-ended questions that can be answered with either a 'yes' or 'no'.
The questions generated should ALWAYS contain sufficient information to result in a 'yes' based on the given text.

** IMPORTANT
Only return a JSON with a 'questions' key, which is a list of strings.
The questions have to be STRICTLY closed ended.
The given text should be able to answer 'yes' for each question.
**
Text:
{input_text}

JSON:
"""


S_Q_PROMPT_NEWS = """Your task is to generate {min_num} to {max_num} closed-ended questions based on a provided set of news snippets.

The input text contains one or more news snippets, each with a 'Title' and a 'Description'. You must synthesize information from ALL available snippets to formulate your questions.

Every question you create must be answerable with a definitive 'yes' based on the information present in the text.

**Guidelines:**
1.  **'Yes' Answers Only:** The information in the provided snippets MUST support a 'yes' answer for every question.
2.  **Strictly Closed-Ended:** Questions must be phrased to be answerable with only 'yes' or 'no'.
3.  **Synthesize Information:** Where possible, create questions that combine facts from multiple titles and descriptions.
4.  **JSON Output:** Return ONLY a single JSON object with a key named "questions", which contains a list of the question strings. Do not include any other text or explanations.

**News Snippets:**
{input_text}

**JSON Output:**
"""
