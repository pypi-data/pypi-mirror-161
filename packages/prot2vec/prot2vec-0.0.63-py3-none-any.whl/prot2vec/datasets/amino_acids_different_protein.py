from tqdm import tqdm
import numpy as np

from prot2vec.datasets.amino_acid import line_to_seqtok, vect_batch

TOT_PROTS = 136_671_841

FILE2_OFFSET = 10_000


def ds_iter_(src_file, seq_len, mask_prob, batch_size):
    batch1 = []
    batch2 = []
    line2 = ''

    with open(src_file, "r", encoding="utf-8") as fr1, open(src_file, "r", encoding="utf-8") as fr2:
        fr1.readline()
        fr2.readline()

        for i in range(FILE2_OFFSET):
            fr1.readline()

        for line1 in fr1:
            line2 = fr2.readline()
            while np.random.rand() < 0.5:
                fr1.readline()
            while np.random.rand() < 0.5:
                fr2.readline()

            seq_in1, seq_in2 = line_to_seqtok(line1, seq_len), line_to_seqtok(line2, seq_len)
            if seq_in1 is None or seq_in2 is None:
                continue

            batch1.append(seq_in1)
            batch2.append(seq_in2)

            if len(batch1) >= batch_size:
                assert len(batch1) == len(batch2)
                # TODO-critical: implement different vect_batch
                v_batch1 = vect_batch(batch1, mask_prob)
                v_batch2 = vect_batch(batch2, mask_prob)

                yield v_batch1
                del v_batch1[:]
                del v_batch2[:]

            print()


if __name__ == '__main__':
    from pathlib import Path

    ROOT = Path(r'C:\DATA\ML-Data\BioML\datasets\UniRef90')

    deggen = ds_iter_(ROOT / 'refprot_random_taxfree.tsv', 24, 0.15, 32)

    while True:
        a = next(deggen)
        print()
