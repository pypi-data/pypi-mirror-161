import json
import os.path
import random
from dataclasses import dataclass
from typing import Optional, Any, Tuple, List, Dict, Union
from transformers.data.data_collator import DataCollatorMixin
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from transformers.tokenization_utils_base import PreTrainedTokenizerBase, BatchEncoding


def load_json(path: str, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as r:
        content = json.load(r)
    return content


def chk_pad_token(tokenizer: PreTrainedTokenizerBase):
    if tokenizer._pad_token is None:
        raise ValueError(
            "You are attempting to pad samples but the tokenizer you are using"
            f" ({tokenizer.__class__.__name__}) does not have a pad token."
        )


def allocate_ids_to_pad(examples: Any, base: Any, tokenizer: PreTrainedTokenizerBase):
    for i, example in enumerate(examples):
        if tokenizer.padding_side == "right":
            base[i, : example.shape[0]] = example
        else:
            base[i, -example.shape[0]:] = example
    return base


def _numpy_collate_batch(examples, tokenizer: PreTrainedTokenizerBase, pad_to_multiple_of: Optional[int] = None):
    import numpy as np

    if isinstance(examples[0], (list, tuple)):
        examples = [np.array(e, dtype=np.int64) for e in examples]

    length_of_first = len(examples[0])
    are_tensors_same_length = all(len(x) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0):
        return np.stack(examples, axis=0)

    chk_pad_token(tokenizer=tokenizer)

    max_length = max(len(x) for x in examples)

    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0):
        max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of

    result = np.full(shape=(len(examples), max_length), fill_value=tokenizer.pad_token_id, dtype=examples[0].dtype)
    result = allocate_ids_to_pad(examples=examples, base=result, tokenizer=tokenizer)

    return result


def _torch_collate_batch(examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
    import numpy as np
    import torch

    if isinstance(examples[0], (list, tuple, np.ndarray)):
        examples = [torch.tensor(e, dtype=torch.long) for e in examples]

    length_of_first = examples[0].size(0)


    are_tensors_same_length = all(x.size(0) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0):
        return torch.stack(examples, dim=0)

    chk_pad_token(tokenizer=tokenizer)

    max_length = max(x.size(0) for x in examples)

    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0):
        max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
    result = examples[0].new_full([len(examples), max_length], tokenizer.pad_token_id)
    result = allocate_ids_to_pad(examples=examples, base=result, tokenizer=tokenizer)

    return result


def _tf_collate_batch(examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
    import numpy as np
    import tensorflow as tf

    if isinstance(examples[0], (list, tuple)):
        examples = [tf.convert_to_tensor(e, dtype=tf.int64) for e in examples]

    # Check if padding is necessary.
    length_of_first = len(examples[0])
    are_tensors_same_length = all(len(x) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0):
        return tf.stack(examples, axis=0)

    chk_pad_token(tokenizer=tokenizer)

    max_length = max(len(x) for x in examples)
    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0):
        max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of

    result = []
    rank = tf.rank(examples[0])
    paddings = np.zeros((rank, 2), dtype=np.int32)
    for example in examples:
        if tokenizer.padding_side == "right":
            paddings[0, 1] = max_length - len(example)
        else:
            paddings[0, 0] = max_length - len(example)
        result.append(tf.pad(example, paddings, constant_values=tokenizer.pad_token_id))

    return tf.stack(result, axis=0)


@dataclass
class DataCollatorForPromptLanguageModeling(DataCollatorMixin):
    tokenizer: PreTrainedTokenizerBase
    mlm: bool = True
    mlm_probability: float = 0.15
    pad_to_multiple_of: Optional[int] = None
    tf_experimental_compile: bool = False
    return_tensors: str = "pt"

    def __post_init__(self):
        if self.mlm and self.tokenizer.mask_token is None:
            raise ValueError(
                "This tokenizer does not have a mask token which is necessary for masked language modeling. "
                "You should pass `mlm=False` to train on causal language modeling instead."
            )
        if self.tf_experimental_compile:
            import tensorflow as tf

            self.tf_mask_tokens = tf.function(self.tf_mask_tokens, jit_compile=True)

    def _replace_masks_to_labels(self, masked_sequences: Any, mask_labels:Any, return_tensors="pt"):
        new_labels = []
        for label, prompt in zip(masked_sequences, mask_labels):
            line = []
            l_append = line.append
            for l in label:
                l_append(prompt.pop(0) if l == self.tokenizer.mask_token_id else l)
            new_labels.append(line)

        if return_tensors == 'pt':
            import torch
            return torch.tensor(new_labels, dtype=torch.int32)
        elif return_tensors == 'np':
            import numpy as np
            return np.array(new_labels, dtype=np.int32)
        elif return_tensors == 'tf':
            import tensorflow as tf
            return tf.constant(new_labels, dtype=tf.int32)

        return new_labels

    @staticmethod
    def tf_bernoulli(shape, probability):
        import tensorflow as tf

        prob_matrix = tf.fill(shape, probability)
        return tf.cast(prob_matrix - tf.random.uniform(shape, 0, 1) >= 0, tf.bool)

    def tf_mask_tokens(
            self, inputs: Any, vocab_size, mask_token_id, special_tokens_mask: Optional[Any] = None,
            prompt_labels: Optional[Any] = None, prompt_label_masks: Optional[Any] = None
    ) -> Tuple[Any, Any]:

        import tensorflow as tf

        input_shape = tf.shape(inputs)
        masked_indices = self.tf_bernoulli(input_shape, self.mlm_probability) & ~special_tokens_mask

        if prompt_label_masks:
            prompt_area = self.tf_bernoulli(input_shape, prompt_label_masks)

        # TODO: check it works
        labels = tf.where(masked_indices + prompt_area, inputs, -100)

        # 80% of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
        indices_replaced = self.tf_bernoulli(input_shape, 0.8) & masked_indices

        inputs = tf.where(indices_replaced, mask_token_id, inputs)

        # 10% of the time, we replace masked input tokens with random word
        indices_random = self.tf_bernoulli(input_shape, 0.1) & masked_indices & ~indices_replaced
        random_words = tf.random.uniform(input_shape, maxval=vocab_size, dtype=tf.int64)
        inputs = tf.where(indices_random, random_words, inputs)

        # add the prompts
        if prompt_labels:
            labels = self._replace_masks_to_labels(labels, prompt_labels, return_tensors='tf')

        # The rest of the time (10% of the time) we keep the masked input tokens unchanged
        return inputs, labels

    def tf_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        import tensorflow as tf

        prompt_labels, prompt_label_masks = None, None

        # Handle dict or lists with proper padding and conversion to tensor.
        if isinstance(examples[0], (dict, BatchEncoding)):
            if "prompt_labels" in examples[0]:
                prompt_labels = [example.pop('prompt_labels') for example in examples]
            if "prompt_label_masks" in examples[0]:
                prompt_label_masks = [example.pop('prompt_label_masks') for example in examples]
                prompt_label_masks = self.tokenizer.pad({"input_ids": prompt_label_masks}, return_tensors="tf",
                                                        pad_to_multiple_of=self.pad_to_multiple_of)['input_ids']
            batch = self.tokenizer.pad(examples, return_tensors="tf", pad_to_multiple_of=self.pad_to_multiple_of)
        else:
            batch = {
                "input_ids": _tf_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
            }

        # If special token mask has been preprocessed, pop it from the dict.
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm:
            if special_tokens_mask is None:
                special_tokens_mask = [
                    self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True)
                    for val in batch["input_ids"].numpy().tolist()
                ]
                # Cannot directly create as bool
                special_tokens_mask = tf.cast(tf.convert_to_tensor(special_tokens_mask, dtype=tf.int64), tf.bool)
            else:
                special_tokens_mask = tf.cast(special_tokens_mask, tf.bool)

            batch["input_ids"], batch["labels"] = self.tf_mask_tokens(
                tf.cast(batch["input_ids"], tf.int64),
                special_tokens_mask=special_tokens_mask,
                mask_token_id=self.tokenizer.mask_token_id,
                vocab_size=len(self.tokenizer),
                prompt_labels=prompt_labels,
                prompt_label_masks=prompt_label_masks,

            )

        else:
            labels = batch["input_ids"]
            if self.tokenizer.pad_token_id is not None:
                # Replace self.tokenizer.pad_token_id with -100
                labels = tf.where(labels == self.tokenizer.pad_token_id, -100, labels)
            else:
                labels = tf.identity(labels)  # Makes a copy, just in case
            batch["labels"] = labels
        return batch

    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:

        prompt_labels, prompt_label_masks = None, None
        # Handle dict or lists with proper padding and conversion to tensor.
        if isinstance(examples[0], (dict, BatchEncoding)):
            if "prompt_labels" in examples[0]:
                prompt_labels = [example.pop('prompt_labels') for example in examples]
            if "prompt_label_masks" in examples[0]:
                prompt_label_masks = [example.pop('prompt_label_masks') for example in examples]
                prompt_label_masks = self.tokenizer.pad(
                    {"input_ids": prompt_label_masks}, return_tensors="pt", pad_to_multiple_of=self.pad_to_multiple_of
                )
            batch = self.tokenizer.pad(examples, return_tensors="pt", pad_to_multiple_of=self.pad_to_multiple_of)
        else:
            batch = {
                "input_ids": _torch_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
            }
        # If special token mask has been preprocessed, pop it from the dict.
        special_tokens_mask = batch.pop("special_tokens_mask", None)

        if self.mlm:
            batch["input_ids"], batch["labels"] = self.torch_mask_tokens(
                batch["input_ids"], special_tokens_mask=special_tokens_mask,
                prompt_labels=prompt_labels, prompt_label_masks=prompt_label_masks['input_ids']
            )
        else:
            labels = batch["input_ids"].clone()
            if self.tokenizer.pad_token_id is not None:
                labels[labels == self.tokenizer.pad_token_id] = -100
            batch["labels"] = labels
        return batch

    def torch_mask_tokens(self, inputs: Any, special_tokens_mask: Optional[Any] = None,
                          prompt_labels:Optional[Any]=None, prompt_label_masks:Optional[Any]=None) -> Tuple[Any, Any]:

        import torch
        labels = inputs.clone()

        # We sample a few tokens in each sequence for MLM training (with probability `self.mlm_probability`)
        probability_matrix = torch.full(labels.shape, self.mlm_probability)

        if special_tokens_mask is None:
            special_tokens_mask = [
                self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
            ]
            special_tokens_mask = torch.tensor(special_tokens_mask, dtype=torch.bool)
        else:
            special_tokens_mask = special_tokens_mask.bool()

        probability_matrix.masked_fill_(special_tokens_mask.bool(), value=0.0)

        if prompt_label_masks is not None:
            probability_matrix.masked_fill_(prompt_label_masks.bool(), value=1.0)

        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = -100  # We only compute loss on masked tokens

        # 80% of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)

        # 10% of the time, we replace masked input tokens with random word
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]
        # The rest of the time (10% of the time) we keep the masked input tokens unchanged
        if prompt_labels:
            labels = self._replace_masks_to_labels(labels, prompt_labels, return_tensors='pt')
        return inputs, labels

    def numpy_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        import numpy as np
        # Handle dict or lists with proper padding and conversion to tensor.
        prompt_labels, prompt_label_masks = None, None
        if isinstance(examples[0], (dict, BatchEncoding)):
            if "prompt_labels" in examples[0]:
                prompt_labels = [example.pop('prompt_labels') for example in examples]
            if "prompt_label_masks" in examples[0]:
                prompt_label_masks = [example.pop('prompt_label_masks') for example in examples]
                prompt_label_masks = self.tokenizer.pad(
                    {"input_ids": prompt_label_masks}, return_tensors="np", pad_to_multiple_of=self.pad_to_multiple_of
                )
            batch = self.tokenizer.pad(examples, return_tensors="np", pad_to_multiple_of=self.pad_to_multiple_of)
        else:
            batch = {
                "input_ids": _numpy_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
            }

        # If special token mask has been preprocessed, pop it from the dict.
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm:
            batch["input_ids"], batch["labels"] = self.numpy_mask_tokens(
                batch["input_ids"], special_tokens_mask=special_tokens_mask,
                prompt_labels=prompt_labels, prompt_label_masks=prompt_label_masks['input_ids']
            )
        else:
            labels = np.copy(batch["input_ids"])
            if self.tokenizer.pad_token_id is not None:
                labels[labels == self.tokenizer.pad_token_id] = -100
            batch["labels"] = labels
        return batch

    def numpy_mask_tokens(self, inputs: Any, special_tokens_mask: Optional[Any] = None,
                          prompt_labels:Optional[Any]=None, prompt_label_masks:Optional[Any]=None) -> Tuple[Any, Any]:

        import numpy as np

        labels = np.copy(inputs)
        # We sample a few tokens in each sequence for MLM training (with probability `self.mlm_probability`)
        probability_matrix = np.full(labels.shape, self.mlm_probability)
        if special_tokens_mask is None:
            special_tokens_mask = [
                self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
            ]
            special_tokens_mask = np.array(special_tokens_mask, dtype=np.bool)
        else:
            special_tokens_mask = special_tokens_mask.astype(np.bool)

        probability_matrix[special_tokens_mask] = 0
        if prompt_label_masks is not None:
            probability_matrix[prompt_label_masks.astype(np.bool)] = 1
        # Numpy doesn't have bernoulli, so we use a binomial with 1 trial
        masked_indices = np.random.binomial(1, probability_matrix, size=probability_matrix.shape).astype(np.bool)
        labels[~masked_indices] = -100  # We only compute loss on masked tokens

        # 80% of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
        indices_replaced = np.random.binomial(1, 0.8, size=labels.shape).astype(np.bool) & masked_indices
        inputs[indices_replaced] = self.tokenizer.mask_token_id

        # 10% of the time, we replace masked input tokens with random word
        # indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        indices_random = (
            np.random.binomial(1, 0.5, size=labels.shape).astype(np.bool) & masked_indices & ~indices_replaced
        )
        random_words = np.random.randint(
            low=0, high=len(self.tokenizer), size=np.count_nonzero(indices_random), dtype=np.int64
        )
        inputs[indices_random] = random_words

        if prompt_labels:
            labels = self._replace_masks_to_labels(labels, prompt_labels, return_tensors='np')

        return inputs, labels


def nested_numeric(value:Any) -> Any:
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        elif "".join(value.split(".")).isdigit():
            return float(value)
        return value
    elif isinstance(value, dict):
        return {nested_numeric(k): nested_numeric(v) for k,v in value.items()}
    elif isinstance(value, dict):
        return [nested_numeric(v) for v in value]
    return value


def get_prompt_dataset(dataset: Any, tokenizer: Union[PreTrainedTokenizerBase],
                        max_seq_len: int, text_col: list = [], desc: List[str] = [],
                        mapping_dict:Optional[Dict]=None):

    import numpy as np
    import logging

    if not mapping_dict and 'label' in dataset.features:
        mapping_dict = {i: k for i, k in enumerate(dataset.features['label'].names)}

    elif not mapping_dict and "label" not in dataset.features:
        logging.info("There is no prompt! The mlm dataset will be returned for training.")

    mapping_dict = mapping_dict if mapping_dict else None

    get_desc = lambda vlist: random.choice(vlist)

    def example_fn(examples):
        prompt_ids = tokenizer([mapping_dict[p] for p in examples['label']], add_special_tokens=False)['input_ids']

        prompt_tokens = None
        if mapping_dict:
            prompt_tokens = [get_desc(desc).format(prompt=" ".join([tokenizer.mask_token]*len(prompt_ids[i])))
                             for i in range(len(examples[text_col]))]

        outputs = tokenizer(
            examples[text_col], prompt_tokens, max_length=max_seq_len, padding='max_length', truncation= True
        )

        if mapping_dict:
            outputs['labels'] = examples['label']
            outputs['prompt_label_masks'] = [np.where(np.array(sentence) == tokenizer.mask_token_id, 1, 0)[0]
                                             for sentence in zip(outputs['input_ids'])]
            outputs['prompt_labels'] = prompt_ids

        return outputs

    return dataset.map(example_fn, batched=True, remove_columns=dataset.column_names)


def load_prompt(name: str, prompt_path : str="prompt.json", encoding:str = 'utf-8'):
    print(prompt_path)
    prompt = load_json(prompt_path, encoding=encoding).get(name)

    if prompt is None:
        raise KeyError("Prompt가 정의되어 있지 않습니다.")
    prompt = nested_numeric(prompt)
    lines, map_dict, text_col = None, None, None
    if "lines" in prompt:
        lines = prompt["lines"]
    if "map_dict" in prompt:
        map_dict = prompt["map_dict"]
    if "text_col" in prompt:
        text_col = prompt['text_col']
    return lines, map_dict, text_col


def get_prompt_datasets_and_collator(
        tokenizer:Union[PreTrainedTokenizerBase, PreTrainedTokenizerFast],
        dataset_names: List[str], max_seq_len: int = 128) -> Tuple[Any, Any]:
    """
    >>> from transformers import AutoTokenizer
    >>> tokenizer = AutoTokenizer.from_pretrained("klue/bert-base")
    >>> dataset, collator = get_prompt_datasets_and_collator(tokenizer, dataset_names=['klue-ynat', 'nsmc'])
    """

    from datasets import load_dataset, concatenate_datasets

    merged = []
    for name in dataset_names:
        inputs = load_dataset(*name.split("-"), split='train')
        lines, map_dict, text_col = load_prompt(name, prompt_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.json"))
        merged.append(
            get_prompt_dataset(
                dataset=inputs,
                tokenizer=tokenizer,
                max_seq_len=max_seq_len,
                text_col=text_col,
                desc=lines,
                mapping_dict=map_dict
            )
        )

    merged = concatenate_datasets(merged)
    merged = merged.shuffle()
    data_collator = DataCollatorForPromptLanguageModeling(tokenizer=tokenizer)
    return merged, data_collator

