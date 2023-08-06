import json

import numpy as np
from pathlib import Path

N_LETS = 3

AA_DICT = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4,
           'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
           'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14,
           'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19}

AA_DICT_REV = {AA_DICT[key]: key for key in AA_DICT}

N_OF_AA = len(AA_DICT)

SPEC_TOK_OFFSET = N_OF_AA ** N_LETS
SPECIAL_TOKENS_DICT = {'?': SPEC_TOK_OFFSET + 1, '<': SPEC_TOK_OFFSET + 2, '>': SPEC_TOK_OFFSET + 3}

VOCABULARY_SIZE = N_OF_AA ** N_LETS + len(SPECIAL_TOKENS_DICT)


def tokenize(seq):
    tokens = [SPECIAL_TOKENS_DICT['<']]
    for i in range(len(seq) - N_LETS + 1):
        token_id = 0
        n_let = seq[i:i + N_LETS]
        for i_aa, aa in enumerate(n_let):
            aa_tok_add = AA_DICT[aa] * (N_OF_AA ** i_aa)
            token_id += aa_tok_add
        tokens.append(token_id)

    tokens.append(SPECIAL_TOKENS_DICT['>'])
    return np.array(tokens)[None, :]


def mask_data(data, mask_prob, exclude_edges, hinter):
    bool_mask = np.random.rand(data.shape[0] * data.shape[1]) < mask_prob
    bool_mask = bool_mask.reshape(data.shape)

    bool_mask[:, 0] = False
    bool_mask[:, -1] = False
    if exclude_edges:
        bool_mask[:, 1] = False
        bool_mask[:, -2] = False

    to_replace = data[bool_mask]

    if hinter is None:
        replacement = np.ones(to_replace.shape, dtype='int32') * SPECIAL_TOKENS_DICT['?']
    else:
        replacement = np.array(list(map(lambda x: hinter[x], to_replace)))

    data[bool_mask] = replacement

    return data, bool_mask


def vect_batch(batch, mask_prob, exclude_edges, hinter):
    tokens_in = np.concatenate(batch, axis=0)
    tokens_out = tokens_in.copy()
    if mask_prob > 1e-6:
        tokens_in, mask = mask_data(tokens_in, mask_prob, exclude_edges, hinter)

    return tokens_in, tokens_out, mask


def ds_iter(src_file, seq_len, mask_prob, batch_size, exclude_edges=False, hint_path=None, random=False):
    if hint_path is not None:
        with open(hint_path, 'r', encoding='utf-8') as fr:
            hinter = json.load(fr)
            hinter = {int(key): int(hinter[key]) for key in hinter}
    else:
        hinter = None

    batch = []
    while True:
        with open(src_file, "r", encoding="utf-8") as fr:
            fr.readline()
            for line in fr:
                _, _, seq = line[:-1].split('\t')
                prot_len = len(seq[:-1])
                if prot_len <= seq_len:
                    continue

                offset = np.random.randint(0, prot_len - seq_len + 1)
                seq = seq[offset:offset + seq_len]

                if random:
                    seq = np.random.randint(0, 20, len(seq))
                    seq = ''.join(list(map(lambda x: AA_DICT_REV[x], seq)))

                seq_in = tokenize(seq)

                if seq_in is None:
                    continue

                batch.append(seq_in)

                if len(batch) >= batch_size:
                    v_batch = vect_batch(batch, mask_prob, exclude_edges, hinter)
                    yield v_batch
                    del batch[:]


if __name__ == '__main__':
    data_dir = Path(r'C:\DATA\ML-Data\BioML\datasets\UniRef90\refprot_random_taxfree.tsv')
    hint_dir = Path(
        r'C:\DATA\ML-Data\BioML\datasets\UniRef90\tokenizer_output\overlaping_triplets\hints\10_hint_redundant_triplets.json')

    GEN = ds_iter(data_dir, 20, 0.9, 32, False, hint_dir, True)

    while True:
        a = next(GEN)
        print()
