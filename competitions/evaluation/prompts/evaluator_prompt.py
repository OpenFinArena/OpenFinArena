# Interpretation
I_PROMPT = """You are a financial competition judge currently scoring a contestant's submission analyzing a company's annual report. Please score the answer based on the following sections: 'Question', 'Standard Answer', 'Marking Criterion', and 'Contestant Analysis and Answer'. The output format should be a list of JSON objects to indicate the mark awarded for each marking criteria. The JSON will have four fields: 'criteria_name', 'mark', 'full_mark' and 'reason'. For each 'mark' given, be careful not to exceed the 'full_mark' available for the marking criteria. Please strictly compare against the 'Standard Answer' and evaluate based on the 'Marking Criterion' for financial analysis accuracy, quantitative reasoning, and business insight demonstration.


### Question

{question}

### Standard Answer

{standard_answer}

### Marking Criteria(Total: 10 points)

{marking_criteria}

### Contestant Analysis and Answer

{contestant_answer}"""


# Recognition
R_PROMPT = """You will be given {num} pairs of [question]s, [extracted_answer]s and [correct_answer]s. You need to go through each of the pairs, compare [extracted_answer] with the [correct_answer], and then assign a binary score. Your response must be a list of JSON arrays. The JSON will have keys `id` and `score`, where `score` is an integer in [0, 1] based on the following rules:


Rubric:
    * Give a score of 1 if [extracted_answer] is equivalent to [correct_answer], including:
        - Exact matches
        - Exact absolute values (e.g., "-1000" = "1000")
        - Equivalent numerical representations (e.g., "1,000" = "1 thousand")
        - Equivalent unit representations (e.g., "0.2" = "20%")
        - Semantically equivalent expressions (e.g., "apple tree" = "the tree of apple")
        - Minor formatting or phrasing differences that don't change the core meaning
        - If the [extracted_answer] is more specific than the [correct_answer] (e.g., includes a month and day when only the year was asked for), give 1 as long as the core answer is correctly present and the added specificity does not create inconsistency or ambiguity.
        - If the [extracted_answer] uses an abbreviation, alias, or widely recognized shorthand for the entity or value referenced in the [correct_answer] (or vice versa), and there is no ambiguity about which entity or value is meant, score as 1. This includes common short names for organizations, companies, or products.
    * Give a score of 0 if the extracted answer differs in meaning from the correct answer, contains inconsistencies, or is ambiguous.


    ### Example Start ###
    [question1]: value of 'Revenue'
    [extracted_answer1]: 510.4 Millions GBP
    [correct_answer1]: 510400000 GBP

    [question2]: value of 'Company Name'
    [extracted_answer2]: Chemring Group PLC
    [correct_answer2]: Chemring

    [question3]: value of 'Core Values'
    [extracted_answer3]: Safety, Innovation, Excellence
    [correct_answer3]: Safety, Excellence, Innovation

    [
        {{"id": 1, "score": 1}},
        {{"id": 2, "score": 1}},
        {{"id": 3, "score": 1}}
    ]
    ### Example End ###


{input}
"""


# Calculation
C_PROMPT = """You will be given 1 pairs of [question], [extracted_answer] and [correct_answer]. You need to compare [extracted_answer] with the [correct_answer], and then output JSON object with `score` in [0, 1] based on the following rules:


Rubric:
    * Give a score of 1 if [extracted_answer] is equivalent to [correct_answer], including:
        - Exact matches
        - Exact absolute values (e.g., "-1000" = "1000")
        - Equivalent numerical representations (e.g., "1,000" = "1 thousand")
        - Equivalent unit representations (e.g., "0.2" = "20%")
        - Minor formatting or phrasing differences that don't change the core meaning
        - Values within acceptable rounding margins for numerical problems. You should use `compare_within_tolerance` tool for help.
    * Give a score of 0 if the extracted answer differs in meaning from the correct answer, contains inconsistencies, or is ambiguous.


{input}
"""


# Abstraction
A_PROMPT = """Based on the list of close-ended 'yes' or 'no' questions, generate a JSON with key 'answers', which is a list of strings that determines whether the provided text contains sufficient information to answer EACH question.
Answers should STRICTLY be either 'yes' or 'no'.
Answer 'yes' if the text provides information that is reasonably synonymous with, paraphrases, or strongly implies the answer to a question.
Answer 'no' if there is not enough directly stated or reasonably inferred information.
**
IMPORTANT: Please make sure to only return in JSON format, with the 'answers' key as a list of strings.

Example:
Example Text: Mario and Luigi were best buds but since Luigi had a crush on Peach Mario ended up killing him.
Example Questions: ["Are there enough information about Luigi and Mario?"]
Example Answers:
{{
    "answers": ["yes"]
}}

The length of 'answers' SHOULD BE STRICTLY EQUAL to that of questions.
===== END OF EXAMPLE ======

Text:
{text}

Questions:
{questions}

JSON:"""


def compose_extraction_batch_input(items: list) -> str:
    r = '\n\n'.join(
        f'[question{idx}]: {i["question"]}\n'
        f'[extracted_answer{idx}]: {i["prediction"]}\n[correct_answer{idx}]: {i["gold"]}'
        for idx, i in enumerate(items, start=1)
    )
    return r


def compose_extraction_single_input(item: dict) -> str:
    return f'[question]: {item["question"]}\n[extracted_answer]: {item["prediction"]}\n[correct_answer]: {item["gold"]}'
