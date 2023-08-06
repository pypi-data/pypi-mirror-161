import numpy as np

AA_DICT = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4,
           'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
           'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14,
           'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19,
           '?': 20}
AA_COUNT = len(AA_DICT)
AA_DICT_REV = {AA_DICT[key]: key for key in AA_DICT}


def tokenize(seq):
    digit_seq = np.array(list(map(lambda x: AA_DICT[x], seq)))

    return digit_seq[None, :]


def mask_data(data, mask_prob):
    bool_mask = np.random.rand(data.shape[0] * data.shape[1]) < mask_prob
    bool_mask = bool_mask.reshape(data.shape)

    to_replace = data[bool_mask]

    replacement = np.ones(to_replace.shape, dtype='int32') * AA_DICT['?']

    data[bool_mask] = replacement

    return data, bool_mask


def vect_batch(batch, mask_prob):
    x = np.concatenate(batch, axis=0)
    y = x.copy()

    x, mask = mask_data(x, mask_prob)

    return x, y, mask


def line_to_seqtok(line, seq_len):
    _, _, seq = line[:-1].split('\t')
    prot_len = len(seq[:-1])
    if prot_len <= seq_len:
        return None

    offset = np.random.randint(0, prot_len - seq_len + 1)
    seq = seq[offset:offset + seq_len]

    seq_in = tokenize(seq)

    if seq_in is None:
        return None

    return seq_in


def ds_iter(src_file, seq_len, mask_prob, batch_size):
    batch = []
    while True:
        with open(src_file, "r", encoding="utf-8") as fr:
            fr.readline()
            for line in fr:
                seq_in = line_to_seqtok(line, seq_len)
                if seq_in is None:
                    continue

                batch.append(seq_in)

                if len(batch) >= batch_size:
                    v_batch = vect_batch(batch, mask_prob)
                    yield v_batch
                    del batch[:]


if __name__ == '__main__':
    from pathlib import Path

    ROOT = Path(r'C:\DATA\ML-Data\BioML\datasets\Prot2Vec_dataset_2022-06')

    ds_it = ds_iter(ROOT / 'uniref90_tax-free_shuffled.tsv', 64, 0.15, 1024)

    for i in range(1000):
        a = next(ds_it)
        print()
