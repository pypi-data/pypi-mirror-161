import os

import tensorflow as tf

from ..pipeline.toolbox import AbstractFaucet


def train(model: tf.keras.Model,
          train_faucet: AbstractFaucet,
          valid_faucet: AbstractFaucet,
          epochs: int,
          optimizer=tf.keras.optimizers.Adam(),
          loss=tf.keras.losses.MeanSquaredError(),
          metrics=tf.keras.losses.MeanSquaredError(),
          loss_weights=None,
          output_path="./") -> os.PathLike:

    def allocate_fn(fn):
        if not isinstance(fn, dict):
            return {i_key: fn for i_key in train_faucet.get_output_names()}

    loss = allocate_fn(loss)
    metrics = allocate_fn(metrics)
    save_model = tf.keras.callbacks.ModelCheckpoint(filepath=os.path.join(output_path, "model.h5"),
                                                    monitor="val_loss",
                                                    verbose=1,
                                                    save_best_only=True,
                                                    save_weights_only=False,
                                                    mode="auto")

    try:
        model.summary()
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics, loss_weights=loss_weights)
        model.fit(
            x=train_faucet.turn_on(), batch_size=train_faucet.batch_size, epochs=epochs, steps_per_epoch=train_faucet.iteration,
            validation_data=valid_faucet.turn_on(), validation_batch_size=valid_faucet.batch_size, validation_steps=valid_faucet.iteration,
            callbacks=[save_model]
        )
        return output_path
    except Exception as e:
        print("[*]Fail to training")
        print(e)
