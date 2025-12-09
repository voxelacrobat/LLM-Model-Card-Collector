"""
===========================================================================================
@file       model_card_collector_shared.py
@brief      Definition file of global usable dictionaries
@details    PAPER_SOURCES - Dict of model architectures with paper references and authors
            ARCHITECTURE_DEFS - Dict of model architectures withdescriptions, training parameters and sources
@author     MM
@date       05.12.2025
@note       
===========================================================================================
"""
PAPER_SOURCES = {
            "BERT": {
                "paper_url": "https://arxiv.org/abs/1810.04805",
                "paper_title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": "Devlin et al., 2019",
                "venue": "NAACL"
            },
            "RoBERTa": {
                "paper_url": "https://arxiv.org/abs/1907.11692",
                "paper_title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
                "authors": "Liu et al., 2019",
                "venue": "arXiv"
            },
            "SciBERT": {
                "paper_url": "https://arxiv.org/abs/1903.10676",
                "paper_title": "SciBERT: A Pretrained Language Model for Scientific Text",
                "authors": "Beltagy et al., 2019",
                "venue": "EMNLP"
            },
            "BioBERT": {
                "paper_url": "https://arxiv.org/abs/1901.08746",
                "paper_title": "BioBERT: a pre-trained biomedical language representation model",
                "authors": "Lee et al., 2020",
                "venue": "Bioinformatics"
            },
            "ELECTRA": {
                "paper_url": "https://arxiv.org/abs/2003.10555",
                "paper_title": "ELECTRA: Pre-training Text Encoders as Discriminators",
                "authors": "Clark et al., 2020",
                "venue": "ICLR"
            },
            "Llama": {
                "paper_url": "https://arxiv.org/abs/2307.09288",
                "paper_title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
                "authors": "Touvron et al., 2023",
                "venue": "arXiv"
            },
            "Llama-3": {
                "paper_url": "https://arxiv.org/abs/2407.21783",
                "paper_title": "The Llama 3 Herd of Models",
                "authors": "Meta AI, 2024",
                "venue": "arXiv"
            },
            "T5": {
                "paper_url": "https://arxiv.org/abs/1910.10683",
                "paper_title": "Exploring the Limits of Transfer Learning with T5",
                "authors": "Raffel et al., 2020",
                "venue": "JMLR"
            },
            "BART": {
                "paper_url": "https://arxiv.org/abs/1910.13461",
                "paper_title": "BART: Denoising Sequence-to-Sequence Pre-training",
                "authors": "Lewis et al., 2020",
                "venue": "ACL"
            },
            "mT5": {
                "paper_url": "https://arxiv.org/abs/2010.11934",
                "paper_title": "mT5: A massively multilingual text-to-text transformer",
                "authors": "Xue et al., 2021",
                "venue": "NAACL"
            },
            "GPT-4": {
                "paper_url": "https://cdn.openai.com/papers/gpt-4-system-card.pdf",
                "paper_title": "GPT-4 System Card",
                "authors": "OpenAI, 2023",
                "venue": "OpenAI"
            },
            "GPT-4o": {
                "paper_url": "https://cdn.openai.com/gpt-4o-system-card.pdf",
                "paper_title": "GPT-4o System Card",
                "authors": "OpenAI, 2024",
                "venue": "OpenAI"
            },
            "Claude": {
                "paper_url": "https://assets.anthropic.com/m/61e7d27f8c8f5919/original/Claude-3-Model-Card.pdf",
                "paper_title": "Claude 3 Model Card",
                "authors": "Anthropic, 2024",
                "venue": "Anthropic"
            },
            "Gemini": {
                "paper_url": "https://storage.googleapis.com/deepmind-media/gemini/gemini_1_report.pdf",
                "paper_title": "Gemini: A Family of Highly Capable Multimodal Models",
                "authors": "Google DeepMind, 2023",
                "venue": "Google"
            }
        }

ARCHITECTURE_DEFS = {
        "BERT": {
            "architecture": "Encoder-only",
            "description": "Bidirectional Encoder Representations from Transformers",
            "huggingface": [
                {"id": "google-bert/bert-base-uncased", "version": "base"},
                {"id": "google-bert/bert-large-uncased", "version": "large"}
            ],
            "year": 2018,
            "organization": "Google"
        },
        "RoBERTa": {
            "architecture": "Encoder-only",
            "description": "Robustly Optimized BERT Pretraining Approach",
            "huggingface": [
                {"id": "FacebookAI/roberta-base", "version": "base"},
                {"id": "FacebookAI/roberta-large", "version": "large"}
            ],
            "year": 2019,
            "organization": "Facebook AI"
        },
        "SciBERT": {
            "architecture": "Encoder-only",
            "description": "BERT variant for scientific text",
            "huggingface": [
                {"id": "allenai/scibert_scivocab_uncased", "version": "scivocab"}
            ],
            "year": 2019,
            "organization": "Allen AI"
        },
        "BioBERT": {
            "architecture": "Encoder-only",
            "description": "BERT for biomedical text mining",
            "huggingface": [
                {"id": "dmis-lab/biobert-v1.1", "version": "v1.1"}
            ],
            "year": 2019,
            "organization": "DMIS Lab"
        },
        "ELECTRA": {
            "architecture": "Encoder-only",
            "description": "Efficiently Learning an Encoder",
            "huggingface": [
                {"id": "google/electra-base-discriminator", "version": "base"}
            ],
            "year": 2020,
            "organization": "Google"
        },
        "GPT-4": {
            "architecture": "Decoder-only",
            "description": "Generative Pre-trained Transformer 4",
            "versions": [
                {"name": "GPT-4", "released": "2023-03-14"},
                {"name": "GPT-4 Turbo", "released": "2023-11-06"},
                {"name": "GPT-4o", "released": "2024-05-13"}
            ],
            "year": 2023,
            "organization": "OpenAI"
        },
        "Claude": {
            "architecture": "Decoder-only",
            "description": "Constitutional AI language model",
            "versions": [
                {"name": "Claude 2", "released": "2023-07"},
                {"name": "Claude 3 Haiku", "released": "2024-03-04"},
                {"name": "Claude 3 Sonnet", "released": "2024-03-04"},
                {"name": "Claude 3 Opus", "released": "2024-03-04"},
                {"name": "Claude 3.5 Sonnet", "released": "2024-06-20"}
            ],
            "year": 2023,
            "organization": "Anthropic"
        },
        "Llama": {
            "architecture": "Decoder-only",
            "description": "Large Language Model Meta AI",
            "huggingface": [
                {"id": "meta-llama/Llama-2-7b-hf", "version": "Llama 2 7B"},
                {"id": "meta-llama/Llama-2-13b-hf", "version": "Llama 2 13B"},
                {"id": "meta-llama/Llama-2-70b-hf", "version": "Llama 2 70B"},
                {"id": "meta-llama/Llama-3.1-8B", "version": "Llama 3.1 8B"}
            ],
            "year": 2023,
            "organization": "Meta"
        },
        "Gemini": {
            "architecture": "Decoder-only",
            "description": "Multimodal AI model by Google",
            "versions": [
                {"name": "Gemini 1.0 Pro", "released": "2023-12-06"},
                {"name": "Gemini 1.5 Pro", "released": "2024-02-15"},
                {"name": "Gemini 1.5 Flash", "released": "2024-05-14"},
                {"name": "Gemini 2.0 Flash", "released": "2024-12"}
            ],
            "year": 2023,
            "organization": "Google DeepMind"
        },
        "T5": {
            "architecture": "Encoder-Decoder",
            "description": "Text-to-Text Transfer Transformer",
            "huggingface": [
                {"id": "google-t5/t5-small", "version": "small"},
                {"id": "google-t5/t5-base", "version": "base"},
                {"id": "google-t5/t5-large", "version": "large"},
                {"id": "google-t5/t5-3b", "version": "3B"},
                {"id": "google-t5/t5-11b", "version": "11B"}
            ],
            "year": 2019,
            "organization": "Google"
        },
        "BART": {
            "architecture": "Encoder-Decoder",
            "description": "Bidirectional and Auto-Regressive Transformer",
            "huggingface": [
                {"id": "facebook/bart-base", "version": "base"},
                {"id": "facebook/bart-large", "version": "large"}
            ],
            "year": 2019,
            "organization": "Facebook AI"
        },
        "mT5": {
            "architecture": "Encoder-Decoder",
            "description": "Multilingual T5",
            "huggingface": [
                {"id": "google/mt5-small", "version": "small"},
                {"id": "google/mt5-base", "version": "base"}
            ],
            "year": 2020,
            "organization": "Google"
        }
    }