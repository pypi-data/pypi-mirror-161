# Why use CordSearch
In response to the Covid-19 pandemic, research efforts and subsequent publications were dramatically accelerated. The breakneck pace has made it nearly impossible for the medical community to verify and reference the results of the many papers published daily. CordSearch can make this process more efficient by providing easy to use semantic search functions. For any paper in the CORD-19 dataset, CordSearch can be used to quickly find similar papers or sentences. If a paper has a promising conclusion, using CordSearch can help researchers identify whether or not the result is supported by the broader literature.

# Package setup

Create a virtual environment and then `pip install -r requirements.txt`.

## Download the data

The Cord-19 dataset can be downloaded through the Huggingface Dataset Hub:

```python
from datasets import load_dataset

ds = load_dataset('cord19', 'fulltext')
```

The dataset is approximately 9gb

## Download punkt for NLTK

```python
import nltk

nltk.download('punkt')
```
 

# Using CordSearch
```python
from cordsearch import CordDataset

ds = CordDataset()

# Get abstracts by ID:
abstract = ds.abstracts[10]

# Get individual sentences by specifying the abstract and sentence IDs
sentence = ds.sentence(abstract_id=10, sentence_id=5)

# Find similar papers by specifying the abstract of interest and the number of most similar papers to be displayed
ds.find_similar_abstracts(abstract_id=10, top_k=2)

# Find similar papers by specifying the fulltext of interest
ds.find_similar_papers(bodytext_id=10, top_k=2)

# Find similar sentences from CORD-19 abstracts
ds.quick_find_similar_sentences(abstract_id=10, sentence_id=5, top_k=2)

# Find similar sentences from CORD-19 fulltexts
ds.find_similar_sentences(bodytext_id=10, sentence_id=5, top_k=2)
```
