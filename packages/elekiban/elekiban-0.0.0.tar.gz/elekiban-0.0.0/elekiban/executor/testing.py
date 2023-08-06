from pipeline.toolbox import Fauset


class Testing:
    def __init__(self, model_path, faucet: Fauset) -> None:
        self._model = tf.load(model_path)
        self._faucet.compile(optimizer, loss, metrics, loss_weights)
        self._faucet = faucet

    def __call__(self, ):
        self._model.fit_generator(self._faucet.turn_on())
