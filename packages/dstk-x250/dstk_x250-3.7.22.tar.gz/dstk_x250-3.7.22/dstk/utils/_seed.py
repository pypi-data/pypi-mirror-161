#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonction d'initialisation des seed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Thu May 19 09:51:12 2022

@author: Cyrile Delestre
"""

import random

import numpy as np


def set_seed(seed: int, cuda: bool=True):
    r"""
    Fonction permettant d'initialiser tous
    les générateurs pseudo-aléatoire (Python +
    numpy + PyTorch si possible + cuda si possible).
    Permettant d'assurer la reproductivité d'une expérience.

    Parameters
    ----------
    seed: int
        Racine souhaitée.
    cuda: bool (=True)
        Indique si l'initialisation doit être fait sur le backend cuda
        si celui-ci est disponible ou non.
    """
    random.seed(seed)
    # la seed de numpy est de précision 2**32
    np.random.seed(seed % 2**32)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available() > 0 and cuda:
            torch.cuda.manual_seed_all(seed)
    except ModuleNotFoundError:
        pass
