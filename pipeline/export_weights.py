#!/usr/bin/env python3
"""Export the trained EpiST-Former to a .npz that `backend/epist_numpy` reads.

Why this file exists
--------------------
It did not. `epist_numpy.py` raised "weights not found; run export_weights.py"
for a script that was never committed, so the 536 KB .npz the service depends
on could not be regenerated from the .keras model. The artifact existed and
the means of producing it did not, which is the same reproducibility gap the
reviewers raised about the dataset.

TensorFlow is needed here and nowhere else in the serving path. Run this once
after training; the service itself never imports it.

    pip install -r requirements-dev.txt
    python pipeline/export_weights.py \
        --model backend/models/epist_former_model.keras \
        --out   backend/models/epist_former_weights.npz

What it guarantees
------------------
`epist_numpy` looks weights up by exact name, so an export that silently used
different names would produce a file that loads and then fails at the first
lookup. This script therefore checks its output against the names that module
requires and refuses to write anything incomplete, reporting what it found
instead.
"""
import argparse
import os
import sys

import numpy as np

# backend/epist_numpy.py looks weights up by exact name, and those names are
# not the layer names in the saved model -- the model calls its layers
# gru_bio, mga_gating, spatiotemporal_attention and output_cases, while the
# .npz calls them gru, meteorological_gated_layer, multi_head_attention and
# dense_2. Reproducing that renaming by rule would be guesswork.
#
# What is stable is the order: Keras returns model.weights in construction
# order, and the i-th weight is the i-th key below. So the mapping is
# positional, and every shape is checked, which catches an architecture change
# immediately rather than producing a file that loads and then misbehaves.
CONTRACT = [
    ("gru/cell.0", (3, 192)),
    ("gru/cell.1", (64, 192)),
    ("gru/cell.2", (2, 192)),
    ("gru_1/cell.0", (3, 192)),
    ("gru_1/cell.1", (64, 192)),
    ("gru_1/cell.2", (2, 192)),
    ("meteorological_gated_layer.0", (64, 64)),
    ("meteorological_gated_layer.1", (64, 64)),
    ("meteorological_gated_layer.2", (64, 64)),
    ("meteorological_gated_layer.3", (64,)),
    ("meteorological_gated_layer.4", (64,)),
    ("meteorological_gated_layer.5", (64,)),
    ("multi_head_attention/query_dense.0", (64, 4, 16)),
    ("multi_head_attention/query_dense.1", (4, 16)),
    ("multi_head_attention/key_dense.0", (64, 4, 16)),
    ("multi_head_attention/key_dense.1", (4, 16)),
    ("multi_head_attention/value_dense.0", (64, 4, 16)),
    ("multi_head_attention/value_dense.1", (4, 16)),
    ("multi_head_attention/output_dense.0", (4, 16, 64)),
    ("multi_head_attention/output_dense.1", (64,)),
    ("layer_normalization.0", (64,)),
    ("layer_normalization.1", (64,)),
    ("dense.0", (64, 64)),
    ("dense.1", (64,)),
    ("layer_normalization_1.0", (64,)),
    ("layer_normalization_1.1", (64,)),
    ("dense_1.0", (1344, 64)),
    ("dense_1.1", (64,)),
    ("dense_2.0", (64, 1)),
    ("dense_2.1", (1,)),
]
N_PARAMS = 146_177


def collect(model):
    """Map the model's weights onto the names epist_numpy reads, by position,
    refusing anything whose shape disagrees."""
    ws = model.weights
    if len(ws) != len(CONTRACT):
        raise SystemExit(
            f"the model has {len(ws)} weights; this exporter expects "
            f"{len(CONTRACT)}. The architecture has changed, so CONTRACT and "
            f"backend/epist_numpy.py must both be updated.")

    out, bad = {}, []
    for w, (key, shape) in zip(ws, CONTRACT):
        arr = np.asarray(w.numpy() if hasattr(w, "numpy") else w, dtype=np.float32)
        if arr.shape != shape:
            bad.append(f"  {key:40s} expected {shape}, model gives "
                       f"{arr.shape}  (from {w.path})")
        out[key] = arr
    if bad:
        raise SystemExit("shape mismatch between the model and the "
                         "contract:\n" + "\n".join(bad))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--model", default=os.path.join(
        here, "..", "backend", "models", "epist_former_model.keras"))
    ap.add_argument("--out", default=os.path.join(
        here, "..", "backend", "models", "epist_former_weights.npz"))
    ap.add_argument("--force", action="store_true",
                    help="write even if the key set does not match what "
                         "epist_numpy requires (for diagnosing a changed "
                         "architecture)")
    a = ap.parse_args()

    sys.path.insert(0, os.path.join(here, "..", "backend"))
    try:
        from tensorflow import keras
        # the two custom layers are defined once, in the verifier, and
        # imported here so there is a single definition to keep correct
        from verify_against_keras import (MeteorologicalGatedLayer,
                                          AdaptiveSpatialGraphLayer)
    except ImportError:
        sys.exit("TensorFlow is not installed. It is needed to read the "
                 ".keras model and for nothing else:\n"
                 "    pip install -r requirements-dev.txt")

    if not os.path.exists(a.model):
        sys.exit(f"model not found at {a.model}")

    model = keras.models.load_model(
        a.model, compile=False,
        custom_objects={"MeteorologicalGatedLayer": MeteorologicalGatedLayer,
                        "AdaptiveSpatialGraphLayer": AdaptiveSpatialGraphLayer})
    w = collect(model)

    total = sum(v.size for v in w.values())

    print(f"model      {a.model}")
    print(f"weights    {len(w)} arrays, {total:,} parameters")
    if total != N_PARAMS:
        print(f"  note: expected {N_PARAMS:,}; the architecture has changed")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez_compressed(a.out, **w)
    size = os.path.getsize(a.out) / 1024
    print(f"\nwrote {a.out}  ({size:.0f} KB)")
    print("Now confirm the port still matches the original:")
    print("    python backend/verify_against_keras.py")


if __name__ == "__main__":
    main()
