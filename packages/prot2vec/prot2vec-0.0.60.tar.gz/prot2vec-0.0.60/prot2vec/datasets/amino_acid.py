import numpy as np
import tensorflow as tf

AA_DICT = {'?': 0, '<': 1, '>': 2,
           'A': 3, 'C': 4, 'D': 5, 'E': 6, 'F': 7,
           'G': 8, 'H': 9, 'I': 10, 'K': 11, 'L': 12,
           'M': 13, 'N': 14, 'P': 15, 'Q': 16, 'R': 17,
           'S': 18, 'T': 19, 'V': 20, 'W': 21, 'Y': 22}

AA_DICT_REV = {AA_DICT[key]: key for key in AA_DICT}


# AA_DISTRIBUTION = np.load('prot2vec/configs/probab_distribution.npy')


def tokenize(seq):
    digit_seq = []
    for aa in seq:
        if aa not in AA_DICT:
            print(f'Unknown amino acid letter \"{aa}\"')
            return None
        digit_seq.append(AA_DICT[aa])

    digit_seq = np.array(digit_seq)

    # TODO-WARNING: resolve this issue!
    # digit_seq[0] = 1
    # digit_seq[-1] = 2

    return digit_seq[None, :]


def mask_data(data, mask_prob, one_in_middle=False):
    if one_in_middle:
        bool_mask = np.zeros(data.shape, dtype='bool')
        mask_index = bool_mask.shape[1] // 2
        bool_mask[:, mask_index] = True
    else:
        bool_mask = np.random.rand(data.shape[0] * data.shape[1]) < mask_prob
        bool_mask = bool_mask.reshape(data.shape)

    # TODO-WARNING: resolve this issue!
    # bool_mask[:, 0] = False
    # bool_mask[:, -1] = False

    to_replace = data[bool_mask]

    replacement = np.zeros(to_replace.shape, dtype='int32')

    data[bool_mask] = replacement

    return data, bool_mask


def vect_batch(batch, mask_prob, one_in_middle=False, to_one_hot=True):
    x = np.concatenate(batch, axis=0)
    y = x.copy()

    x, mask = mask_data(x, mask_prob, one_in_middle)

    if to_one_hot:
        x = tf.one_hot(x, len(AA_DICT))
        y = tf.one_hot(y, len(AA_DICT))

    return x, y, mask


def line_to_seqtok(line, seq_len, random=''):
    _, _, seq = line[:-1].split('\t')
    prot_len = len(seq[:-1])
    if prot_len <= seq_len:
        return None

    offset = np.random.randint(0, prot_len - seq_len + 1)
    seq = seq[offset:offset + seq_len]

    if random == 'full':
        seq = ''.join(list(map(lambda x: AA_DICT_REV[x], np.random.randint(3, 23, seq_len))))

    seq_in = tokenize(seq)

    if seq_in is None:
        return None

    return seq_in


def ds_iter(src_file, seq_len, mask_prob, batch_size, one_in_middle=False, to_one_hot=True, random=''):
    batch = []
    while True:
        with open(src_file, "r", encoding="utf-8") as fr:
            fr.readline()
            for line in fr:
                seq_in = line_to_seqtok(line, seq_len, random)
                if seq_in is None:
                    continue

                batch.append(seq_in)

                if len(batch) >= batch_size:
                    v_batch = vect_batch(batch, mask_prob, one_in_middle, to_one_hot)
                    yield v_batch
                    del batch[:]


def double_mask(src_file, seq_len, mask_prob_1, mask_prob_2, batch_size, use_mask, random=''):
    wrapped_iter = ds_iter(src_file, seq_len, mask_prob_1, batch_size, to_one_hot=False, random=random)

    while True:
        x, y, mask = next(wrapped_iter)

        x2 = x.copy()
        x2, _ = mask_data(x2, mask_prob_2)

        x = tf.one_hot(x, len(AA_DICT))
        x2 = tf.one_hot(x2, len(AA_DICT))
        y = tf.one_hot(y, len(AA_DICT))

        if use_mask:
            yield {'deep': x, 'shallow': x2}, y, mask
        else:
            yield {'deep': x, 'shallow': x2}, y


if __name__ == '__main__':
    from pathlib import Path

    ROOT = Path(r'C:\DATA\ML-Data\BioML\datasets\Prot2Vec_dataset_2022-06')

    ds_it = ds_iter(ROOT / 'uniref90_tax-free_shuffled.tsv', 64, 0.15, 1024)
    # ds_it = double_mask(ROOT / 'refprot_random_taxfree.tsv', 24, 0.15, 0.35, 32, False, 'full')

    for i in range(1000):
        a = next(ds_it)
        a = np.argmax(a[0], axis=-1), np.argmax(a[1], axis=-1), a[2]
        print()
