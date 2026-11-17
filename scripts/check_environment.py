"""Check the lab environment without downloading data or running exercises."""

import importlib
import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")


def main():
    assert sys.version_info[:2] == (3, 10), sys.version
    modules = (
        "numpy scipy scipy.io scipy.misc pandas matplotlib.pyplot sklearn.datasets "
        "sklearn.linear_model sklearn.metrics sklearn.decomposition h5py PIL.Image "
        "imageio tensorflow keras IPython ipykernel ipywidgets nbformat nbclient "
        "dlai_tools.testing_utils termcolor music21 mido pydub.generators faker "
        "babel.dates emoji tqdm.notebook transformers datasets pyarrow seqeval.metrics "
        "accelerate torch torch.utils.data"
    )
    for name in modules.split():
        importlib.import_module(name)
    print("PASS: all third-party lab dependencies import")

    import numpy as np
    import tensorflow as tf
    import torch
    from tensorflow.keras.layers.experimental.preprocessing import RandomFlip
    from tensorflow.python.framework.ops import EagerTensor
    from keras.engine.functional import Functional
    from tensorflow.python.ops.resource_variable_ops import ResourceVariable
    from tensorflow.keras.optimizers import Adam
    from transformers import (
        DistilBertConfig,
        DistilBertForQuestionAnswering,
        DistilBertTokenizerFast,
        TFDistilBertForQuestionAnswering,
        TFDistilBertForTokenClassification,
        Trainer,
        TrainingArguments,
    )
    import emoji
    from music21 import converter, note, stream
    from pydub import AudioSegment
    from datasets import Dataset, load_from_disk

    assert emoji.emojize(":smile:", use_aliases=True) != ":smile:"
    assert np.__version__ == "1.23.5"
    assert tf.__version__ == "2.10.1"
    assert isinstance(tf.constant(1), EagerTensor)
    model_input = tf.keras.Input(shape=(3,))
    assert type(tf.keras.Model(model_input, tf.keras.layers.Dense(2)(model_input))) == Functional
    Adam(learning_rate=0.001, decay=0.01)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(3,)),
        tf.keras.layers.Dense(2),
    ])
    model.compile(optimizer="adam", loss="mse")
    x = np.ones((2, 3), dtype=np.float32)
    assert np.isfinite(model.train_on_batch(x, np.zeros((2, 2), dtype=np.float32)))
    torch.tensor([1.0], requires_grad=True).square().sum().backward()

    # Exercise the TensorFlow and PyTorch Transformer implementations offline.
    config = DistilBertConfig(
        vocab_size=20, n_layers=1, n_heads=2, dim=8, hidden_dim=16,
        max_position_embeddings=16,
    )
    tokens = tf.constant([[1, 2, 3]])
    assert TFDistilBertForQuestionAnswering(config)(tokens).start_logits.shape == (1, 3)
    assert TFDistilBertForTokenClassification(config)(tokens).logits.shape[:2] == (1, 3)
    assert DistilBertForQuestionAnswering(config)(torch.tensor([[1, 2, 3]])).start_logits.shape == (1, 3)

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        model.save(root / "model.h5")
        restored = tf.keras.models.load_model(root / "model.h5")
        np.testing.assert_allclose(model(x).numpy(), restored(x).numpy())
        Dataset.from_dict({"text": ["lab"]}).save_to_disk(str(root / "dataset"))
        assert load_from_disk(str(root / "dataset"))[0]["text"] == "lab"
        Trainer(model=DistilBertForQuestionAnswering(config), args=TrainingArguments(
            output_dir=str(root / "trainer"), report_to=[], no_cuda=True,
        ))
        score = stream.Stream([note.Note("C4")])
        score.write("midi", fp=str(root / "test.mid"))
        assert len(converter.parse(str(root / "test.mid")).recurse().notes) == 1
        AudioSegment.silent(duration=100).export(str(root / "test.wav"), format="wav")
        assert len(AudioSegment.from_wav(str(root / "test.wav"))) == 100
        # The original style-transfer helper used scipy.misc.imsave (removed).
        repository = Path(__file__).resolve().parents[1]
        style_lab = next(repository.glob("Course 4*/Week 4*/labs/W4A2"))
        sys.path.insert(0, str(style_lab))
        try:
            from nst_utils import save_image
        finally:
            sys.path.pop(0)
        from PIL import Image
        save_image(str(root / "style.png"), np.zeros((1, 4, 4, 3)))
        with Image.open(root / "style.png") as saved:
            assert saved.size == (4, 4)
    print("PASS: TensorFlow training/HDF5, PyTorch, Transformers, datasets, MIDI/WAV and images")

    import nbformat
    from nbclient import NotebookClient

    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(
        "import sys\n"
        f"assert sys.prefix == {sys.prefix!r}, sys.executable\n"
        "import numpy, tensorflow, torch\n"
        "print('kernel-ok')"
    )])
    NotebookClient(notebook, timeout=120, kernel_name="python3").execute()
    assert "kernel-ok" in "".join(output.get("text", "") for output in notebook.cells[0].outputs)
    print("PASS: Jupyter kernel executes using this environment")
    print(f"Python: {sys.executable}")
    print("Environment check passed. Datasets, pretrained models and exercise answers are not checked.")


if __name__ == "__main__":
    main()
