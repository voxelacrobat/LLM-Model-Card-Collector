# LLM-Model-Card-Collector
Source-tracked Model Card Collector with parameter count and training data extraction

This repository contains a small Python utility to build a **source-tracked overview of language models** (encoder-only, decoder-only, encoder-decoder) based on Hugging Face model cards, metadata, and predefined architecture definitions.

The key idea is that every important piece of information (parameter count, training data, paper reference) is stored together with a **transparent source description** (e.g. “Extracted from Model Card…”, “Hugging Face metadata: 'datasets' field”, “GPT-4 System Card PDF”).

---

## Features

- Collects model information for **predefined model families** (BERT, RoBERTa, SciBERT, BioBERT, ELECTRA, T5, BART, mT5, Llama, GPT-4, Claude, Gemini, …).:contentReference[oaicite:1]{index=1}  
- Extracts:
  - Approximate **parameter counts** from model card text or tags.
  - Short **training data descriptions** from model cards or `datasets` metadata.
  - **Paper / system card references** (title, authors, venue, URL) from a shared configuration.  
- Writes per-model **Markdown files** that include:
  - Basic metadata and links.
  - Extracted fields (parameters, training data) + their sources.
  - Paper reference.
  - Original model card content.:contentReference[oaicite:3]{index=3}  
- Exports a comprehensive **Excel workbook** with:
  - One sheet per architecture type (`Encoder-only`, `Decoder-only`, `Encoder-Decoder`).
  - An `Alle Modelle` (“All models”) sheet.
  - A `Quellenübersicht` (“Source overview”) sheet listing for each model which values were used and from which sources they were derived.:contentReference[oaicite:4]{index=4}  

---

## File Structure

- `model_card_collector.py`  
  Core implementation of the `ModelCollector` class and the `main()` entry point. Handles downloading model cards, extracting information, writing Markdown and Excel outputs.:contentReference[oaicite:5]{index=5}  

- `model_card_collector_shared.py`  
  Contains the global configuration dictionaries:  
  - `PAPER_SOURCES`: per-family paper/system-card references (URL, title, authors, venue).  
  - `ARCHITECTURE_DEFS`: per-family architecture definitions (type, description, Hugging Face model IDs and/or proprietary versions, year, organisation).:contentReference[oaicite:6]{index=6}  

---

## Requirements

- Python 3.9+ (recommended)
- Python packages:
  - `huggingface_hub`
  - `pandas`
  - `openpyxl`
  - `requests` (as used by `huggingface_hub`):contentReference[oaicite:7]{index=7}  

Install them for example with:

```bash
pip install huggingface_hub pandas openpyxl requests
