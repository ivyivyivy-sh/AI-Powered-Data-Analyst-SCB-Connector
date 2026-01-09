# 🤖 AI Data Analyst V3 + SCB Connector

**An intelligent data analytics platform that bridges the gap between raw data repositories and actionable insights using Generative AI.**

---

## Overview
The **AI Data Analyst V3** is a modular Python application designed to act as an autonomous data agent. Unlike static dashboards, it utilizes **Google's Gemini LLM** to generate visualization code on demand, allowing users to query data in natural language.

Key innovation: This project integrates a custom **REST API Connector** for [Statistics Sweden (SCB)](https://www.scb.se/), enabling direct ingestion of live government demographics and economic data, alongside robust handling of local CSV files.

## Key Features

### 1. Multimodal "Reasoning Engine"
* **Metadata-Only Analysis:** To ensure privacy and scalability, only column schemas (not rows) are sent to the LLM.
* **Code Generation:** The AI writes, sanitizes, and executes **Plotly** Python code dynamically.
* **Automated Insights:** Generates qualitative business summaries to accompany quantitative charts.

### 2. Live SCB API Connector
* **Custom JSON Parser:** Flattens SCB's complex hierarchical JSON-POST response into clean Pandas DataFrames.
* **Input Sanitization:** Automatically detects and fixes incorrect `format: "px"` headers in user queries to prevent crashes.

### 3. Enterprise-Grade Architecture
* **Smart "Sanitizer" Tab:** Users can clean data (rename columns, drop nulls) using natural language before analysis.
* **State Management:** Utilizes Streamlit Session State to persist cleaned datasets across different tabs.
* **Rate Limit Handling:** Implements `@st.cache_data` to minimize API costs and latency.
* **Dynamic Delimiters:** Auto-detects and handles European CSV formats (semicolons) vs standard commas.

---

## Architecture

The application follows a modular "Frontend-Logic" pattern:

```text
ai_data_analyst_v3/
├── app.py              # Frontend: UI, Session State, and Input Handling
├── utils.py            # Backend: API Logic, Prompt Engineering, SCB Parser
├── requirements.txt    # Dependency Management
└── .streamlit/
    └── secrets.toml    # Secure API Key Storage (Not in Repo)
