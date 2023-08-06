# UDFT: Unitary Discrete Fourier Transform (and related)

![licence](https://img.shields.io/github/license/forieux/udft) ![pypi](https://img.shields.io/pypi/v/udft) ![status](https://img.shields.io/pypi/status/udft) ![version](https://img.shields.io/pypi/pyversions/udft) ![maintained](https://img.shields.io/maintenance/yes/2022) [![Documentation Status](https://readthedocs.org/projects/udft/badge/?version=latest)](https://udft.readthedocs.io/en/latest/?badge=latest)

This module implements unitary discrete Fourier transform, that is orthonormal
`det(F) = 1` and `F⁻¹ = F^*`. This module existed before the introduction of the
`norm="ortho"` keyword and is now a very (very) thin wrapper around Numpy,
[pyFFTW](https://pypi.org/project/pyFFTW/), and Scipy (maybe others in the
future), mainly done for my personal usage. There is also functions related to
Fourier and convolution like `ir2fr`.

It is useful for convolution [1]: they respect the Perceval equality, e.g., the
value of the null frequency is equal to `1/√N * ∑ₙ xₙ`.

```
[1] B. R. Hunt "A matrix theory proof of the discrete convolution theorem", IEEE
Trans. on Audio and Electroacoustics, vol. au-19, no. 4, pp. 285-288, dec. 1971
```

If you are having issues, please let me know

francois.orieux AT l2s.centralesupelec.fr

## Installation and documentation

UDFT is just the file `udft.py` and depends on `numpy` and Python 3.7+ only.
Optional dependency are [pyFFTW](https://pypi.org/project/pyFFTW/) and
[scipy](https://scipy.org/). Documentation is
[here](https://udft.readthedocs.io/en/stable/index.html). I recommend using
[poetry](https://python-poetry.org/) for installation

```
   poetry add udft
```
or
```
   poetry add udft[fftw]
```
to install [pyFFTW](https://pypi.org/project/pyFFTW/), or pip
```
   pip install udft
```
For a quick and dirty installation, just copy the `udft.py` file: it is
quite stable, follow the [Semantic
Versioning](https://semver.org/spec/v2.0.0.html), and major changes are
unlikely.

The code is hosted on [GitHub](https://github.com/forieux/udft).

## License

The code is in the public domain.
