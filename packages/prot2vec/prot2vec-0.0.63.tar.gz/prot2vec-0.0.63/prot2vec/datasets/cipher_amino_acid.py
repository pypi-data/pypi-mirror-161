import numpy as np
import tensorflow as tf
import json

AA_DICT = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4,
           'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
           'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14,
           'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19,
           '?': 20}
AA_COUNT = len(AA_DICT)
AA_DICT_REV = {AA_DICT[key]: key for key in AA_DICT}


class CipherAminoAcidDs(object):
    def __init__(self, src_file, seq_len, mask_prob, batch_size, n_of_ciphers=100, random_style='', cipher_src=None):
        self.src_file = src_file
        self.seq_len = seq_len
        self.mask_prob = mask_prob
        self.batch_size = batch_size
        self.n_of_ciphers = n_of_ciphers
        self.random_style = random_style

        if cipher_src is None:
            self.create_ciphers(n_of_ciphers)
        else:
            self.load_cipher(cipher_src)

        self.fr = open(src_file, "r", encoding="utf-8")
        self.fr.readline()

    def __iter__(self):
        return self

    def __next__(self):
        batch = []
        while True:
            line = self.fr.readline()
            if len(line) < 1:
                self.fr.close()
                self.fr = open(self.src_file, "r", encoding="utf-8")
                self.fr.readline()
                line = self.fr.readline()

            _, _, seq = line[:-1].split('\t')
            prot_len = len(seq)
            if prot_len <= self.seq_len:
                continue

            offset = np.random.randint(0, prot_len - self.seq_len)
            seq = seq[offset:offset + self.seq_len]

            if self.random_style == 'full':
                seq = ''.join(list(map(lambda x: AA_DICT_REV[x], np.random.randint(0, 20, self.seq_len))))

            seq_in = self.tokenize(seq)

            if seq_in is None:
                continue

            batch.append(seq_in)

            if len(batch) >= self.batch_size:
                v_batch = self.vect_batch(batch, self.mask_prob)
                return v_batch

    def load_cipher(self, src):
        with open(src, 'r', encoding='utf-8') as fr:
            ciphers = json.load(fr)

        self.ciphers = {int(key): np.array(ciphers[key]) for key in ciphers}

    def create_ciphers(self, n_of_ciphers):
        np.random.seed(42)

        self.ciphers = {i: np.zeros((AA_COUNT,), dtype='int32') for i in range(n_of_ciphers)}

        for i in range(n_of_ciphers):
            tokens_in = [*range(AA_COUNT)]
            for j in range(AA_COUNT):
                sel = np.random.randint(0, len(tokens_in))
                self.ciphers[i][j] = tokens_in.pop(sel)

    def encrypt(self, x, selected_ciphers):
        for i, cipher in enumerate(selected_ciphers):
            x[i] = np.array(list(map(lambda y: self.ciphers[cipher][y], x[i])))

        return x

    def tokenize(self, seq):
        digit_seq = list(map(lambda x: AA_DICT[x], seq))
        digit_seq = np.array(digit_seq)[None, :]
        return digit_seq

    def mask_data(self, data, mask_prob):
        bool_mask = np.random.rand(data.shape[0] * data.shape[1]) < mask_prob
        bool_mask = bool_mask.reshape(data.shape)

        to_replace = data[bool_mask]
        replacement = np.ones(to_replace.shape, dtype='int32') * AA_DICT['?']
        data[bool_mask] = replacement

        return data, bool_mask

    def vect_batch(self, batch, mask_prob):
        x = np.concatenate(batch, axis=0)

        selected_ciphers = np.random.randint(0, self.n_of_ciphers, self.batch_size)

        x = self.encrypt(x, selected_ciphers)
        y = selected_ciphers
        x, _ = self.mask_data(x, mask_prob)
        x = tf.one_hot(x, len(AA_DICT))
        y = tf.one_hot(y, self.n_of_ciphers)

        return x, y


if __name__ == '__main__':
    from pathlib import Path

    ROOT = Path(r'C:\DATA\ML-Data\BioML\datasets\Prot2Vec_dataset_2022-06')

    degen = CipherAminoAcidDs(ROOT / 'swissprot_shuffled.tsv', 24, 0.15, 32,
                              cipher_src=r'C:\DATA\ML-Data\BioML\other\sequence_encryption\ciphers.json')

    while True:
        print()
        a = next(degen)
        print()
