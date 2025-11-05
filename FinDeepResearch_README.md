# Financial Deep Research (FinDeepResearch)

**Corporate financial analysis** is a critical process for understanding a listed company's business health, financial performance, and stock valuation, ultimately guiding investment decisions. 
Professional analysts typically execute a comprehensive and rigorous workflow, beginning with the retrieval and recognition of relevant data from diverse sources, such as corporate disclosures, financial news, historical stock prices, and market indexes. 
The data is then used for metric calculation, followed by strategic summarization and interpretation, aggregating in the generation of a research report to inform decision-making. 
**FinDeepResearch** is specifically designed to emulate this professional pipeline to **conduct corporate financial analysis following an expert-designed analytical structure to generate a rigorous, structured report**. 
Comprising **64 listed companies from 8 financial markets** and a total of **15,808 grading items**, FinDeepResearch provides a robust framework for evaluating the ability of advanced AI techniques (e.g., deep research agents) to generate corporate financial analysis reports that simultaneously adhere to a **systematic analytical structure (rigor)** and produce **specific, accurate claims (precision)**.

<p align="center">
  <a href="https://openfinarena.com/fin-deep-research"><b>📊 Benchmark Page</b></a> |
  <a href="https://www.arxiv.org/abs/2510.13936"><b>📑 Arxiv Paper</b></a> |
  <a href="https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/input_analytical_structure.csv"><b>🤗 Dataset</b></a>
</p>


## Task
The task aims to generate a comprehensive research report for a listed company by adhering to an expert-designed analytical framework and synthesizing heterogeneous financial data from diverse web sources, including corporate disclosures, financial news, stock prices, and market indices.

Formally, given a research task instruction `𝑖` with a desired analytical structure `S`, a method `M` is required to produce a research report `R` strictly following the analytical structure `𝑆`.

<div align="center">
<b>R = M (𝑖, 𝑆)</b>
</div>

<div align="center">
  <img src="public/images/findeepresearch_overview.png" width="100%" alt="FinDeepResearch Overview" />
</div>

## Samples

| Market | Company Name | Input Analytical Structure | Sample Output Report |
|---|---|---|---|
| 🇺🇸 US | Nvidia | [test001.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test001.md) | [test001-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test001-report.md) |
| 🇬🇧 UK | Shell PLC | [test012.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test012.md) | [test012-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test012-report.md) |
| 🇨🇳 CN | 宁德时代新能源科技股份有限公司 | [test018.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test018.md) | [test018-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test018-report.md) |
| 🇭🇰 HK | 腾讯 | [test025.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test025.md) | [test025-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test025-report.md) |
| 🇸🇬 SG | Food Empire Holdings Ltd | [test039.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test039.md) | [test039-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test039-report.md) |
| 🇦🇺 AU | CSL Ltd | [test043.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test043.md) | [test043-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test043-report.md) |
| 🇲🇾 MY | IJM Corporation Berhad | [test051.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test051.md) | [test051-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test051-report.md) |
| 🇮🇩 ID | PT Garudafood Putra Putri Jaya Tbk | [test061.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Analytical%20Structure/test061.md) | [test061-report.md](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/Sample%20Output%20Reports/test061-report.md) |

## Dataset

**Selected companies:**
<ul>
    <li><strong>4 Languages:</strong> English, Simplified Chinese, Traditional Chinese and Indonesian Bahasa</li>
    <li><strong>8 Markets:</strong> United States (US), United Kingdom (UK), China (CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID)</li>
    <li><strong>10 Industries (BICS):</strong> Communications, Consumer Discretionary, Consumer Staples, Energy, Health Care, Industrials, Materials, Real Estate, Technology, and Utilities</li>
    <li><strong>64 Companies:</strong> 8 companies from each market</li>
</ul>

The whole FinDeepResearch dataset for evaluation can be downloaded via the [🤗link](https://huggingface.co/datasets/OpenFinArena/FinDeepResearch/blob/main/input_analytical_structure.csv).