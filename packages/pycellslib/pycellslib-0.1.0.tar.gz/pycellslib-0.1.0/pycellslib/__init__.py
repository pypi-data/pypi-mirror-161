"""
Este modulo tendra la implementacion de objetos iniciales (que no dependen de
ninguna caracteristica particular de cualquier automata, como la dimensiona-
lidad, ...) tanto abstractos como no abstractos, estos son, aquellos que
codifican la informacion y comportamiento de las celulas (CellularInformation),
de la topologia (Topology, ...), de la vecindad (Neighborhood), la informacion
de las funciones de transicion y de como se relacionan todos estos objetos
entre si (con el objeto Automata)
"""

from abc import ABCMeta, abstractmethod

import numpy as np


class PyCellsLibError(Exception):
    """
    Esta clase solo tiene la intencion de renombrar (se crea un sinonimo), para
    hacer mas claro que errores son creados en la libreria, todas las
    excepciones deben heredar de esta clase
    """


class InitializationWithoutParametersError(PyCellsLibError):
    """
    Esta excepcion debe ser lanzada cuando se intente instanciar un objeto
    sin pasar los parametros requeridos a la clase
    """

    def __init__(self, class_name):
        msg = f"No se puede instanciar {class_name} sin parametros"
        super().__init__(msg)


class InvalidParameterError(PyCellsLibError):
    """
    Esta excepcion debe ser lanzada cuanto se pase un argumento invalido, esto
    es, no esta en el rango requerido, no tenga el tipo adecuado, ...
    """

    def __init__(self, reason_msg):
        msg = f"Parametro invalido, {reason_msg}"
        super().__init__(msg)


class CellInformation(metaclass=ABCMeta):
    """
    Una celula es una entidad que puede tener n estados representados por
    numeros enteros, y que tienen algun nombre, adicionalmente, la celula tiene
    atributos asociados, que son tambien valores numericos con nombre, estos se
    pueden usar para representar variables fisicas (velocidad, ...), variables
    demograficas, ...

    Esta es la clase base de las que deben heredar aquellas clases que brindan
    informacion de los parametros asociados a las celulas de algun automata.
    """

    @abstractmethod
    def get_states(self):
        """
        Este metodo retorna una tupla, lista o arreglo de los posibles estados
        que puede tener una celula

        Returns
        -------
        out(tuple(int)|list(int)|ndarray(int)): Posibles estados que puede
            tener una celula
        """

    @abstractmethod
    def get_number_of_attributes(self):
        """
        Este metodo retorna el numero de atributos que tiene una celula. En
        caso de que la celula no tenga atributos se retorna 0

        Returns
        -------
        out(int): numero de atributos de una celula
        """

    @abstractmethod
    def get_default_state(self):
        """
        Este metodo retorna el valor del estado que tienen las celulas por
        defecto

        Returns
        -------
        out(int): valor del estado por defecto de la celula
        """

    @abstractmethod
    def get_default_value_of_attributes(self):
        """
        Este metodo retorna los valores que tiene una celula por defecto en
        cada atributo. En caso de que la celula no tenga atributos, se retorna
        None

        Returns
        -------
        out(list|ndarray|None): valores por defecto de los atributos de la
            celula.
        """

    # con el objetivo de obtener y mostrar informacion del automata, como
    # densidad o flujo de celulas en un estado, ... se nombran los estados
    @abstractmethod
    def get_name_of_state(self, state):
        """
        Este metodo retorna el nombre asociado a un estado.

        Parameters
        ----------
        state(int): valor del estado del que se desea conocer el nombre

        Returns
        -------
        out(str): nombre del estado, puede ser un string vacio
        """

    # con el objetivo de obtener y mostrar informacion del automata, como
    # densidad, flujos, ... se nombran los atributos, los cuales tienen un
    # orden fijo
    @abstractmethod
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
        out(str|None): nombre del atributo, puede ser un string vacio
        """


class Topology(metaclass=ABCMeta):
    """
    La topologia representa la informacion espacial de una automata, esto es,
    tiene encapsulada las dimensiones, la distribucion de las celulas, los
    valores de estados y atributos en cada parte del espacio, metodos
    que extraen y asignan valores a subregiones del espacio...

    Internamente la clase Topology debe manejar 2 estructuras de datos para
    poder implementar la logica de actualizacion de las celulas (porque esta
    actualizacion se debe realizar en paralelo, es decir, en una de las
    estructuras de datos se van leyendo los valores, para poder calcular cual
    sera el nuevo valor en la siguiente iteracion, y en la otra estructura
    de datos se va escribiendo el nuevo valor de las celulas), por tanto en
    cada una de las estructuras se podra solo realizar una de dos, o escribir
    o leer (este comportamiento se puede modificar con el metodo flip, que
    invierte los papeles de lectura-escritura en las estructuras de datos).
    Ademas estas estructuras deben tener el cuenta el como la clase maneja
    las fronteras (las celulas de la frontera son no actualizables, su unico
    objetivo es el de hacer que todas las celulas actualizables tengan la
    misma condicion para las vecindades)
    """

    @abstractmethod
    def get_offset(self):
        """
        Este metodo debe retornar el offset que se le hacen a las posiciones
        en la matrix para no considerar las celulas de las fronteras en el
        proceso de actualizacion
        """

    @abstractmethod
    def __iter__(self):
        """
        La clase Topology debe brindar una interfaz por la cual se pueda
        iterar por cada celula para realizar el proceso de actualizacion, este
        metodo retorna un iterador sobre las posiciones de las celulas que son
        actualizables (esto es, las que no estan en la frontera)

        Returns
        -------
        out(iter(int)): iterador que recorre cada uno de los indices de las
            celulas que son actualizables
        """

    @abstractmethod
    def flip(self):
        """
        Este metodo cambia el papel (ser de lectura o ser de escritura) que
        cumplen las 2 estructuras de datos en las que se almacenan la
        informacion de estados y atributos de las celulas
        """

    @abstractmethod
    def get_cell(self, position):
        """
        Este metodo obtiene la informacion de una celula, tanto los estados
        como los atributos. Este metodo no permite obtener una celula que esta
        en la frontera

        Parameters
        ----------
        position(tuple(int)|list(int)|ndarray(int)): representan la posicion de
            la celula

        Returns
        -------
        outs(tuple): tupla cuya primera componente es un entero con el valor
            del estado de la celula asociada a la posicion dada, y la segunda
            componente es un array con el valor de los atributos, o None, en
            caso de que las celulas no tenga atributos
        """

    @abstractmethod
    def get_states(self):
        """
        Este metodo retorna los estados de las celulas, no se tiene en cuenta
        la frontera

        Returns
        -------
        out(list(int)|tuple(int)|ndarray(int)): estados de las celulas
        """

    @abstractmethod
    def get_attributes(self):
        """
        Este metodo retorna los atributos de las celulas, no se tiene en cuenta
        la frontera

        Returns
        -------
        out(list(float)|tuple(float)|ndarray(float)): atributos de las celulas
        """

    @abstractmethod
    def update_cell(self, position, cell_state, cell_attributes):
        """
        Este metodo actualiza la informacion de una celula, tanto estados como
        atributos

        Parameters
        ----------
        position(tuple|list): representa la posicion de la celula que sera
            actualizada
        cell_state(int): entero con el valor del estado de la celula
        cell_attributes(list(float)|ndarray(float)|None): lista o arreglo con
            los valores de los atributos. Si las celulas no tienen atributos
            se pasa None
        """

    @abstractmethod
    def set_border_values(self, cell_state, cell_attributes):
        """
        Este metodo establece el valor en los bordes

        Parameters
        ----------
        state_value(int): especifica el valor de los estados en los bordes
        attributes_values(list): especifica el valor de los atributos en los
            bordes, cada elemento de la lista especifica un atributo
        """

    @abstractmethod
    def set_values_from(self, cell_state, cell_attributes):
        """
        Este metodo establece el valor de las celulas usando los mismos
        parametros tanto para los estados, como para los atributos

        Parameters
        ----------
        cell_state(int): entero con el valor de los estados de las celulas
        cell_attributes(list|None): lista o arreglo con los valores de
            los atributos. Si las celulas no tienen atributos se pasa None
        """

    @abstractmethod
    def set_values_from_configuration(self, cell_states, cell_attributes):
        """
        Este metodo establece el valor de las celulas desde un arreglo de
        estados y un arreglo de atributos

        Parameters
        ----------
        cell_states(ndarray(int)): arreglo con los valores de los estados de
            cada celula
        cell_attributes(ndarray(float)|None): arreglo con los valores de los
            atributos de cada celula. Si las celulas no tienen atributos se
            pasa None
        """

    @abstractmethod
    def apply_mask(self, position, mask):
        """
        Este metodo retorna la vecindad de una celula mediante la aplicacion
        de la mascara que representa la vecindad

        Parameters
        ----------
        position(tuple(int)|list(int)): posicion en la que se ubica la mascara
        mask(ndarray): arreglo que representa alguna vecindad

        Returns
        ------
        out(tuple): Tupla donde la primera componente son los estados de las
            celulas que representan la vecindad, y la segunda componente
            representa los atributos de cada celula, si las celulas no tienen
            atributos se retorna None
        """


class Neighborhood(metaclass=ABCMeta):
    """
    El vecindario de una celula define que celulas condicionan como cambia de
    estado cuando se aplica la funcion de transicion. La vecindad de una celula
    se representa como una mascara (array de numpy de tipo bool), False indica
    que la celula no afecta, y True indica que la celula si afecta. Esta
    mascara se superpone en el array que contiene las celulas (en la clase
    Topology) usando como coordenadas la posicion de la celula en cuestion mas
    un offset (una translacion)
    """

    @abstractmethod
    def get_mask(self):
        """
        Este metodo retorna la mascara que define la vecindad de una celula

        Returns
        -------
        out(ndarray(bool)): mascara
        """

    @abstractmethod
    def get_offset(self):
        """
        Este metodo retorna el offset de la mascara

        Returns
        -------
        out(tuple(int)|list(int)|ndarray(int)): valor que indica el offset en
            cada eje de la mascara
        """


class Rule(metaclass=ABCMeta):
    """
    Una regla representa el como cambia el estado de cada celula, esto es,
    representa la vecindad y la funcion de transicion que se aplica a la
    vecindad
    """

    @abstractmethod
    def get_neighborhood(self):
        """
        Este metodo retorna la vecindad asociada a la regla

        Returns
        -------
        out(Neighborhood): Objeto que representa la vecindad
        """

    @abstractmethod
    def apply_rule(self, cell_states, cell_attributes):
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
        out(int|ndarray|list): representa el valor del estado de la celula y
            posiblemente el valor de los atributos de la celula. En caso de
            retornar valor de tipo ndarray o list, entonces la primera
            componente debe ser el valor del estado y las demas componentes,
            los valores de los atributos
        """


class Automaton:
    """
    Un objeto de la clase Automaton encapsula la idea de automata, esta clase
    se encarga de coordinar las clases Cells, Topology y Rules, y ofrece
    metodos para la extraccion de informacion (densidades o de estados o de
    atributos, flujos, ...) del automata
    """

    def __init__(self, cell_information, rule, topology, name=""):
        self.cell_information = cell_information
        self.rule = rule
        self.topology = topology
        self.name = name

        neighborhood = self.rule.get_neighborhood()
        self.mask = neighborhood.get_mask()
        self.offset = neighborhood.get_offset()

    def load_configuration(self, directory):
        """
        Este metodo debe cargar la informacion del automata desde un directorio
        """

    def save_configuration(self, directory):
        """
        Este metodo debe guardar toda la informacion que permita la
        reinstanciacion del automata en cualquier sistema
        """

    def get_density_of_state(self, state):
        """
        Este metodo obtiene la densidad de algun estado en todo el espacio
        """

    def get_densities_of_states(self):
        """
        Este metodo obtiene las densidades de todos los estados en todo el
        espacio
        """

    def get_average_of_attribute(self, index):
        """
        Este metodo obtiene el promedio del atributo especificado (por medio
        del indice) en todo el espacio
        """

    def get_averages_of_attributes(self):
        """
        Este metodo obtiene el promedio de todos los atributos en todo el
        espacio
        """

    def next_step(self):
        """
        Este metodo itera un paso en la ejecucion del automata
        """
        # en el paso anterior, la nueva informacion se escribio en el buffer
        # de escritura, para usarla en el paso de actualizacion, el buffer
        # debe ser cambiado a uno de lectura
        self.topology.flip()

        for position in self.topology:
            mask_position = tuple(
                position[i] + self.offset[i] for i in range(len(position))
            )

            cells, attributes = self.topology.apply_mask(mask_position, self.mask)

            cell, attributes = self.rule.apply_rule(cells, attributes)

            self.topology.update_cell(position, cell, attributes)


class PositionIterator:
    """
    Esta clase representa un iterador sobre posiciones permitidas en el
    espacio

    Parameters
    ----------
    dimensions(ndarray(int)): dimensiones del espacio
    border_widths(ndarray(int)): dimensiones de la frontera del espacio
    """

    def __init__(self, dimensions, border_widths):
        self.dimensions = dimensions
        # dimensiones de la frontera
        self.border_widths = border_widths

        self.index = np.ndindex(*(self.dimensions + self.border_widths))

    def __iter__(self):
        return self

    def __next__(self):
        """
        Este metodo itera sobre todos los posibles indices del espacio y
        retorna solo aquellos que no corresponden a puntos de la frontera
        """
        while True:
            # se revisa que las coordenadas esten en el limite permitido
            coordinate = np.array(next(self.index), dtype=np.int)

            inferior_limit = self.border_widths - 1 < coordinate
            superior_limit = coordinate < self.dimensions + self.border_widths

            if np.all(inferior_limit & superior_limit):
                return tuple(coordinate)

        return coordinate


class FiniteNGridTopology(Topology):
    """
    La topologia representa la informacion espacial de una automata, esto es,
    tiene encapsulada las dimensiones, la distribucion de las celulas, los
    valores de estados y atributos en cada parte del espacio, metodos
    que extraen y asignan valores a subregiones del espacio...

    Esta clase representa una topologia rectangular n-dimensional finita, esto
    es, para 2 dimensiones se puede visualizar como una teselacion de
    rectangulos, para 3 dimensiones como una teselacion de cubos, ...

    Parameters
    ----------
    attributes_number(int): numero de atributos de cada celula en el espacio
    dimensions(tuple(int)|list(int)|ndarray(int)): dimensiones del espacio
    border_widths(tuple(int)|list(int)|ndarray(int)): dimensiones de la
        frontera. Estas dimensiones se le suman a las dimensiones del espacio
    """

    def __init__(self, attributes_number, dimensions, border_widths):
        # numero de atributos de cada celula en el espacio
        self.attributes_number = attributes_number
        # dimensiones del espacio sin tener en cuenta la frontera
        self.dimensions = np.array(dimensions, dtype=np.int)
        # dimensiones de la frontera
        self.border_widths = np.array(border_widths, dtype=np.int)

        # dimensiones reales del espacio, esto es, considerando la frontera
        self.real_dimensions = self.dimensions + 2 * self.border_widths

        # subregion del espacio completo, sin considerar la frontera
        self.subshape = tuple(
            slice(self.border_widths[i], self.dimensions[i] + self.border_widths[i])
            for i in range(self.dimensions.size)
        )

        # el indice 0 corresponde al buffer 1 y el indice 1 corresponde al
        # buffer 2
        self.states = [
            np.zeros(self.real_dimensions, dtype=np.int),
            np.zeros(self.real_dimensions, dtype=np.int),
        ]

        # si se tienen 0 atributos, entonces no hace falta crear un array
        self.attributes = None
        if attributes_number != 0:
            self.attributes = [
                np.zeros((*self.real_dimensions, attributes_number), dtype=np.float),
                np.zeros((*self.real_dimensions, attributes_number), dtype=np.float),
            ]

        # estos atributos llevan la cuenta de que buffer se usa para lectura y
        # que buffer se usa para escritura
        self.write_buffer = 0
        self.read_buffer = 1

    def get_offset(self):
        """
        Este metodo debe retornar el offset que se le hacen a las posiciones
        en la matrix para no considerar las celulas de las fronteras en el
        proceso de actualizacion
        """
        return self.border_widths

    def __iter__(self):
        """
        La clase Topology debe brindar una interfaz por la cual se pueda
        iterar por cada celula para realizar el proceso de actualizacion, este
        metodo retorna un iterador sobre las posiciones de las celulas que son
        actualizables (esto es, las que no estan en la frontera)

        Returns
        -------
        out(iter(list(tuple(int)))): iterador que recorre cada uno de los
            indices de las celulas que son actualizables
        """
        return PositionIterator(self.dimensions, self.border_widths)

    def flip(self):
        """
        Este metodo cambia el papel (ser de lectura o ser de escritura) que
        cumplen las 2 estructuras de datos en las que se almacenan la
        informacion de estados y atributos de las celulas
        """
        self.write_buffer += 1
        self.read_buffer += 1

        self.write_buffer %= 2
        self.read_buffer %= 2

    def get_cell(self, position):
        """
        Este metodo obtiene la informacion de una celula, tanto los estados
        como los atributos. Este metodo no permite obtener una celula que esta
        en la frontera

        Parameters
        ----------
        position(tuple(int)): representan la posicion de la celula

        Returns
        -------
        outs(tuple): tupla cuya primera componente es un entero con el valor
            del estado de la celula asociada a la posicion dada, y la segunda
            componente es un array con el valor de los atributos, o None, en
            caso de que las celulas no tenga atributos
        """
        state = self.states[self.read_buffer][position]

        attributes = None
        if self.attributes is not None:
            attributes = self.attributes[self.read_buffer][position]

        return state, attributes

    def get_states(self):
        """
        Este metodo retorna los estados de las celulas, no se tiene en cuenta
        la frontera

        Returns
        -------
        out(ndarray(int)): estados de las celulas
        """
        return self.states[self.read_buffer][self.subshape]

    def get_attributes(self):
        """
        Este metodo retorna los atributos de las celulas, no se tiene en cuenta
        la frontera

        Returns
        -------
        out(ndarray(float)): atributos de las celulas
        """
        return self.attributes[self.read_buffer][self.subshape]

    def update_cell(self, position, cell_state, cell_attributes):
        """
        Este metodo actualiza la informacion de una celula, tanto estados como
        atributos

        Parameters
        ----------
        position(tuple(int)): representa la posicion de la celula que sera
            actualizada
        cell_state(int): entero con el valor del estado de la celula
        cell_attributes(list(float)|ndarray(float)|None): lista o arreglo con
            los valores de los atributos. Si las celulas no tienen atributos
            se pasa None
        """
        self.states[self.write_buffer][position] = cell_state

        if self.attributes is not None:
            self.attributes[self.write_buffer][position] = cell_attributes

    def set_border_values(self, cell_state, cell_attributes):
        """
        Este metodo establece el valor en los bordes

        Parameters
        ----------
        cell_state(int): especifica el valor de los estados en los bordes
        cell_attributes(list(float)|ndarray(float)|None): especifica el valor
            de los atributos en los bordes, cada elemento de la lista
            especifica un atributo
        """
        # se crea mascara para establecer el valor en los bordes
        mask = np.ones(self.real_dimensions, dtype=np.bool)
        # el subshape no hace parte de la frontera
        mask[self.subshape] = 0
        self.states[self.write_buffer][mask] = cell_state

        if self.attributes is not None:
            self.attributes[self.write_buffer][mask] = cell_attributes

    def set_values_from(self, cell_state, cell_attributes):
        """
        Este metodo establece el valor de las celulas usando los mismos
        parametros tanto para los estados, como para los atributos

        Parameters
        ----------
        cell_state(int): entero con el valor de los estados de las celulas
        cell_attributes(list(float)|ndarray(float)|None): especifica el valor
            de los atributos, si la celula no tiene atributos se pasa None
        """
        self.states[self.write_buffer][self.subshape] = cell_state

        if self.attributes is not None:
            self.attributes[self.write_buffer][self.subshape] = cell_attributes

    def set_values_from_configuration(self, cell_states, cell_attributes):
        """
        Este metodo establece el valor de las celulas desde un arreglo de
        estados y un arreglo de atributos

        Parameters
        ----------
        cell_states(ndarray(int)): arreglo con los valores de los estados de
            cada celula
        cell_attributes(ndarray(float)|None): arreglo con los valores de los
            atributos de cada celula. Si las celulas no tienen atributos se
            pasa None
        """
        self.states[self.write_buffer][self.subshape] = cell_states

        if self.attributes is not None:
            self.attributes[self.write_buffer][self.subshape] = cell_attributes

    def apply_mask(self, position, mask):
        """
        Este metodo retorna la vecindad de una celula mediante la aplicacion
        de la mascara que representa la vecindad

        Parameters
        ----------
        position(tuple(int)): posicion en la que se ubica la mascara, esta
            posicion debe tener en cuenta la frontera y las dimensiones de la
            mascara
        mask(ndarray): arreglo que representa alguna vecindad

        Returns
        ------
        out(tuple): Tupla donde la primera componente es un array con los
            estados de las celulas que representan la vecindad, y la segunda
            componente un array con los atributos de cada celula, si las
            celulas no tienen atributos se retorna None
        """
        # se extrae la region en donde se aplicara la mascara
        subshape = tuple(
            slice(position[i], position[i] + mask.shape[i])
            for i in range(len(mask.shape))
        )

        states = self.states[self.read_buffer][subshape][mask]

        attributes = None
        if self.attributes is not None:
            attributes = self.attributes[self.read_buffer][subshape][mask]

        return states, attributes
