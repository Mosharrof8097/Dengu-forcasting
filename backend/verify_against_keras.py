"""Assert the numpy forward pass matches the original Keras model.

Shipping an unverified reimplementation would be worse than the status quo: the
service would answer confidently with numbers nobody had checked. This loads the
original .keras, runs both on the same random inputs, and fails loudly on any
disagreement beyond float tolerance.

Needs TensorFlow, so it is a development check, not a runtime dependency.
Run it whenever the weights or epist_numpy.py change.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from epist_numpy import get_model, LOOKBACK, N_BIO, N_WEATHER

HERE = os.path.dirname(os.path.abspath(__file__))
KERAS = os.path.join(HERE, "models", "epist_former_model.keras")
TOL = 2e-4


@keras.utils.register_keras_serializable()
class MeteorologicalGatedLayer(layers.Layer):
    def __init__(self, hidden_dim=64, **kw):
        super().__init__(**kw)
        self.hidden_dim = hidden_dim

    def build(self, input_shape):
        bio_dim, weather_dim = input_shape[0][-1], input_shape[1][-1]
        self.W_gate = self.add_weight(name="W_gate", shape=(weather_dim, self.hidden_dim), initializer="glorot_uniform")
        self.W_bio = self.add_weight(name="W_bio", shape=(bio_dim, self.hidden_dim), initializer="glorot_uniform")
        self.W_env = self.add_weight(name="W_env", shape=(weather_dim, self.hidden_dim), initializer="glorot_uniform")
        self.bias_gate = self.add_weight(name="b_gate", shape=(self.hidden_dim,), initializer="zeros")
        self.bias_bio = self.add_weight(name="b_bio", shape=(self.hidden_dim,), initializer="zeros")
        self.bias_env = self.add_weight(name="b_env", shape=(self.hidden_dim,), initializer="zeros")
        super().build(input_shape)

    def call(self, inputs):
        x_bio, x_weather = inputs
        gate = tf.nn.sigmoid(tf.matmul(x_weather, self.W_gate) + self.bias_gate)
        h_bio = tf.nn.tanh(tf.matmul(x_bio, self.W_bio) + self.bias_bio)
        h_env = tf.nn.tanh(tf.matmul(x_weather, self.W_env) + self.bias_env)
        return (1.0 - gate) * h_bio + gate * h_env

    def get_config(self):
        c = super().get_config(); c.update({"hidden_dim": self.hidden_dim}); return c


@keras.utils.register_keras_serializable()
class AdaptiveSpatialGraphLayer(layers.Layer):
    def __init__(self, num_nodes=11, embedding_dim=16, **kw):
        super().__init__(**kw)
        self.num_nodes, self.embedding_dim = num_nodes, embedding_dim

    def build(self, input_shape):
        self.E1 = self.add_weight(name="node_embedding_1", shape=(self.num_nodes, self.embedding_dim), initializer="glorot_uniform")
        self.E2 = self.add_weight(name="node_embedding_2", shape=(self.num_nodes, self.embedding_dim), initializer="glorot_uniform")
        self.W_spatial = self.add_weight(name="spatial_transform_weight", shape=(input_shape[-1], input_shape[-1]), initializer="glorot_uniform")
        super().build(input_shape)

    def call(self, inputs):
        adj = tf.nn.softmax(tf.nn.relu(tf.matmul(self.E1, self.E2, transpose_b=True)))
        return tf.matmul(adj, tf.matmul(inputs, self.W_spatial))

    def get_config(self):
        c = super().get_config(); c.update({"num_nodes": self.num_nodes, "embedding_dim": self.embedding_dim}); return c


def main():
    km = keras.models.load_model(KERAS, compile=False, custom_objects={
        "MeteorologicalGatedLayer": MeteorologicalGatedLayer,
        "AdaptiveSpatialGraphLayer": AdaptiveSpatialGraphLayer})
    nm = get_model()
    print(f"keras params {km.count_params():,} | numpy params {nm.n_params:,}")

    rng = np.random.default_rng(7)
    N = 64
    # a mix of scales: standardised-looking inputs and raw-count-looking ones,
    # so the comparison is not only valid near zero
    bio = np.concatenate([rng.normal(size=(N // 2, LOOKBACK, N_BIO)),
                          rng.uniform(0, 80, size=(N // 2, LOOKBACK, N_BIO))]).astype("float32")
    wx = np.concatenate([rng.normal(size=(N // 2, LOOKBACK, N_WEATHER)),
                         rng.uniform(-2, 40, size=(N // 2, LOOKBACK, N_WEATHER))]).astype("float32")

    kp = km.predict([bio, wx], verbose=0).reshape(-1)
    np_p = nm.predict(bio, wx)
    diff = np.abs(kp - np_p)
    rel = diff / np.maximum(np.abs(kp), 1e-6)

    print(f"\n{'':4}{'keras':>14}{'numpy':>14}{'abs diff':>12}")
    for i in list(range(4)) + list(range(N // 2, N // 2 + 4)):
        print(f"{i:>4}{kp[i]:>14.6f}{np_p[i]:>14.6f}{diff[i]:>12.2e}")
    print(f"\nmax abs diff {diff.max():.3e} | max rel diff {rel.max():.3e} "
          f"| tolerance {TOL:.0e}")
    if diff.max() > TOL:
        print("\nMISMATCH — the numpy implementation is NOT equivalent. Do not deploy it.")
        return 1
    print("\nPASS — numpy inference reproduces the published model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
