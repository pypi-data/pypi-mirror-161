"""
El vecindario de una celula define que celulas condicionan como cambia de
estado cuando se aplica la funcion de transicion. La vecindad de una celula
se representa como una mascara (array de numpy de tipo bool), False indica
que la celula no afecta, y True indica que la celula si afecta. Esta
mascara se superpone en el array que contiene las celulas (en la clase
Topology) usando como coordenadas la posicion de la celula en cuestion mas
un offset (una translacion)

En este modulo se implementan varios tipos de vecindarios usados en la
definicion de automatas celulares unodimensionales
"""

import numpy as np

from pycellslib import Neighborhood


class LeftCellNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que solo una celula
    a una distancia "r" a la izquierdad afecta en la funcion de transicion

    Params
    ------
    distance(int): distancia de la celula vecina
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, distance=1, inclusive=True):
        self.mask = np.zeros((1, 1 + distance), dtype=np.bool)
        self.mask[0, 0] = 1

        if inclusive:
            self.mask[0, -1] = 1

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
        return 0, -self.mask.size + 1


# es el mismo caso que LeftCellNeighborhood solo que la celula ahora esta a la
# izquierda y la celula vecina a la derecha
class RightCellNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que solo una celula
    a una distancia "r" a la derecha afecta a la funcion de transicion

    Params
    ------
    distance(int): distancia de la celula vecina
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, distance=1, inclusive=True):
        self.mask = np.zeros((1, 1 + distance), dtype=np.bool)
        self.mask[0, -1] = 1

        if inclusive:
            self.mask[0, 0] = 1

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return 0, 0


# esta es una combinacion de LeftCellNeighborhood y de RightCellNeighborhood
class IntervalCellNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que una celula
    a una distancia "r1" a la derecha y una celula a una distancia "r2" a la
    izquierda afecta a la funcion de transicion

    Params
    ------
    left_distance(int): distancia de la celula vecina de la izquierda
    right_distance(int): distancia de la celula vecina de la derecha
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, left_distance=1, right_distance=1, inclusive=True):
        size = left_distance + 1 + right_distance
        self.mask = np.zeros((1, size), dtype=np.bool)

        self.mask[0, 0] = 1
        self.mask[0, -1] = 1
        if inclusive:
            self.mask[0, left_distance] = 1

        self.left_distance = left_distance

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return (0, -self.left_distance)


class LeftSideNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que las celulas hasta
    una distancia "r" a la izquierdad afecta a la funcion de transicion

    Params
    ------
    distance(int): distancia de la ultima celula vecina
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, distance=1, inclusive=True):
        self.mask = np.ones((1, 1 + distance), dtype=np.bool)

        if not inclusive:
            self.mask[0, -1] = 0

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
        return 0, -self.mask.size + 1


# es el mismo caso que LeftCellNeighborhood solo que la celula ahora esta a la
# izquierda
class RightSideNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que las celulas hasta
    una distancia "r" a la izquierdad afecta a la funcion de transicion

    Params
    ------
    distance(int): distancia de la ultima celula vecina
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, distance=1, inclusive=True):
        self.mask = np.ones((1, 1 + distance), dtype=np.bool)

        if not inclusive:
            self.mask[0, 0] = 0

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return 0, 0


# esta es una combinacion de LeftCellNeighborhood y de RightCellNeighborhood
class BothSideNeighborhood(Neighborhood):
    """
    Esta clase representa la vecindad de una celula en la que las celulas hasta
    una distancia "r1" a la izquierdad y las celulas hasta una distancia "r2"
    a la derecha afecta a la funcion de transicion

    Params
    ------
    distance(int): distancia de la ultima celula vecina
    inclusive(bool): si es True, la celula afecta su propia transicion, False
        en caso contrario
    """

    def __init__(self, left_distance=1, right_distance=1, inclusive=True):
        size = left_distance + 1 + right_distance
        self.mask = np.ones((1, size), dtype=np.bool)

        if not inclusive:
            self.mask[0, left_distance] = 0

        self.left_distance = left_distance

    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray): mascara
        """
        return self.mask

    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(int|tuple): valor que indica el offset en cada eje de la mascara
        """
        return (0, -self.left_distance)


# En el caso 1 dimensional los vecindarios Moore, Neumman, L^2, Circular
# coinciden
class DummyNeighborhood(BothSideNeighborhood):
    """
    Clase usada para la definicion de vecindades estandar
    """

    def __init__(self, distance, inclusive=True):
        super().__init__(distance, distance, inclusive)


MooreNeighborhood = DummyNeighborhood
NeummanNeighborhood = DummyNeighborhood
L2Neighborhood = DummyNeighborhood
CircularNeighborhood = DummyNeighborhood
