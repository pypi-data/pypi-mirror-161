"""
Una regla representa el como cambia el estado de cada celula, esto es,
representa la vecindad y la funcion de transicion que se aplica a la
vecindad

En este modulo se implementan las reglas para la definicion de automatas
celulares bidimensionales
"""
import numpy as np

from pycellslib import Rule
from pycellslib.twodimensional.neighborhoods import MooreNeighborhood


class BSNotationRule(Rule):
    """
    Esta clase representa las reglas de transicion denotadas con la notacion
    B/S Notation

    Parameters
    ----------
    B(list(int)): lista de los enteros que ocacionan a una celula muerta, nacer
    S(list(int)): lista de los enteros que permiten que una celula viva
        sobreviva
    radius(int): en este formato de especificacino de las reglas
        se debe usar una vecindad de Moore, este parametro representa el radio
        de esa vecindad
    """

    def __init__(self, B, S, radius=1):
        self.B = B
        self.S = S
        self.radius = radius
        self.neighborhood = MooreNeighborhood(radius=radius, inclusive=True)

    def get_neighborhood(self):
        """
        Este metodo retorna la vecindad asociada a la regla

        Returns
        -------
        out(Neighborhood): Objeto que representa la vecindad
        """
        return self.neighborhood

    def apply_rule(self, cell_states, _):
        """
        Este metodo aplica la regla a una vecindad de alguna celula

        Params
        ------
        cell_states(ndarray(int)): estados de las celulas vecinas

        Returns
        -------
        out(int): estado de la celula en la siguiente iteracion
        """
        # indice de la celula del centro
        current_cell = cell_states[cell_states.size // 2]
        # para no contar a la celula del centro se establece el valor a cero
        cell_states[cell_states.size // 2] = 0

        alive_cells = np.sum(cell_states)

        new_state = 0
        if current_cell == 1:
            if self.S == []:
                new_state = 0
            if alive_cells in self.S:
                new_state = 1

        if current_cell == 0:
            if self.B == []:
                new_state = 1
            if alive_cells in self.B:
                new_state = 1

        return new_state, None
