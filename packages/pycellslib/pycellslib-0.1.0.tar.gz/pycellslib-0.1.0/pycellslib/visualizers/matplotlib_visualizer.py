"""
Docs
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap


class ColorPaletteCreator:
    """
    Esta clase brinda una interfaz a la funcion LinearSementedColormap, para
    la creacion de paleta usando un numero discreto de colores

    Parameters
    ----------
    colors(lits(int, RGBA/...)): lista de duplas, en las que la primera
        componente es un entero especificando el estado y el segundo un color
        en el formato RGBA o cualquier otro entendido por matplotlib
    name(str): nombre de la paleta de colores
    """

    def __init__(self, colors, name=""):
        max_color = max(i for i, _ in colors)
        self.colors = [(0, 0, 0)] * (max_color + 1)

        for index, color in colors:
            self.colors[index] = color

        self.cmap = LinearSegmentedColormap.from_list(name, self.colors)

    def set_color(self, state, color):
        """
        Este metodo configura el color para un estado dado

        Parameters
        ----------
        state(int): estado para el que se va a configurar el color
        color(RGBA/...): color especificado en el formato RGBA o cualquier otro
            entendido por matplotlib
        """
        if state >= len(self.colors):
            self.colors.append(color)

        self.colors[state] = color


class GameOfLifeLikePalette(ColorPaletteCreator):
    """
    Esta clase representa una paleta de colores para automatas con estados
    binarios (0/1)

    Parameters
    ----------
    invert(bool): originalmente al estado 0 se le asigna el color blanco y al
        estado 1, el color negor. Si este parametro es True se invierten los
        colores
    """

    def __init__(self, invert=False):
        colors = [[0, "white"], [1, "black"]]

        if invert:
            colors[0][0] = 1
            colors[1][0] = 0

        super().__init__(colors, "Game Of Life")


def update_function(_, axes, palette, interpolation, automaton):
    """
    Funcion usada para la actualizacion de la animacion

    parameters
    -: frame actual en el que se va en la simulacion
    axes(Axes): axes de la figura en matplotlib
    palette(Palette): paleta de colores usada para la graficacion de la imagen
    interpolation(str): interpolacion usada para la graficacion de la imagen
    automaton(Automaton): automata usado en la animacion
    """
    automaton.next_step()
    states = automaton.topology.get_states()
    img = axes.imshow(
        255 * states / states.max(),
        cmap=palette,
        aspect="equal",
        interpolation=interpolation,
    )
    return (img,)


def configure_animation(
    title,
    fontdict={
        "color": "white",
        "family": "sans-serif",
        "fontweight": "bold",
        "fontsize": 16,
    },
    figsize=(5, 5),
    backgroud_color="black",
):
    """
    Esta funcion configura la animacion
    """
    fig = plt.figure(figsize=figsize, facecolor=backgroud_color)
    axes = fig.add_subplot()

    axes.set_title(title, fontdict=fontdict)
    axes.set_xticks([])
    axes.set_yticks([])

    return fig, axes


def animate(
    automaton,
    fig,
    axes,
    palette=GameOfLifeLikePalette().cmap,
    interpolation="None",
    frames=None,
    time_per_frame=50,
    save_count=None,
):
    """
    Esta funcion corre una animacion previamente configurada
    """
    axes.imshow(
        255 * automaton.topology.get_states(), cmap=palette, interpolation=interpolation
    )
    animation = FuncAnimation(
        fig,
        update_function,
        frames=frames,
        fargs=(axes, palette, interpolation, automaton),
        interval=time_per_frame,
        save_count=save_count,
    )
    plt.show()

    return animation
