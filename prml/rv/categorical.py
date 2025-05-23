import numpy as np

from prml.rv.dirichlet import Dirichlet
from prml.rv.rv import RandomVariable


class Categorical(RandomVariable):
    """
    Categorical distribution
    p(x|mu) = prod_k mu_k^x_k
    """

    def __init__(self, mu=None):
        """
        construct categorical distribution

        Parameters
        ----------
        mu : (n_classes,) np.ndarray or Dirichlet
            probability of each class
        """
        super().__init__()
        self.mu = mu

    @property
    def mu(self):
        return self.parameter["mu"]

    @mu.setter
    def mu(self, mu):
        if isinstance(mu, np.ndarray):
            if mu.ndim != 1:
                raise ValueError("dimensionality of mu must be 1")
            if (mu < 0).any():
                raise ValueError("mu must be non-negative")
            if not np.allclose(mu.sum(), 1):
                raise ValueError("sum of mu must be 1")
            self.n_classes = mu.size
            self.parameter["mu"] = mu
        elif isinstance(mu, Dirichlet):
            self.n_classes = mu.size
            self.parameter["mu"] = mu
        else:
            if mu is not None:
                raise TypeError(f"{type(mu)} is not supported for mu")
            self.parameter["mu"] = None

    @property
    def ndim(self):
        if hasattr(self.mu, "ndim"):
            return self.mu.ndim
        else:
            return None

    @property
    def size(self):
        if hasattr(self.mu, "size"):
            return self.mu.size
        else:
            return None

    @property
    def shape(self):
        if hasattr(self.mu, "shape"):
            return self.mu.shape
        else:
            return None

    def _check_input(self, x):
        assert x.ndim == 2
        assert (x >= 0).all()
        assert (x.sum(axis=-1) == 1).all()

    def _fit(self, x):
        if isinstance(self.mu, Dirichlet):
            self._bayes(x)
        elif isinstance(self.mu, RandomVariable):
            raise NotImplementedError
        else:
            self._ml(x)

    def _ml(self, x):
        self._check_input(x)
        self.mu = np.mean(x, axis=0)

    def _map(self, x):
        self._check_input(x)
        assert isinstance(self.mu, Dirichlet)
        alpha = self.mu.alpha + x.sum(axis=0)
        self.mu = (alpha - 1) / (alpha - 1).sum()

    def _bayes(self, x):
        self._check_input(x)
        assert isinstance(self.mu, Dirichlet)
        self.mu.alpha += x.sum(axis=0)

    def _pdf(self, x):
        self._check_input(x)
        assert isinstance(self.mu, np.ndarray)
        return np.prod(self.mu ** x, axis=-1)

    def _draw(self, sample_size=1):
        assert isinstance(self.mu, np.ndarray)
        return np.eye(self.n_classes)[
            np.random.choice(self.n_classes, sample_size, p=self.mu)
        ]
