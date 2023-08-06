# CrystalBLEU

## Install
Install the requirements:
```bash
pip install crystalbleu
```

## Usage
```python
from collections import Counter
# Import CrystalBLEU
from crystalbleu import corpus_bleu

# Extract trivially shared n-grams
k = 500
frequencies = Counter(tokenized_corpus)
trivially_shared_ngrams = dict(frequencies.most_common(k))

# Calculate CrystalBLEU
crystalBLEU_score = corpus_bleu(
    references, candidates, ignoring=trivially_shared_ngrams)
```
