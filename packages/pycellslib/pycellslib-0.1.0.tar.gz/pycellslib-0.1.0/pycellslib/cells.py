"""
Una celula es una entidad que puede tener n estados representados por
numeros enteros, y que tienen algun nombre, adicionalmente, la celula tiene
atributos asociados, que son tambien valores numericos con nombre, estos se
pueden usar para representar variables fisicas (velocidad, ...), variables
demograficas, ...

En este modulo se implementan las celulas mas comunes (celula del juego de la
vida, ...) usadas en automatas celulares
"""

from pycellslib import CellInformation


class StandardCell(CellInformation):
    """
    Esta clase representa una celula estandar, esto es, aquellas que no tienen
    atributos

    Parameters
    ----------
    start(int|list(int)|tuple(int)|ndarray(int)): parametro usado para
        especificar los posibles estados del automata, cuando se pasa un
        iterable. Pero start toma un valor entero, se usa para especificar
        el rango en el que estan los estados
    end(int|None): cuando el parametro start es un entero, este parametro es
        usado para especificar el rango en el que estan los estados
    step(int|None): cuando el parametro start es un entero, este parametro es
        usado para especificar que enteros en el rango especificado hacen
        parte de los posibles estados
    default_state(int|None): valor por defecto que se usa para los estados
    name_of_states(list(str)|tuple(str)|None): nombre de cada estado
    """

    def __init__(
        self, start=None, end=None, step=None, default_state=None, name_of_states=None
    ):
        if isinstance(start, list):
            self.states = start
        else:
            # start debe ser int
            self.states = list(range(start if end else 0, end or start, step or 1))

        self.default_state = default_state or self.states[0]

        self.name_of_states = name_of_states or []
        diff = len(self.states) - len(self.name_of_states)
        self.name_of_states.extend([""] * diff)

    def get_states(self):
        """
        Este metodo retorna los posibles estados que puede tener una celula

        Returns
        -------
        out(list(int)): Posibles estados que puede tener una celula
        """
        return self.states

    def get_number_of_attributes(self):
        """
        Este metodo retorna el numero de atributos que tiene una celula. En
        caso de que la celula no tenga atributos se retorna 0

        Returns
        -------
        out(int): numero de atributos de una celula
        """
        return 0

    def get_default_state(self):
        """
        Este metodo retorna el valor del estado que tienen las celulas por
        defecto

        Returns
        -------
        out(int): valor del estado por defecto de la celula
        """
        return self.default_state

    def get_default_value_of_attributes(self):
        """
        Este metodo retorna los valores que tiene una celula por defecto en
        cada atributo. En caso de que la celula no tenga atributos, se retorna
        None

        Returns
        -------
        out(None): valores por defecto de los atributos de la celula.
        """
        return None

    # con el objetivo de obtener y mostrar informacion del automata, como
    # densidad o flujo de celulas en un estado, ... se nombran los estados
    def get_name_of_state(self, state):
        """
        Este metodo retorna el nombre asociado a un estado.

        Parameters
        ----------
        state(int): valor del estado del que se desea conocer el nombre

        Returns
        -------
        out(str): nombre del estado
        """
        return self.name_of_states[state]

    # con el objetivo de obtener y mostrar informacion del automata, como
    # densidad, flujos, ... se nombran los atributos, los cuales tienen un
    # orden fijo
    def get_name_of_attributes(self, index):
        """
        Este metodo retorna el nombre del atributo asociado a un indice, el
        indice cuenta desde cero. Se retorna None en caso de que la celula no
        tenga atributos

        Parameters
        ----------
        index(int): indice que corresponde al atributo

        Returns
        -------
        out(None): nombre del atributo, puede ser un string vacio
        """
        return None


class LifeLikeCell(StandardCell):
    """
    Esta clase representa a las celulas que se usan en el juego de la vida
    """

    def __init__(self):
        super().__init__([0, 1], name_of_states=["Dead", "Alive"])
