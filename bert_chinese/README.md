you can download the pretrained bert model here **[google-bert/bert-base-chinese · Hugging Face](https://huggingface.co/google-bert/bert-base-chinese)**

or in hf mirror site **[google-bert/bert-base-chinese · HF Mirror (hf-mirror.com)](https://hf-mirror.com/google-bert/bert-base-chinese)**

## How to Get Started With the Model

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

model = AutoModelForMaskedLM.from_pretrained("bert-base-chinese")
```