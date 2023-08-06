from pycellslib import FiniteNGridTopology


class FinitePlaneTopology(FiniteNGridTopology):
    """
    La topologia representa la informacion espacial de una automata, esto es,
    tiene encapsulada las dimensiones, la distribucion de las celulas, los
    valores de estados y atributos en cada parte del espacio, metodos
    que extraen y asignan valores a subregiones del espacio...

    Esta clase representa la topologia que se puede visualizar como un plano
    rectangular finito

    Parameters
    ----------
    attributes_number(int): numero de atributos por celula
    width(int): ancho del espacio
    height(int): alto del espacio
    border_width(int): ancho de la frontera
    border_height(int): alto de la frontera
    """

    def __init__(self, attributes_number, width, height, border_width, border_height):
        super().__init__(
            attributes_number, (height, width), (border_height, border_width)
        )
