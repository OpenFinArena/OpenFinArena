# Financial Deep Forecasting (FinDeepForecast)

The current paradigm for evaluating Large Language Models (LLMs) and AI Agents in financial analysis is constrained by its reliance on **static, historical datasets**. This approach primarily assesses a model's capacity to interpret past events rather than forecast future outcomes. This methodological misalignment with real-world practice fails to simulate the **dynamic, looking-forward** environments that analysts and economists face. To address this critical gap, we introduce **FinDeepForecast**, a live benchmark for evaluating the **genuine financial forecasting capabilities** of LLMs and AI agents. It challenges models to make time-sensitive predictions on the future **financial metrics and ratios of listed companies from 9 global stock exchanges**, as well as **broader macroeconomic indicators across 8 countries/regions**. Crucially, the accuracy of these forecasts can only be verified by future outcomes, providing a dynamic and realistic assessment of model performance.

<p align="center">
  <a href="https://openfinarena.com/fin-deep-forecast/"><b>📊 Benchmark Page</b></a> |
  <a href=""><b>📑 Technical Report (Coming Soon)</b></a>
</p>

## Task

The task focuses on the forecast of corporate financial metrics or macroeconomic indicators. Formally, given a question `q` that queries the state of the world at a future time, the objective is for a method `M` to generate the answer `a` to the question `q`.

<div align="center">
<b>a = M (q)</b>
</div>

For example, "What is the estimated year-over-year GDP growth rate for China in 2025?".

## Participation
### Forecasting Question Suggestion

We welcome your contributions to our forecast queue in the FinDeepForecast Challenge. If you would like to suggest a forecasting question, please submit it using this [Google Form](https://docs.google.com/forms/d/e/1FAIpQLScTzJRbkPetxTB76cMuxWrbF4GEyaSOSFrKnBGJKmFmmRmCYQ/viewform). The OpenFinArena team will evaluate each suggestion and notify you if it is accepted.

### Service Registration or Prediction Submission
#### Online API Service Registration
If you are willing to add your model to the scheduled forecasts, please submit the necessary information via the [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSc-Z8Pbup--Jk5gwUKz45uoaHio_3qkLzSq4VSJMkDzve6cLQ/viewform).

#### Offline Prediction Submission

If you are interested in participating in the ongoing forecasts offline, please download the questions from [Hugging Face](). Once you complete the predictions locally, please send your results in **JSON format** to OpenFinArena@gmail.com.

Example:
```
[
  {
    "id": "1233",
    "prediction": "23.4"
  },
  {
    "id": "4561",
    "prediction": "4.5%"
  }
]
```

Please use the following subject in your email: **FinDeepForecast-{Method Name}-{Method Type}-{Team Name}-{Organization}**.

The **Method Name** should be a unique name for your system/method, not just the name of the base model used (e.g., "MyAwesomeMethod", "FinAgent-v2", not "GPT-4").

The **Method Type** might be "Thinking", "Thinking + Search", "Deep Research" or other types that can best explain the type of your method.

If the method type cannot be confirmed or you choose not to disclose it, please indicate "Other". If you have a dedicated logo for your Organization, please attach the logo in the size of 100x100, such as <img src="https://openfinarena.com/images/logo/chatgpt.svg" alt="OpenAI Logo" style="display:inline-block; margin:0;"> for OpenAI, which will be presented in the leaderboard.