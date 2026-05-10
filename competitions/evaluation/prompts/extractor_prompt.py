import json
from typing import List

RAI_PROMPT = """Extract data from a markdown table and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
// The final array will contain an object for each field/year combination found.
[
  {{"name": "<field_name>", "year": <year>, "value": "<extracted_value_or_N/A>"}},
  ...
]
```

## Processing Rules
- For each `Required Field`, create a separate JSON object for **every year** available in the input data.
- Extract object by checking first column (Field name) and year header.
- Match values in markdown table headers that may contain typos if they are intended to mean the same thing.
- If a required field is missing or its Value cell is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any table rows that are not in the required fields list.
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


RAI_PROMPT_GENERAL = """Extract data from markdown content and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
// The final array will contain an object for each field/year combination found.
[
  {{"name": "<field_name>", "year": <year>, "value": "<extracted_value_or_N/A>"}},
  ...
]
```

## Processing Rules
- For each required field and year combination, find its corresponding value within the markdown content.
- Match field names and years even if they contain typos or slight variations.
- If a value for a required field-year combination cannot be found or is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any information not related to the required fields.
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


R2_PROMPT = """Extract data from a markdown table and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
[
  {{"name": "field1", "value": "<extracted_value_or_N/A>"}},
  {{"name": "field2", "value": "<extracted_value_or_N/A>"}}
]
```

## Processing Rules
- Match rows by the the first column (Field name).
- Match values in markdown table rows that may contain typos if they are intended to mean the same thing.
- If a required field is missing or its Value cell is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any table rows that are not in the required fields list.
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


R2_PROMPT_GENERAL = """Extract data from markdown content and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
[
  {{"name": "field1", "value": "<extracted_value_or_N/A>"}},
  {{"name": "field2", "value": "<extracted_value_or_N/A>"}}
]
```

## Processing Rules
- For each required field, find its corresponding value within the markdown content.
- Match field names even if they contain typos or slight variations.
- If a value for a required field cannot be found or is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any information not related to the required fields.
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


R3_PROMPT = """Extract data from a markdown table and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
// The final array will contain an object for each field/year combination found.
[
  {{"name": "<field_name>", "year": <year>, "value": "<extracted_value_or_N/A>"}},
  ...
]
```

## Processing Rules
- For each `Required Field`, create a separate JSON object for **every year** available in the input data.
- Extract object by checking first column (Field name) and year header.
- Match values in markdown table headers that may contain typos if they are intended to mean the same thing.
- Compose value with multiplier(skip if N/A) and currency(skip if N/A).
- If a required field is missing or its Value cell is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any table rows that are not in the required fields list.
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


R3_PROMPT_GENERAL = """Extract data from markdown content and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
// The final array will contain an object for each field/year combination found.
[
  {{"name": "<field_name>", "year": <year>, "value": "<extracted_value_or_N/A>"}},
  ...
]
```

## Processing Rules
- For each required field and year combination, find its corresponding value within the markdown content.
- Match field names and years even if they contain typos or slight variations.
- Compose the final value with its multiplier and currency, if they are present.
- If a value for a required field-year combination cannot be found or is empty, output "N/A" as the value.
- If a required field appears multiple times, use the first occurrence.
- Ignore any information not related to the required fields.
- Return only the JSON array; no extra text.

## Required Fields (maintain this exact order)
{fields}

## Input Data

```md
{input_markdown}
```"""


R4_PROMPT = """Extract data from a markdown table and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
[
  {json_structure}
]
```

## Processing Rules
- Preserve the Value text as-is.
- Return only the JSON array; no extra text.

## Input Data

```md
{input_markdown}
```"""


R4_PROMPT_GENERAL = """Extract data from markdown content and convert it to a structured JSON array.

## Input Format
- Markdown content enclosed in "```md" code blocks

## Output Format
Return a JSON array of objects with the following structure:
```json
[
  {json_structure}
]
```

## Processing Rules
- Map the data from the markdown content to the JSON structure provided in the Output Format.
- Preserve the extracted text as-is.
- Return only the JSON array; no extra text.

## Input Data

```md
{input_markdown}
```"""


SPLIT_PROMPT = """Analyze the provided content and extract it into predefined subsections based on the fields they contain.

## Required Subsections
The content should be divided into the following logical sections:

{subsections}

## Output Format
Return a JSON array of objects, with one object for each required subsection.
```
[
    {{
        "subsection_no": "<e.g., S1.1>",
        "subsection_header": "<The most relevant header text found near the content, or an empty string if none is found>",
        "section_header": "<The higher-level header text found near the content, or an empty string>",
        "subsection_content": "<All text and markdown tables associated with this subsection's fields>",

    }},
    ...
]
```

## Processing Rules
- For each required subsection, locate the block of text and tables in the input that contains its associated fields.
- A subsection's content begins where its fields first appear and ends where the fields for the next subsection begin, or at the end of the document.
- Capture all content (paragraphs, tables, lists) that belongs to a subsection.
- If the same subsection occurs multiple times, create a separate item in the array for each occurrence.
- The `subsection_header` and `section_header` are secondary. Find the closest markdown header texts that act as titles for the located content. If no clear headers exist for the content block, return an empty string for them.
- Return the `subsection_content` as-is, preserving the original markdown.
- Return `subsection_header` and `section_header` without hashtags.

## Input Data

```md
{input_markdown}
```"""

def compose_fields(fields: List[str]):
    return '\n'.join(f'- {f}' for f in fields)


def compose_json_structure(fields: List[str]):
    json_dict = {f: '<extracted_value_or_N/A>' for f in fields}
    return json.dumps(json_dict)


def compose_subsection_structure(subsection_no: str, subsection_name: str, subsection_fields: List[str]) -> str:
    fields_info = ', '.join([f'`{f}`' for f in subsection_fields])
    template = f'- {subsection_no}: {subsection_name}. This subsection contains information related to: {fields_info}.'
    return template


def compose_report_desp(subsection_cfg: dict):
    subsections = []
    for subsection_no, subsection_meta in subsection_cfg.items():
        subsections.append(
            compose_subsection_structure(subsection_no, subsection_meta['name'], subsection_meta['fields'])
        )
    return '\n'.join(subsections)
