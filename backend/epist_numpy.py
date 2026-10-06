"""EpiST-Former inference in numpy alone.

Why this exists
---------------
The deployed service could not run the published model. TensorFlow was removed
from requirements.txt (commits 9bb4c95, 47aeea4) because it did not fit the
serverless build, so `HAS_TF` was False in production and every response came
from the deterministic fallback -- while the manuscript stated
`fallback_active: false`. Reviewer 4 asked directly which one the live
deployment serves.

Hosting the model somewhere with more memory is one answer. This is a better
one: TensorFlow is needed to *train* this network, not to *run* it. The whole
forward pass is matrix arithmetic, so it is reimplemented here against weights
exported to a 536 KB .npz. The deployed service then runs the real published
model with numpy as its only dependency -- no runtime to size, no memory
ceiling, and nothing to fall back from.

Architecture (read from the saved model, 146,177 parameters)
    input_bio     (21, 3) -> GRU(64, sequences)
    input_weather (21, 3) -> GRU(64, sequences)
        -> MeteorologicalGatedLayer(64)
        -> MultiHeadAttention(4 heads, key_dim 16) + Add + LayerNorm
        -> Dense(64) + Add + LayerNorm
        -> Flatten(1344) -> Dense(64) -> Dropout(inference: identity) -> Dense(1)

Correctness is not assumed: `verify_against_keras.py` loads the original .keras
and asserts agreement to within float tolerance on random inputs. That check
must pass before this file is used to serve anything.
"""
import os
import numpy as np

WEIGHTS = os.path.join(os.path.dirname(__file__), "models",
                       "epist_former_weights.npz")
LOOKBACK = 21
N_BIO = 3
N_WEATHER = 3


def _sigmoid(x):
    # split form avoids overflow warnings on large negative inputs
    out = np.empty_like(x)
    p = x >= 0
    out[p] = 1.0 / (1.0 + np.exp(-x[p]))
    e = np.exp(x[~p])
    out[~p] = e / (1.0 + e)
    return out


def _layernorm(x, gamma, beta, eps=1e-3):
    # Keras LayerNormalization defaults to epsilon=1e-3, not 1e-5
    mu = x.mean(axis=-1, keepdims=True)
    var = x.var(axis=-1, keepdims=True)
    return gamma * (x - mu) / np.sqrt(var + eps) + beta


def _gru(x, kernel, recurrent, bias):
    """Keras GRU, reset_after=True, gate order z (update), r (reset), h (new).

    reset_after matters: with it, the reset gate is applied to the recurrent
    matmul's *output* rather than to the hidden state before the matmul, and
    there are two separate bias vectors. Getting this wrong still produces
    plausible-looking numbers, which is exactly why this is verified against
    Keras rather than eyeballed.
    """
    T, _ = x.shape
    units = recurrent.shape[0]
    b_in, b_rec = bias[0], bias[1]
    xz = x @ kernel[:, :units] + b_in[:units]
    xr = x @ kernel[:, units:2 * units] + b_in[units:2 * units]
    xh = x @ kernel[:, 2 * units:] + b_in[2 * units:]
    h = np.zeros(units, dtype=np.float32)
    seq = np.empty((T, units), dtype=np.float32)
    for t in range(T):
        rz = h @ recurrent[:, :units] + b_rec[:units]
        rr = h @ recurrent[:, units:2 * units] + b_rec[units:2 * units]
        rh = h @ recurrent[:, 2 * units:] + b_rec[2 * units:]
        z = _sigmoid(xz[t] + rz)
        r = _sigmoid(xr[t] + rr)
        hh = np.tanh(xh[t] + r * rh)
        h = z * h + (1.0 - z) * hh
        seq[t] = h
    return seq


def _mha(x, W):
    """Self-attention, 4 heads of key_dim 16, Keras einsum convention."""
    q = np.einsum("td,dhk->thk", x, W["q_k"]) + W["q_b"]
    k = np.einsum("td,dhk->thk", x, W["k_k"]) + W["k_b"]
    v = np.einsum("td,dhk->thk", x, W["v_k"]) + W["v_b"]
    scores = np.einsum("qhk,shk->hqs", q, k) / np.sqrt(q.shape[-1])
    scores -= scores.max(axis=-1, keepdims=True)
    a = np.exp(scores)
    a /= a.sum(axis=-1, keepdims=True)
    ctx = np.einsum("hqs,shk->qhk", a, v)
    return np.einsum("qhk,hkd->qd", ctx, W["o_k"]) + W["o_b"]


class EpiSTFormer:
    """Loads once, predicts many times. Thread-safe: no mutable state."""

    def __init__(self, path=WEIGHTS):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"weights not found at {path}; run pipeline/export_weights.py")
        z = np.load(path)
        g = lambda k: np.asarray(z[k], dtype=np.float32)
        self.gru_bio = (g("gru/cell.0"), g("gru/cell.1"), g("gru/cell.2"))
        self.gru_wx = (g("gru_1/cell.0"), g("gru_1/cell.1"), g("gru_1/cell.2"))
        self.mga = [g(f"meteorological_gated_layer.{i}") for i in range(6)]
        self.mha = {
            "q_k": g("multi_head_attention/query_dense.0"),
            "q_b": g("multi_head_attention/query_dense.1"),
            "k_k": g("multi_head_attention/key_dense.0"),
            "k_b": g("multi_head_attention/key_dense.1"),
            "v_k": g("multi_head_attention/value_dense.0"),
            "v_b": g("multi_head_attention/value_dense.1"),
            "o_k": g("multi_head_attention/output_dense.0"),
            "o_b": g("multi_head_attention/output_dense.1"),
        }
        self.ln1 = (g("layer_normalization.0"), g("layer_normalization.1"))
        self.ln2 = (g("layer_normalization_1.0"), g("layer_normalization_1.1"))
        self.d_ff = (g("dense.0"), g("dense.1"))
        self.d_h = (g("dense_1.0"), g("dense_1.1"))
        self.d_out = (g("dense_2.0"), g("dense_2.1"))
        self.n_params = sum(v.size for v in z.values())

    def predict_one(self, bio, weather):
        """bio, weather: (21, 3) arrays. Returns a scalar prediction."""
        bio = np.asarray(bio, dtype=np.float32).reshape(LOOKBACK, N_BIO)
        wx = np.asarray(weather, dtype=np.float32).reshape(LOOKBACK, N_WEATHER)

        hb = _gru(bio, *self.gru_bio)
        hw = _gru(wx, *self.gru_wx)

        Wg, Wb, We, bg, bb, be = self.mga
        gate = _sigmoid(hw @ Wg + bg)
        h_bio = np.tanh(hb @ Wb + bb)
        h_env = np.tanh(hw @ We + be)
        x = (1.0 - gate) * h_bio + gate * h_env

        x = _layernorm(x + _mha(x, self.mha), *self.ln1)
        # the feed-forward Dense carries a relu (config says activation: relu);
        # leaving it linear produced outputs in the right range but wrong --
        # 42.93 against 36.92 -- which is exactly the kind of error that looks
        # plausible and is caught only by comparing against the real model
        ff = np.maximum(0.0, x @ self.d_ff[0] + self.d_ff[1])
        x = _layernorm(x + ff, *self.ln2)

        flat = x.reshape(-1)
        h = np.maximum(0.0, flat @ self.d_h[0] + self.d_h[1])   # Dense relu
        return float((h @ self.d_out[0] + self.d_out[1])[0])

    def predict(self, bio_batch, weather_batch):
        return np.array([self.predict_one(b, w)
                         for b, w in zip(bio_batch, weather_batch)])


_MODEL = None


def get_model():
    """Lazy singleton, so import never fails a request path."""
    global _MODEL
    if _MODEL is None:
        _MODEL = EpiSTFormer()
    return _MODEL
