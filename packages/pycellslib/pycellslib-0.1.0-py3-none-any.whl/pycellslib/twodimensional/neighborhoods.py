"""
El vecindario de una celula define que celulas condicionan como cambia de
estado cuando se aplica la funcion de transicion. La vecindad de una celula
se representa como una mascara (array de numpy de tipo bool), False indica
que la celula no afecta, y True indica que la celula si afecta. Esta
mascara se superpone en el array que contiene las celulas (en la clase
Topology) usando como coordenadas la posicion de la celula en cuestion mas
un offset (una translacion)

En este modulo se implementan varios tipos de vecindarios usados en la
definicion de automatas celulares 2-dimensionales
"""

import numpy as np

from pycellslib import Neighborhood


class MooreNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de Moore de una celula en un espacio
    2-dimensional

    Parameters
    ----------
    radius(int): radio de la vecindad
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, radius=1, inclusive=True):
        self.radius = radius

        self.mask = np.ones((1 + 2 * radius, 1 + 2 * radius), dtype=np.bool)
        if not inclusive:
            self.mask[radius, radius] = 0

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray(bool)): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return -self.radius, -self.radius


class CircularNeighborhood(Neighborhood):
    """docstring for CircularNeighborhood"""


class L2Neighborhood(Neighborhood):
    """docstring for L2Neighborhood"""


class NeumannNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de Neumann de una celula en un espacio
    2-dimensional

    Parameters
    ----------
    radius(int): radio de la vecindad
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, radius=1, inclusive=True):
        self.radius = radius
        xx, yy = np.meshgrid(
            np.arange(-radius, radius + 1, 1, dtype=np.int),
            np.arange(-radius, radius + 1, 1, dtype=np.int),
            sparse=True,
        )
        self.mask = np.abs(xx) + np.abs(yy)
        self.mask = self.mask <= radius
        if not inclusive:
            self.mask[radius, radius] = 0

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray(bool)): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return -self.radius, -self.radius
