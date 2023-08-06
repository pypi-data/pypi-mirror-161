from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from typing import Optional, Any, Tuple, Dict, List, Union
import torch


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


def _replace_masks_to_labels(tokenizer, masked_sequences: Any, mask_labels: Any, return_tensors="pt"):
    new_labels = []
    for label, prompt in zip(masked_sequences, mask_labels):
        line = []
        l_append = line.append
        for l in label:
            l_append(prompt.pop(0) if l == tokenizer.mask_token_id else l)
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


def torch_mask_tokens(tokenizer, inputs: Any, special_tokens_mask: Optional[Any] = None,
                      prompt_labels: Optional[Any] = None, prompt_label_masks: Optional[Any] = None,
                      mlm_probability: float = 0.15) -> Tuple[Any, Any]:
    labels = inputs.clone()

    # We sample a few tokens in each sequence for MLM training (with probability `self.mlm_probability`)
    probability_matrix = torch.full(labels.shape, mlm_probability)

    if special_tokens_mask is None:
        special_tokens_mask = [
            tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
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
    inputs[indices_replaced] = tokenizer.convert_tokens_to_ids(tokenizer.mask_token)

    # 10% of the time, we replace masked input tokens with random word
    indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
    random_words = torch.randint(len(tokenizer), labels.shape, dtype=torch.long)
    inputs[indices_random] = random_words[indices_random]

    # The rest of the time (10% of the time) we keep the masked input tokens unchanged
    if prompt_labels:
        labels = _replace_masks_to_labels(tokenizer, labels, prompt_labels, return_tensors='pt')
    return inputs, labels


def numpy_mask_tokens(tokenizer, inputs: Any, special_tokens_mask: Optional[Any] = None,
                      prompt_labels: Optional[Any] = None, prompt_label_masks: Optional[Any] = None, mlm: bool = True,
                      mlm_probability: float = 0.15) -> Tuple[Any, Any]:
    import numpy as np

    labels = np.copy(inputs)
    # We sample a few tokens in each sequence for MLM training (with probability `self.mlm_probability`)
    probability_matrix = np.full(labels.shape, mlm_probability)
    if special_tokens_mask is None:
        special_tokens_mask = [
            tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        special_tokens_mask = np.array(special_tokens_mask, dtype=np.bool_)
    else:
        special_tokens_mask = special_tokens_mask.astype(np.bool_)

    probability_matrix[special_tokens_mask] = 0
    if prompt_label_masks is not None:
        probability_matrix[prompt_label_masks.astype(np.bool_)] = 1
    # Numpy doesn't have bernoulli, so we use a binomial with 1 trial
    masked_indices = np.random.binomial(1, probability_matrix, size=probability_matrix.shape).astype(np.bool_)
    labels[~masked_indices] = -100  # We only compute loss on masked tokens

    # 80% of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
    indices_replaced = np.random.binomial(1, 0.8, size=labels.shape).astype(np.bool_) & masked_indices
    inputs[indices_replaced] = tokenizer.mask_token_id

    # 10% of the time, we replace masked input tokens with random word
    # indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
    indices_random = (
            np.random.binomial(1, 0.5, size=labels.shape).astype(np.bool_) & masked_indices & ~indices_replaced
    )
    random_words = np.random.randint(
        low=0, high=len(tokenizer), size=np.count_nonzero(indices_random), dtype=np.int64
    )
    inputs[indices_random] = random_words

    if prompt_labels:
        labels = _replace_masks_to_labels(tokenizer, labels, prompt_labels, return_tensors='np')

    return inputs, labels


def mask_token_with_prompt(tokenizer, examples: Dict[str, Any], pad_to_multiple_of: Optional[int] = None,
                           mlm: bool = True) -> Dict[str, Any]:
    assert 'prompt_labels' in examples and 'prompt_label_masks' in examples, 'Prompt Tuning 데이터를 만들기 위해서는 ' \
                                                                             '"prompt_labels"과 "prompt_label_masks"가 ' \
                                                                             '정의되어 있어야 합니다. '

    prompt_labels = examples.pop('prompt_labels')

    prompt_label_masks = tokenizer.pad(
        {"input_ids": examples.pop('prompt_label_masks')}, return_tensors="np", pad_to_multiple_of=pad_to_multiple_of
    )

    batch = tokenizer.pad(examples, return_tensors="np", pad_to_multiple_of=pad_to_multiple_of)

    special_tokens_mask = batch.pop("special_tokens_mask", None)

    if mlm:
        batch["input_ids"], batch["labels"] = numpy_mask_tokens(tokenizer,
                                                                batch["input_ids"],
                                                                special_tokens_mask=special_tokens_mask,
                                                                prompt_labels=prompt_labels,
                                                                prompt_label_masks=prompt_label_masks['input_ids']
                                                                )
    else:
        labels = batch["input_ids"].clone()
        if tokenizer.pad_token_id is not None:
            labels[labels == tokenizer.pad_token_id] = -100
        batch["labels"] = labels
    return batch


def get_prompt_dataset(dataset: Any, tokenizer: Union[PreTrainedTokenizerBase],
                       max_seq_len: int, text_col: list = [], desc: List[str] = [],
                       mapping_dict: Optional[Dict] = None):
    """
    >>> from transformers import AutoTokenizer
    >>> from datasets import load_dataset
    >>> tokenizer = AutoTokenizer.from_pretrained("klue/bert-base")
    >>> prompt = {
    ...            'nsmc': {'lines': ['이건 {prompt}적인 문장이야.', '감정 분류 결과: {prompt}'],
    ...                     'map_dict': {0: '부정', 1: '긍정'},
    ...                     'text_col': 'document'}
    ...          }
    >>> dataset = get_prompt_dataset(
    ...    load_dataset("nsmc")['train'],
    ...    tokenizer,
    ...    max_seq_len=512,
    ...    text_col=prompt["nsmc"]['text_col'],
    ...    desc = prompt['nsmc']['lines'],
    ...    mapping_dict=prompt["nsmc"]['map_dict']
    ...
    ... )
    """
    import random
    import numpy as np
    import logging

    if not mapping_dict and 'label' in dataset.features:
        mapping_dict = {i: k for i, k in enumerate(dataset.features['label'].names)}

    elif not mapping_dict and "label" not in dataset.features:
        logging.info("There is no prompt! The mlm dataset will be returned for training.")

    mapping_dict = mapping_dict if mapping_dict else None
    get_desc = lambda vlist: random.choice(vlist)

    def example_fn(examples):
        prompt_ids = tokenizer(
            [mapping_dict[p] for p in examples['label']], add_special_tokens=False
        )['input_ids']

        prompt_tokens = None
        if mapping_dict:
            prompt_tokens = [get_desc(desc).format(prompt=" ".join([tokenizer.mask_token] * len(prompt_ids[i])))
                             for i in range(len(examples[text_col]))]

        outputs = tokenizer(
            examples[text_col], prompt_tokens, max_length=max_seq_len, padding='max_length', truncation=True
        )

        if mapping_dict:
            outputs['labels'] = examples['label']
            outputs['prompt_label_masks'] = [np.where(np.array(sentence) == tokenizer.mask_token_id, 1, 0)[0]
                                             for sentence in zip(outputs['input_ids'])]
            outputs['prompt_labels'] = prompt_ids

        outputs = mask_token_with_prompt(tokenizer, outputs)
        return outputs

    return dataset.map(example_fn, batched=True, remove_columns=dataset.column_names)


if __name__=="__main__":
    from transformers import AutoTokenizer
    from datasets import load_dataset
    tokenizer = AutoTokenizer.from_pretrained("klue/bert-base")
    prompt = {

    'nsmc': {'lines': ['이건 {prompt}적인 문장이야.', '감정 분류 결과: {prompt}'],
                                  'map_dict': {0: '부정', 1: '긍정'},

                'text_col': 'document'}
                }
    dataset = get_prompt_dataset(

    load_dataset("nsmc")['train'],

    tokenizer,

    max_seq_len = 512,

    text_col = prompt["nsmc"]['text_col'],
    desc=prompt['nsmc']['lines'],
    mapping_dict = prompt["nsmc"]['map_dict']

         )