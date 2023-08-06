import curses as c
import os
import time
from abc import ABCMeta, abstractmethod

import numpy as np

os.environ.setdefault("ESCDELAY", "25")


# indice de colores de curses
COLOR_SELECTED_ELEMENT = 1

# eventos que representan a que ventana se debe ir en la siguiente iteracion
PRESENTATION = 0
SIMULATION = 1
CONFIGURATIONS = 2
CREDITS = 3
QUIT = 4


class TestAutomata:
    """docstring for TestAutomata"""

    def __init__(self):
        self.states = [
            np.zeros((13, 13), dtype=np.int),
            np.zeros((13, 13), dtype=np.int),
        ]

        # self.states[0][5:8, 5:8] = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        # self.states[0][5:8, 5:8] = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        self.states[0][5:8, 5:8] = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
        self.states[1][5:8, 5:8] = [[0, 0, 0], [1, 1, 1], [0, 0, 0]]

        self.index = 0

    def get_states(self):
        self.index = (self.index + 1) % 2
        return self.states[self.index]


class Writable:
    """docstring for Writable"""

    def __init__(self, text, position):
        self.text = text
        self.position = position

    def write(self, window):
        """ """
        height, width = window.getmaxyx()

        for y in range(len(self.text)):
            for x in range(len(self.text[y])):
                column = self.position[1] + x
                row = self.position[0] + y

                # solo se debe dibujar lo que este dentro de la ventana
                if 0 < row < height - 1 and 0 < column < width - 1:
                    window.addch(row, column, self.text[y][x])


class Panel(metaclass=ABCMeta):
    """docstring for Panel"""

    @abstractmethod
    def handle_input(self, char):
        """ """

    @abstractmethod
    def write(self, window):
        """ """


class Window(metaclass=ABCMeta):
    """"""

    @abstractmethod
    def handle_input(self, char):
        """ """

    @abstractmethod
    def write(self):
        """ """


class ConfigurationInformationPanel(Panel):
    """docstring for ConfigurationInformation"""

    def __init__(self, window):
        self.window = window
        self.message = Writable(
            ["Informacion", "de configuraciones", "de la simulacion"], (1, 1)
        )

    def handle_input(self, char):
        """ """

    def write(self):
        """ """
        self.window.box()
        self.message.write(self.window)
        self.window.refresh()


class SimulationInformationPanel(Panel):
    """docstring for SimulationInformation"""

    def __init__(self, window):
        self.window = window
        self.message = Writable(["Informacion", "de la simulacion"], (1, 1))

    def handle_input(self, char):
        """ """

    def write(self):
        """ """
        self.window.box()
        self.message.write(self.window)
        self.window.refresh()


class SimulationPanel(Panel):
    """docstring for SimulationPanel"""

    def __init__(self, window, automata):
        self.window = window
        self.automata = automata
        self.states = Writable("", (1, 1))

    def states_to_string(self, states):
        string = []

        for i in range(len(states)):
            line = ""
            for j in range(len(states[i])):
                if states[i][j] == 1:
                    line += "*"
                else:
                    line += " "

            string.append(line)

        return string

    def handle_input(self, char):
        """ """

    def write(self):
        """ """
        self.window.box()
        self.states.text = self.states_to_string(self.automata.get_states())
        self.states.write(self.window)
        self.window.refresh()


class SimulationWindow(Window):
    """docstring for SimulationWindow"""

    def __init__(self, stdscr, automata):
        self.stdscr = stdscr
        height, width = self.stdscr.getmaxyx()
        # los bordes no cuentan como espacio utilizable
        height -= 2
        width -= 2

        width_configuration_information_panel = 40
        height_simulation_information_panel = 15

        # ventanas de los paneles
        height_simulation_panel = height - height_simulation_information_panel
        width_simulation_panel = width - width_configuration_information_panel
        simulation_panel = c.newwin(
            height_simulation_panel, width_simulation_panel, 1, 1
        )
        configuration_information_panel = c.newwin(
            height, width_configuration_information_panel, 1, width_simulation_panel + 1
        )
        simulation_information_panel = c.newwin(
            height_simulation_information_panel,
            width_simulation_panel,
            height_simulation_panel + 1,
            1,
        )

        # paneles
        self.simulation_panel = SimulationPanel(simulation_panel, automata)
        self.configuration_information_panel = ConfigurationInformationPanel(
            configuration_information_panel
        )
        self.simulation_information_panel = SimulationInformationPanel(
            simulation_information_panel
        )

    def handle_input(self, char):
        if char == 27:  # ESC
            return PRESENTATION

    def write(self):
        self.simulation_panel.write()
        self.configuration_information_panel.write()
        self.simulation_information_panel.write()

        # se cargan los cambios
        self.stdscr.refresh()


class ConfigurationWindow(Window):
    """docstring for ConfigurationWindow"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.message = Writable(["Configuration"], (10, 10))

    def handle_input(self, char):
        if char == 27:  # ESC
            return PRESENTATION

    def write(self):
        self.message.write(self.stdscr)

        # se cargan los cambios
        self.stdscr.refresh()


class CreditWindow(Window):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.message = Writable(["Luis Papiernik es el mejor"], (10, 10))

    def handle_input(self, char):
        if char == 27:  # ESC
            return PRESENTATION

    def write(self):
        self.message.write(self.stdscr)

        # se cargan los cambios
        self.stdscr.refresh()


class PresentationWindow(Window):
    """docstring for PresentationWindow"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.buttons = [
            Writable(["Play"], (10, 10)),
            Writable(["Configuration"], (11, 10)),
            Writable(["Credit"], (12, 10)),
            Writable(["Quit"], (13, 10)),
        ]

        self.linter_index = 0

    def launch_event(self):
        if self.linter_index == 0:
            return SIMULATION
        if self.linter_index == 1:
            return CONFIGURATIONS
        if self.linter_index == 2:
            return CREDITS
        if self.linter_index == 3:
            return QUIT

    def handle_input(self, char):
        """ """
        if char == 10:  # ENTER
            return self.launch_event()
        if char == 259:  # UP
            self.linter_index -= 1
        if char == 258:  # DOWN
            self.linter_index += 1
        self.linter_index %= 4

    def write(self):
        """ """
        for i in range(4):
            if self.linter_index == i:
                self.stdscr.attron(c.color_pair(COLOR_SELECTED_ELEMENT))

            self.buttons[i].write(self.stdscr)

            if self.linter_index == i:
                self.stdscr.attroff(c.color_pair(COLOR_SELECTED_ELEMENT))

        # se cargan los cambios
        self.stdscr.refresh()


class CursesVisualizer:
    """
    Esta clase se encarga de coordinar todos los objetos necesarios para
    realizar la visualizacion de un automata en pantalla
    """

    def __init__(self, automata):
        self.stdscr = self.initialize()

        self.windows = [0] * 4
        self.windows[PRESENTATION] = PresentationWindow(self.stdscr)
        self.windows[SIMULATION] = SimulationWindow(self.stdscr, automata)
        self.windows[CONFIGURATIONS] = ConfigurationWindow(self.stdscr)
        self.windows[CREDITS] = CreditWindow(self.stdscr)
        self.current_window = PRESENTATION

        self.quit = False

        self.fps = 10
        self.time_per_frame = 1 / self.fps

    def initialize(self):
        """
        Este metodo realiza la inicializacion de recursos
        """
        # se inicializa curses y se obtiene una referencia a la ventana
        # principal
        stdscr = c.initscr()
        # se habilita que getch no bloquee el ciclo del programa
        stdscr.nodelay(True)
        # para hacer que el tiempo de espera de caracteres sea el mismo
        # para caractreres normales y secuencias especiales
        # stdscr.set_escdelay(0)  # solo funciona en python 3.9

        # para manejar colores
        c.start_color()

        # se delega el trabajo de codificar el codigo de teclas especiales
        # a curses
        stdscr.keypad(True)
        # se desabilita el mostrar en pantalla cada vez que se presione una
        # tecla (con esto se controlara que se muestra en pantalla)
        c.noecho()
        # se habilita la lectura de entrada del teclado sin tener que
        # presionar la tecla ENTER (se lee un caracter a la vez, no se espera
        # el caracter \n), esto desactiva el buffer en la lectura
        c.cbreak()

        # se oculta el cursor de la pantalla
        c.curs_set(0)

        # inicializacion de colores
        c.init_pair(COLOR_SELECTED_ELEMENT, c.COLOR_RED, c.COLOR_BLACK)
        # c.init_pair(COLOR_SELECTED_PANEL, c.COLOR_GREEN, c.COLOR_BLACK)

        # se limpia el texto antes de cambiar de ventana
        stdscr.erase()
        # se dibuja un borde para toda la ventana
        stdscr.box()

        return stdscr

    def limit_frame_rate(self, initialize=False):
        if initialize:
            self.last_time = time.time()
            return self.fps

        diff = time.time() - self.last_time
        if diff < self.time_per_frame:
            time.sleep(self.time_per_frame - diff)

        self.last_time = time.time()

        # se debe retornar la tasa real de fps actual
        return 0

    def loop(self):
        """
        Este metodo coordina el ciclo de vida del visualizador
        """
        self.limit_frame_rate(initialize=True)
        while not self.quit:
            # se obtiene entrada del usuario
            char = self.stdscr.getch()
            event = self.windows[self.current_window].handle_input(char)
            self.windows[self.current_window].write()

            # se presiono la letra q o el evento de la ventana es quit
            if char == 113 or event == QUIT:
                self.quit = True

            # se debe cambiar de ventana
            if event is not None:
                # se limpia el texto antes de cambiar de ventana
                self.stdscr.erase()
                # se dibuja un borde para toda la ventana
                self.stdscr.box()

                self.current_window = event

            self.limit_frame_rate(initialize=False)

    def end(self):
        """
        Este metodo libera recursos una vez se ha terminado la ejecucion
        """
        # se revierten las configuraciones establecidas
        c.echo()
        c.nocbreak()
        self.stdscr.keypad(False)
        c.curs_set(0)

        c.endwin()


if __name__ == "__main__":
    try:
        visualizer = CursesVisualizer(TestAutomata())

        visualizer.loop()
        visualizer.end()
    except Exception as e:
        c.echo()
        c.nocbreak()
        c.curs_set(0)

        c.endwin()
        print(e)
