# Financial Document Research (FinDocResearch)

The accurate and timely interpretation of corporate financial disclosures, such as financial statements, is critical for informed decision-making (e.g., investment) in finance.
However, the complexity and knowledge-intensive nature of these documents often render their analysis a time-consuming and laborious process. The application of Artificial Intelligence (AI) techniques presents a transformative opportunity to automate this process to provide actionable intelligence from these documents.
**Financial Document Research (FinDocResearch)** is therefore designed to evaluate the capabilities of advanced AI techniques, such as LLMs and Agents, in **comprehensively analyzing a listed company's multi-year annual reports and producing a rigorous, structured research report**.
FinDocResearch features **80 listed companies** from **8 financial markets**, including United States (US), United Kingdom (UK), China(CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID).
By simulating the workflows of professional research analysts, FinDocResearch establishes a novel benchmark for assessing cross-document research methodologies in financial AI.

<p align="center">
  <a href="https://openfinarena.com/fin-doc-research"><b>📊 Project Website</b></a> |
  <a href="https://finddr2025.github.io/"><b>🪐 Grand Challenge @ ICAIF 25</b></a> |
  <a href="https://www.preprints.org/manuscript/202601.0702"><b>📑 Technical Report </b></a> |
  <a href="https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/dataset.csv"><b>🤗 Dataset</b></a>
</p>

## Task

FinDocResearch requires methods to generate a rigorous, structured research report based solely on a pair of multi-year annual reports of a listed company. The use of external data sources other than the provided annual reports, such as websites, news articles, and financial data providers, is strictly prohibited.
Formally, given two annual reports `(d1, d2)` of a listed company and a desired report structure `S`, a method `M` is required to produce a research report `R` strictly following the report structure `𝑆`.

<div align="center">
<b>R = M (d1, d2, 𝑆)</b>
</div>

## Desired Report Structure
The desired structure of the research report are as follows:
<ul>
  <li><strong>Company Overview:</strong> This section provides a concise overview of the company, including:
    <ul>
      <li>Basic Information</li>
      <li>Core Competencies</li>
      <li>Mission &amp; Vision</li>
    </ul>
  </li>

  <li><strong>Financial Performance:</strong> This section presents a detailed analysis of the company's financial health, including:
    <ul>
      <li>Income Statement</li>
      <li>Balance Sheet</li>
      <li>Cash Flow Statement</li>
      <li>Key Financial Ratios</li>
      <li>Operating Performance</li>
    </ul>
  </li>

  <li><strong>Business Analysis:</strong> This section provides a summary and analysis of a company's business performance and strategies, including:
    <ul>
      <li>Profitability Analysis</li>
      <li>Financial Performance Summary</li>
      <li>Business Competitiveness</li>
    </ul>
  </li>

  <li><strong>Risk Factors:</strong> This section identifies and discusses the principal risks the company faces, including:
    <ul>
      <li>Market Risks</li>
      <li>Operational Risks</li>
      <li>Financial Risks</li>
      <li>Compliance Risks</li>
    </ul>
  </li>

  <li><strong>Corporate Governance:</strong> This section outlines the company's governance framework, including:
    <ul>
      <li>Board Composition</li>
      <li>Internal Controls</li>
    </ul>
  </li>

  <li><strong>Future Outlook:</strong> This section provides management's projections and strategic plans for the future, including:
    <ul>
      <li>Strategic Direction</li>
      <li>Challenges and Uncertainties</li>
      <li>Innovation and Development Plans</li>
    </ul>
  </li>
</ul>

For a more detailed overview of the structure, please refer to this [link](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/desired_report_structure.md).

## Samples

| Market | Company Name | Input Annual Reports | Sample Output Report |
|--------|-------------|---------------------|---------------------|
| 🇺🇸 US | Nvidia | [NVIDIA_2024.pdf](https://s201.q4cdn.com/141608511/files/doc_financials/2024/q4/1cbe8fe7-e08a-46e3-8dcc-b429fc06c1a4.pdf)<br>[NVIDIA_2023.pdf](https://s201.q4cdn.com/141608511/files/doc_financials/2023/q4/4e9abe7b-fdc7-4cd2-8487-dc3a99f30e98.pdf) | [sample001.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample001.md) |
| 🇬🇧 UK | Chenming Group PLC | [Chenming Group_2024.pdf](https://www.chemring.com/~/media/Files/C/Chemring-V3/docs/chemring-annual-report-and-accounts-dec-2024.pdf)<br>[Chenming Group_2023.pdf](https://www.chemring.com/~/media/Files/C/Chemring-V3/docs/annual-report-and-accounts-jan-2024.pdf) | [sample002.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample002.md) |
| 🇨🇳 CN | 宁德时代新能源科技股份有限公司 | [宁德时代新能源科技股份有限公司_2024.pdf](https://www.catl.com/uploads/1/file/public/202503/20250317094543_6ig9e0mwng.pdf)<br>[宁德时代新能源科技股份有限公司_2023.pdf](https://www.catl.com/uploads/1/file/public/202403/20240321205248_hda9h48qci.pdf) | [sample003.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample003.md) |
| 🇭🇰 HK | 腾讯 | [腾讯控股有限公司_2024.pdf](https://static.www.tencent.com/uploads/2025/04/08/0706a9085e70140122364ded872455ca.pdf)<br>[腾讯控股有限公司_2023.pdf](https://static.www.tencent.com/uploads/2024/04/08/4e1745d32fbe5e8145a82bc4c26bc8aa.pdf) | [sample004.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample004.md) |
| 🇸🇬 SG | Food Empire Holdings Ltd | [Food Empire Holdings Limited_2024.pdf](https://investor.foodempire.com/newsroom/20250401_074656_F03_8II6R0N45HT7UQ0C.1.pdf)<br>[Food Empire Holdings Limited_2023.pdf](https://investor.foodempire.com/newsroom/20240403_075800_F03_60TXJJB5F7S9I2N1.1.pdf) | [sample005.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample005.md) |
| 🇦🇺 AU | CSL Ltd | [CSL Limited_2024.pdf](https://www.csl.com/-/media/shared/documents/annual-report/csl-annual-report-2024.pdf)<br>[CSL Limited_2023.pdf](https://www.csl.com/-/media/shared/documents/annual-report/csl-annual-report-2023.pdf) | [sample006.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample006.md) |
| 🇲🇾 MY | IJM Corporation Berhad | [IJM Corporation Berhad_2024.pdf](https://www.ijm.com/sites/default/files/annualreport-pdf/arc_ar_2024.pdf)<br>[IJM Corporation Berhad_2023.pdf](https://www.ijm.com/sites/default/files/annualreport-pdf/arc_ar_2023_0.pdf) | [sample007.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample007.md) |
| 🇮🇩 ID | PT Garudafood Putra Putri Jaya Tbk | [PT Garudafood Putra Putri Jaya Tbk_2024.pdf](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_EREP/202503/e97dd88412_e32c9e893f.pdf)<br>[PT Garudafood Putra Putri Jaya Tbk_2023.pdf](https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_EREP/202404/40866dab6e_41883aa0ed.pdf) | [sample008.md](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/Sample%20Output%20Reports/sample008.md) |



## Dataset

**Selected listed companies and annual reports:**
<ul>
  <li><strong>4 Languages:</strong> English, Simplified Chinese, Traditional Chinese and Indonesian Bahasa</li>
  <li><strong>8 Markets:</strong> United States (US), United Kingdom (UK), China (CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID)</li>
  <li><strong>10 Industries (BICS):</strong> Communications, Consumer Discretionary, Consumer Staples, Energy, Health Care, Industrials, Materials, Real Estate, Technology, and Utilities, etc.</li>
  <li><strong>80 Companies:</strong> 10 companies from each market</li>
  <li><strong>160 Reports:</strong> 2 annual reports (i.e., 2023 and 2024) for each selected company are provided</li>
</ul>

| Market | No. of Companies | No. of Documents | Max No. of Pages per Document | Min No. of Pages per Document | Average No. of Pages per Document | Examples |
|--------|------------------|------------------|-------------------------------|-------------------------------|-----------------------------------|----------|
| 🇺🇸 US | 10 | 20 | 444 | 82 | 178 | Williams-Sonoma Inc, UnitedHealth Group Incorporated |
| 🇬🇧 UK | 10 | 20 | 481 | 105 | 235 | Shell PLC, Unilever PLC |
| 🇨🇳 CN | 10 | 20 | 353 | 143 | 225 | 上汽集团股份有限公司, 中国电信股份有限公司 |
| 🇭🇰 HK | 10 | 20 | 353 | 127 | 236 | 美团, 中国海洋石油 |
| 🇸🇬 SG | 10 | 20 | 268 | 136 | 216 | IHH Healthcare Berhad, Raffles Medical Group Ltd |
| 🇦🇺 AU | 10 | 20 | 254 | 79 | 139 | BHP Group Ltd, Metcash Ltd |
| 🇲🇾 MY | 10 | 20 | 280 | 132 | 200 | Far East Holdings Berhad, UOA Development Berhad |
| 🇮🇩 ID | 10 | 20 | 599 | 204 | 383 | PT Harum Energy Tbk, PT Bumi Serpong Damai Tbk |

The whole FinDocResearch dataset for evaluation can be downloaded via the [🤗link](https://huggingface.co/datasets/OpenFinArena/FinDocResearch/blob/main/dataset.csv).

## Evaluation

### Env Preparation

```bash
conda create -n findocresearch python=3.12
conda activate findocresearch
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### How to Evaluate a Prediction

The evaluation process consists of 2 main steps
1. Context extraction:
   1. Extracts structured information from markdown files into a standardized JSON format that can be compared against ground truth data.
   2. Format score assessing section headers, subsection headers and markdown tables is given in the end.
2. Evaluation:
   1. Evaluates extracted predictions against ground truth data using different scoring methods based on question types.
   2. Content scores of 4 categories are given:
      - **Overall**: The final weighted score across all companies and question types
      - **Country-specific scores**: Individual scores for each market/location:
        - USA, UK, China, Hong Kong, Australia, Singapore, Malaysia, Indonesia
      - **Section-specific scores**: Individual scores for each section:
        - S1, S2, S3, S4, S5, S6
      - **Level-specific scores**: Individual scores for each level:
        - level1: Recognition
        - level2: Calculation
        - level3: Abstraction
        - level4: Interpretation

### Ground Truth

Ground truth files are **not provided** in this repository due to future competition constraints.

To run the evaluation script, place your own sample markdown files under:

```
data/ground_truth/findocresearch_track/markdown/
```

Each file should correspond to a company in the dataset (e.g., `test001.md`). With sample files in place, the evaluation pipeline will be fully executable.

### Usage

```bash
PYTHONPATH='.' python evaluation/run.py \
    --track findocresearch \
    --prediction_folder data/predictions/samples/markdown
```
**Parameters**:
- `--track`: `findocresearch` or `findeepresearch`
- `--prediction_folder`: Path to folder containing markdown prediction files. Each file should be the generated research report in markdown format following the analytical structure specified for that company, with the file name matching the input name exactly (e.g., `test001.md`).
- `--model`: llm model to use for extraction (default: `gpt-4.1`)
- `--extraction_only`: If to skip evaluation and only run extraction
- `--evaluation_only`: If to skip extraction and only run evaluation
- `--overwrite`: If to overwrite existing results

**Env Variables**:
- `TRACE_ENABLED`: Set to `true` to enable llm prompt and response persistence for debugging purpose
