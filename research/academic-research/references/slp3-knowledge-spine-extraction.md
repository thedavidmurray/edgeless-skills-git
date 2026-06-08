# SLP3 Knowledge Spine Extraction Workflow

## Context
When ingesting chapters from *Speech and Language Processing* (3rd ed. draft, Jurafsky & Martin, 2026), follow this pipeline to extract structured knowledge spines and track progress.

## Pipeline

```
1. Download PDF from https://web.stanford.edu/~jurafsky/slp3/<chapter>.pdf
2. Extract text with pymupdf (fitz)
3. Structure into knowledge spine entry (markdown)
4. Save to claude-vault/03-Knowledge/Knowledge-Spine/<chapter-name>.md
5. Update tracker: claude-vault/03-Knowledge/Knowledge-Spine/slp3-ingestion-tracker.md
6. Identify actionable tasks for the swarm
7. Create Paperclip issues (if API available)
```

## Canonical Locations

- **Knowledge spines**: `claude-vault/03-Knowledge/Knowledge-Spine/`
- **Master tracker**: `claude-vault/03-Knowledge/Knowledge-Spine/slp3-ingestion-tracker.md`
- **DO NOT use**: `Codex-vault/` (deprecated, redirect to claude-vault)

## Chapter Coverage

| # | Title | Status | Key Topics |
|---|-------|--------|------------|
| 2 | Words and Tokens | ✅ | Tokenization, normalization |
| 3 | N-gram Language Models | ✅ | MLE, smoothing, perplexity |
| 4 | Logistic Regression | ✅ | Sigmoid, softmax, regularization |
| 5 | Embeddings | ✅ | word2vec, GloVe, FastText |
| 6 | Neural Networks | ✅ | ReLU, backprop, dropout |
| 7 | Large Language Models | ✅ | Architectures, prompting, safety |
| 8 | Transformers | ✅ | Attention, multi-head, positional encoding |
| 9 | Post-training/Alignment | ✅ | RLHF, instruction tuning, test-time compute |
| 10 | Masked Language Models | ✅ | BERT, RoBERTa, span corruption |
| 11 | IR & RAG | ✅ | Indexing, dense retrieval, reranking |
| 12 | Machine Translation | ✅ | Encoder-decoder, beam search, backtranslation |
| 13 | RNNs and LSTMs | ✅ | Elman, BPTT, LSTM gates |
| 14 | Phonetics & Speech | ✅ | ARPAbet, spectrograms, MFCC |
| 15 | Automatic Speech Recognition | ✅ | CTC, LAS, Whisper, Wav2Vec 2.0 |
| 16 | Text-to-Speech | ✅ | ENCODEC, VALL-E, RVQ, zero-shot TTS |
| 17 | Sequence Labeling (POS/NER) | ✅ | HMM, CRF, BIO tagging, Viterbi |
| 18 | Context-Free Grammars | 🔄 | CKY, constituency parsing |
| 19-25 | Parsing, IE, Semantics, Discourse | ⏳ | Pending |
| A-K | Appendices | ⏳ | HMMs, Naive Bayes, smoothing |

## Spine Format Template

Each knowledge spine should include:
1. **Core Concepts** - Main definitions and key ideas
2. **Key Equations** - Numbered equations from the chapter
3. **Key Papers/Systems** - Citations and authors
4. **Connections** - Links to other chapters
5. **Applications** - Real-world use cases
6. **Historical Notes** - Development timeline

## Text Extraction Command

```python
import fitz
doc = fitz.open('/tmp/slp3-chXX.pdf')
text = ''.join(page.get_text() for page in doc)
```

## Paperclip Issue Creation

- Company ID: `c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712`
- API Base: `http://127.0.0.1:3100/api`
- **Critical route split**: List/create issues at `/api/companies/<id>/issues`, but get/patch individual issues at `/api/issues/<id>` (NOT `/api/companies/<id>/issues/<id>`)

## Batch Groupings

- **Batch 1 (Foundations)**: Ch. 2-6
- **Batch 2 (Modern LLMs)**: Ch. 7-9
- **Batch 3 (Applied NLP)**: Ch. 10-16
- **Batch 4 (Linguistic Structure)**: Ch. 17-25
- **Batch 5 (Algorithms)**: Appendices A-K

## Discovered 2026-06-05

The paperclip API route split was discovered during this ingestion. Collection operations (list, create) use `/api/companies/<id>/issues`, but individual operations (get, patch) use `/api/issues/<id>` directly. This is documented in `references/rest-api-routes.md` in the `paperclip-api` skill.
