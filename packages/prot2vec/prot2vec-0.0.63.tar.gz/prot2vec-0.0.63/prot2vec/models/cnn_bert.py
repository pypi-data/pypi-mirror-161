from keras_pos_embd import PositionEmbedding
from tensorflow.keras.layers import Conv1D, Dropout, Input, Add, Dense, Conv1DTranspose, Embedding
from tensorflow.keras.models import Model

from prot2vec.layers.resnet import add_block_conv1d
from prot2vec.layers.transformer_block import TransformerBlock


def get_model(seq_len=40, seq_depth=21, emb_size=256, n_layers=6, n_heads=8, ff_dim=512, activation='relu', dropout=0.1,
              kernel_size=7, n_strides=5):
    # Input Layer
    input_layer = Input(shape=(seq_len, seq_depth), name='input_layer')
    x = input_layer
    x = Embedding(seq_depth, seq_depth)(x)

    # Transformation of one-hot amino acids sequence with shape=(None, seq_len, seq_depth)
    # to shorter vector sequence sequence with shape=(None, seq_len // n_strides, emb_size)
    x = Conv1D(emb_size, kernel_size, activation=activation, padding='same')(x)
    x = Dropout(dropout)(x)
    x = add_block_conv1d(x, emb_size, kernel_size, activation, dropout)
    x = Conv1D(emb_size, kernel_size, activation=activation, padding='same', strides=n_strides)(x)
    x = Dropout(dropout)(x)

    # Position Embedding
    x = PositionEmbedding(input_dim=seq_len, output_dim=emb_size, mode=PositionEmbedding.MODE_ADD)(x)

    # Transformer Blocks
    skip = x
    for i in range(n_layers):
        if i % 2 == 0 and i > 0:
            x = Add()([skip, x])
            skip = x
        x = TransformerBlock(embed_dim=emb_size, num_heads=n_heads, ff_dim=ff_dim)(x)
    x = Add()([skip, x])

    # Inverse transformation
    # from shape=(None, seq_len // n_strides, emb_size)
    # to shape=(None, seq_len, seq_depth)
    x = Conv1DTranspose(emb_size, kernel_size, padding='same', strides=n_strides)(x)
    x = Dropout(dropout)(x)
    x = add_block_conv1d(x, emb_size, kernel_size, activation, dropout)
    x = add_block_conv1d(x, emb_size, kernel_size, activation, dropout)

    # 'Time' Distributed Dense for amino-acid classification
    x = Dense(seq_depth, activation='softmax')(x)

    output_layer = x

    model = Model(
        inputs=input_layer,
        outputs=output_layer,
        name='cnn_bert')

    return model


if __name__ == '__main__':
    model = get_model()
    print()
