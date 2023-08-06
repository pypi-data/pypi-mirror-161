from pycellslib import FiniteNGridTopology


class FiniteLineTopology(FiniteNGridTopology):
    """
    La topologia representa la informacion espacial de una automata, esto es,
    tiene encapsulada las dimensiones, la distribucion de las celulas, los
    valores de estados y atributos en cada parte del espacio, metodos
    que extraen y asignan valores a subregiones del espacio...

    Esta clase representa la topologia en la que el espacio se puede visualizar
    como una linea recta finita

    Parameters
    ----------
    attributes_number(int): numero de atributos de cada celula en el espacio
    size(int): dimension del espacio
    border_width(int): dimension de la frontera. Estas dimensiones se le
        suman a las dimensiones del espacio
    """

    def __init__(self, attributes_number, size, border_width):
        super().__init__(attributes_number, (1, size), (0, border_width))
