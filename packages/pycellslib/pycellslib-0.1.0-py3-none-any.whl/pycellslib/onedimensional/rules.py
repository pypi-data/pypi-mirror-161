import numpy as np

from pycellslib import Rule
from pycellslib.onedimensional.neighborhoods import MooreNeighborhood


class WolframCodeRule(Rule):
    """
    Esta clase representa las reglas de transicion denotadas mediante el codigo
    de wolfram para automatas unidimensionales

    Parameters
    ----------
    rule_number(int): numero que representa la regla
    states_number(int): numero de todos los estados posibles de las celulas
    neighborhood_radius(int): en este formato de especificacino de las reglas
        se debe usar una vecindad de Moore, este parametro representa el radio
        de esa vecindad
    """

    def __init__(self, rule_number, states_number=2, neighborhood_radius=1):
        # la base esta determinada por todos lo posibles estados de las celulas
        self.base = states_number
        # numero de vecinos en la vecindad
        size = 2 * neighborhood_radius + 1
        # elementos que forman la base, esto es, las potencias de la base
        self.base_elements = self.base ** np.arange(size - 1, -1, -1)

        # todas las posibles configuraciones de las vecindades
        self.neighborhood_configurations = self.base**size
        self.neighborhood = MooreNeighborhood(neighborhood_radius)

        # la regla se pasa como un numero entero, que tiene que ser traducida
        # en la representacion de self.base
        self.rule = self.get_base_representation(rule_number)

    def get_neighborhood(self):
        """
        Este metodo retorna la vecindad asociada a la regla

        Returns
        -------
        out(Neighborhood): Objeto que representa la vecindad
        """
        return self.neighborhood

    def get_max_rule_number(self):
        """
        Este metodo retorna la maxima regla permitida con el numero de estados
        y la vecindad actual
        """
        return self.base**self.neighborhood_configurations - 1

    def get_base_representation(self, number):
        """
        Este metodo convierte un entero a la base usada por la clase, usando
        tantas cifras como numero de configuraciones de los vecinos hayan

        Parameters
        ----------
        number(int): numero entero a cambiar de base

        Returns
        -------
        out(ndarray(int)): representacion del entero pasado como parametro en
            la base usada por la clase
        """
        # se convierte el numero a la base deseada
        base_number = list(map(int, np.base_repr(number, self.base)))

        # si la longitud de la lista es mayor que la de todas las posibles
        # configuraciones de los vecinos, entonces se esta pasando una regla
        # que no esta definida, no tiene sentido en la base actual
        if len(base_number) > self.neighborhood_configurations:
            raise Exception("Fuera de rango")

        # la lista con la representacion del numero siempre debe tener la
        # longitud determinada por el numero de configuraciones posibles de los
        # vecinos, entonces se hace un padding a la izquierda de ser necesario
        diff = self.neighborhood_configurations - len(base_number)
        if diff > 0:
            base_number = [0] * diff + base_number

        return np.array(base_number)

    def base_representation_to_int(self, base_representation):
        """
        Este metodo convierte un numero especificado en la base numerica usada
        por la clase a entero

        Parameters
        ----------
        base_representation(ndarray(int)): representacion de un entero la base
            numerica usada en la clase

        Returns
        -------
        out(int): entero que representa al parametro de entrada
        """
        return np.sum(self.base_elements * base_representation)

    def apply_rule(self, cell_states, cell_attributes=None):
        """
        Este metodo aplica las reglas de transicion a una vecindad de la
        celula

        Parameters
        ----------
        cell_states(ndarray(int)): arreglo que representa los estados de la
            vecindad de una celula (es retornado por el metodo apply_mask de
            la clase topology)
        cell_attributes(ndarray(float)): arreglo que representa los atributos
            de la vecindad de una celula (es retornado por el metodo apply_mask
            de la clase topology)

        Returns
        -------
        out(int): representa el valor del siguiente estado de la celula
        """
        neighborhood_configuration = self.base_representation_to_int(cell_states)

        return (
            self.rule[
                self.neighborhood_configurations - 1 - neighborhood_configuration
            ],
            None,
        )
