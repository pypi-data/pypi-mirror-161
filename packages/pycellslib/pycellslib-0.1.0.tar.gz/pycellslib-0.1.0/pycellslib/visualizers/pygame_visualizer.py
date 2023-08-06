"""
Docs
"""
from os.path import exists

import numpy as np
import pygame as p
import pygame.locals as pl

_EVENTS = None
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "CYAN": (0, 255, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "ORANGE": (255, 165, 0),
    "MAGENTA": (255, 0, 255),
    "SILVER": (192, 192, 192),
    "PURPLE": (128, 0, 128),
    "TEAL": (0, 128, 128),
    "GRAY": (128, 128, 128),
    "RED": (255, 0, 0),
    "BROWN": (165, 42, 42),
    "GOLDEN": (255, 215, 0),
}


def set_events():
    """
    Docs
    """
    global _EVENTS

    _EVENTS = p.event.get()

    return _EVENTS


class System:
    """matrix(automaton) representa el sistema cada numero en la matrix representa un
    color. Colors es un diccionario con numeros como claves y tuplas en
    formato (R, G, B) como valor, states son los posibles
    valores que hay en la matrix. name es el nombre del sistema.
    nullCell es un entero que representa a una celda en la que no hay
    nada. clear, export, add se usa para activar dichas funciones
    """

    def __init__(
        self, automaton, colors, null_cell=0, clear=True, export=True, add=True
    ):
        self.automaton = automaton
        # para que la configuracion inicial se pueda ver en pantalla
        self.automaton.topology.flip()
        self.automaton.topology.set_values_from_configuration(
            self.automaton.topology.get_states(), None
        )
        self.automaton.topology.flip()

        self.height, self.width = automaton.topology.dimensions
        self.colors = colors
        self.states = automaton.cell_information.get_states()
        self.null_cell = null_cell
        self.events = {
            "keydown": [],
            "keyup": [],
            "mousebuttondown": [],
            "mousebuttonup": [],
            "mousemotion": [],
        }
        if clear:
            self.events["keydown"].append(self.clear)
        if export:
            self.events["keydown"].append(self.export)
        if add:
            self.events["mousebuttondown"].append(self.add)

    def get_color(self, i, j):
        offset = self.automaton.topology.get_offset()
        j += offset[1]
        i += offset[0]
        state, _ = self.automaton.topology.get_cell((i, j))
        return self.colors.get(state, "BLACK")

    def get_caption(self):
        return self.automaton.name

    def get_name(self, extention="png"):
        number = 0
        while True:
            name = self.automaton.name + str(number) + "." + extention
            if not exists(name):
                return name
            number += 1

    def clear(self, key):
        """limpia el tablero"""
        if key == "c":
            self.automaton.topology.set_values_from(self.null_cell, None)
            # para que el cambio se pueda ver en pantalla toca hacer unn flip
            self.automaton.topology.flip()
            self.automaton.topology.set_values_from(self.null_cell, None)
            self.automaton.topology.flip()

    def export(self, key):
        """exporta el tablero a un archivo txt"""
        if key == "e":
            np.savetxt(self.get_name("txt"), self.automaton.topology.get_states())
            print("Text saved")

    def add(self, pos, _, added=None):
        """agrega celulas al tablero y retorna el valor agregado en caso de no
        pasar una valor a ser agregado"""
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = self.automaton.topology.get_offset()
            x += offset[1]
            y += offset[0]

            # se obtiene el indice actual del estado en los posibles estados
            state, _ = self.automaton.topology.get_cell((y, x))
            index = self.states.index(state)

            # para que el cambio se pueda ver en pantalla toca hacer unn flip
            self.automaton.topology.flip()
            self.automaton.topology.update_cell(
                (y, x), self.states[(index + 1) % len(self.states)], None
            )
            self.automaton.topology.flip()
            self.automaton.topology.update_cell(
                (y, x), self.states[(index + 1) % len(self.states)], None
            )

    def key_down(self, key):
        for function in self.events["keydown"]:
            function(key)

    def key_up(self, key):
        for function in self.events["keyup"]:
            function(key)

    def mouse_button_down(self, pos, event):
        for function in self.events["mousebuttondown"]:
            function(pos, event)

    def mouse_button_up(self, pos, event):
        for function in self.events["mousebuttonup"]:
            function(pos, event)

    def mouse_motion(self, pos, event):
        for function in self.events["mousemotion"]:
            function(pos, event)

    def update(self):
        """Se debe implementar en las clases que heredan"""
        self.automaton.next_step()


class CellGraph:
    """docstring for CellGraph"""

    def __init__(
        self,
        system,
        margin_width=0,
        margin_height=0,
        background_color=(0, 0, 0),
        cellwidth=5,
        cellheight=5,
        fps=60,
        separation_between_cells=1,
    ):
        self.separation_between_cells = separation_between_cells
        self.background_color = background_color
        self.margin_height = margin_height
        self.margin_width = margin_width
        self.cellheight = cellheight
        self.cellwidth = cellwidth
        self.system = system
        self.fps = fps

        self.width = (
            2 * margin_width
            + cellwidth * system.width
            + separation_between_cells * (system.width - 1)
        )
        self.height = (
            2 * margin_height
            + cellheight * system.height
            + separation_between_cells * (system.height - 1)
        )

    def getPositionInMatrix(self, pos):
        """dada la posicion de la pantalla retorna la posicion en la matrix"""
        posx = pos[0] - self.margin_height
        posy = pos[1] - self.margin_width
        posx = posx / (self.cellwidth + self.separation_between_cells)
        posy = posy / (self.cellheight + self.separation_between_cells)
        return int(posx), int(posy)

    def draw(self, screen):
        """dibuja el sistema en pantalla"""
        screen.fill(self.background_color)
        for i in range(self.system.height):
            for j in range(self.system.width):
                p.draw.rect(
                    screen,
                    self.system.get_color(i, j),
                    p.Rect(
                        self.margin_width
                        + j * self.cellwidth
                        + (j * self.separation_between_cells),
                        self.margin_height
                        + i * self.cellheight
                        + (i * self.separation_between_cells),
                        self.cellwidth,
                        self.cellheight,
                    ),
                )

    def reload(self, screen):
        self.draw(screen)
        if self.pause:
            p.display.set_caption(self.system.get_caption() + " Pause")
        else:
            p.display.set_caption(self.system.get_caption())
        p.display.update()

    def eventManager(self, screen):
        quit = False
        pause = False

        for event in set_events():
            if event.type == p.QUIT:
                quit = True
                break
            if event.type == p.KEYDOWN:
                if event.key == pl.K_p or event.key == pl.K_SPACE:
                    pause = True
                if event.key == pl.K_q:
                    quit = True
                if event.key == pl.K_s:
                    p.image.save(screen, self.system.get_name())
                    print("Saved image")
                self.system.key_down(p.key.name(event.key))
            if event.type == p.MOUSEBUTTONDOWN:
                self.system.mouse_button_down(
                    self.getPositionInMatrix(event.pos), event
                )
            if event.type == p.KEYUP:
                self.system.key_up(event)
            if event.type == p.MOUSEBUTTONUP:
                self.system.mouse_button_up(self.getPositionInMatrix(event.pos), event)
            if event.type == p.MOUSEMOTION:
                self.system.mouse_motion(self.getPositionInMatrix(event.pos), event)

        return quit, pause

    def run(self, manual=False):
        p.display.init()

        screen = p.display.set_mode((self.width, self.height))
        p.display.set_caption(self.system.get_caption())

        clock = p.time.Clock()

        quit = False
        self.pause = True

        self.reload(screen)

        while not quit and not manual:
            clock.tick(self.fps)

            quit, temp = self.eventManager(screen)

            if temp:
                self.pause = not self.pause

            if not self.pause and not quit:
                self.system.update()

            self.reload(screen)

        while not quit and manual:
            pause = False
            while not pause and not quit:
                clock.tick(10)
                quit, pause = self.eventManager(screen)
                self.reload(screen)

                if p.key.get_pressed()[pl.K_SPACE]:
                    pause = True

            if pause and not quit:
                self.pause = True
                self.system.update()

            self.reload(screen)
