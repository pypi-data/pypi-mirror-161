from tensorflow.keras.layers import Conv1D, Dropout, Add, Dense


def add_block_conv1d(x, kernel_count, kernel_size, activation, dropout):
    skip = x
    x = Conv1D(kernel_count, kernel_size, activation=activation, padding='same')(x)
    x = Dropout(dropout)(x)
    x = Conv1D(kernel_count, kernel_size, activation=activation, padding='same')(x)
    x = Add()([x, skip])
    x = Dropout(dropout)(x)

    return x


def add_block_dense(x, n_neurons, activation, dropout):
    skip = x
    x = Dense(n_neurons, activation=activation, padding='same')(x)
    x = Dropout(dropout)(x)
    x = Dense(n_neurons, activation=activation, padding='same')(x)
    x = Add()([x, skip])
    x = Dropout(dropout)(x)

    return x
