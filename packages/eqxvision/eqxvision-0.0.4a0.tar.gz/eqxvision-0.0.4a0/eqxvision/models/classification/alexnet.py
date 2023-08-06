from typing import Any, Optional

import equinox as eqx
import equinox.nn as nn
import jax
import jax.nn as jnn
import jax.numpy as jnp
import jax.random as jrandom
from equinox.custom_types import Array

from ...layers import Activation


model_urls = {
    "alexnet": "https://download.pytorch.org/models/alexnet-owt-7be5be79.pth",
}


class AlexNet(eqx.Module):
    """A simple port of torchvision.models.alexnet"""

    features: eqx.Module
    avgpool: eqx.Module
    classifier: eqx.Module

    def __init__(
        self,
        num_classes: int = 1000,
        dropout: float = 0.5,
        *,
        key: Optional["jax.random.PRNGKey"] = None
    ) -> None:
        """**Arguments:**

        - `num_classes`: Number of classes in the classification task.
                        Also controls the final output shape `(num_classes,)`. Defaults to `1000`.
        - `dropout`: Parameter used for the `equinox.nn.Dropout` layers. Defaults to `0.5`.
        - `key`: A `jax.random.PRNGKey` used to provide randomness for parameter
            initialisation. (Keyword only argument.)

        ???+ note "JIT call:"

            ```python
            @eqx.filter_jit
            def forward(model, x, key):
               keys = jax.random.split(key, x.shape[0])
               output = jax.vmap(model)(x, key=keys)
               ...
            ```
        """
        super().__init__()
        if not key:
            key = jrandom.PRNGKey(0)
        keys = jrandom.split(key, 8)

        self.features = nn.Sequential(
            [
                nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2, key=keys[0]),
                Activation(jnn.relu),
                nn.MaxPool2d(kernel_size=3, stride=2),
                nn.Conv2d(64, 192, kernel_size=5, padding=2, key=keys[1]),
                Activation(jnn.relu),
                nn.MaxPool2d(kernel_size=3, stride=2),
                nn.Conv2d(192, 384, kernel_size=3, padding=1, key=keys[2]),
                Activation(jnn.relu),
                nn.Conv2d(384, 256, kernel_size=3, padding=1, key=keys[3]),
                Activation(jnn.relu),
                nn.Conv2d(256, 256, kernel_size=3, padding=1, key=keys[4]),
                Activation(jnn.relu),
                nn.MaxPool2d(kernel_size=3, stride=2),
            ]
        )
        self.avgpool = nn.AdaptiveAvgPool2d((6, 6))
        self.classifier = nn.Sequential(
            [
                nn.Dropout(p=dropout),
                nn.Linear(256 * 6 * 6, 4096, key=keys[5]),
                Activation(jnn.relu),
                nn.Dropout(p=dropout),
                nn.Linear(4096, 4096, key=keys[6]),
                Activation(jnn.relu),
                nn.Linear(4096, num_classes, key=keys[7]),
            ]
        )

    def __call__(self, x: Array, *, key: "jax.random.PRNGKey") -> Array:
        """**Arguments:**

        - `x`: The input. Should be a JAX array with `3` channels.
        - `key`: Utilised by few layers in the network such as `Dropout` or `BatchNorm`.
        """
        if key is None:
            raise RuntimeError("The model requires a PRNGKey.")
        keys = jrandom.split(key, 2)
        x = self.features(x, key=keys[0])
        x = self.avgpool(x)
        x = jnp.ravel(x)
        x = self.classifier(x, key=keys[1])
        return x


def alexnet(**kwargs: Any) -> AlexNet:
    r"""AlexNet model architecture from the
    `"One weird trick..." <https://arxiv.org/abs/1404.5997>`_ paper.
    The required minimum input size of the model is 63x63.

    """
    model = AlexNet(**kwargs)
    # TODO: Add comptability with torch weights
    return model
