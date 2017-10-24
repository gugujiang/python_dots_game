"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil
import threading
import tkinter
import tkinter as tk
from tkinter.messagebox import showinfo
import os
import random

import time
import pygame

try:
    from PIL import ImageTk, Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from view import GridView
from game import DotGame, ObjectiveManager, CompanionGame
from dot import BasicDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = "Zhengyan Wang (s4419759)"
__email__ = ""
__date__ = ""

__version__ = "1.1.1"


def load_image_pil(image_id, size, prefix, suffix='.png'):
    """Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
    width, height = size
    file_path = os.path.join(prefix, f"{width}x{height}", image_id + suffix)
    return ImageTk.PhotoImage(Image.open(file_path))


def load_image_tk(image_id, size, prefix, suffix='.gif'):
    """Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
    width, height = size
    file_path = os.path.join(prefix, f"{width}x{height}", image_id + suffix)
    return tk.PhotoImage(file=file_path)


# This allows you to simply load png images with PIL if you have it,
# otherwise will default to gifs through tkinter directly
load_image = load_image_pil if HAS_PIL else load_image_tk  # pylint: disable=invalid-name

DEFAULT_ANIMATION_DELAY = 0  # (ms)
ANIMATION_DELAYS = {
    # step_name => delay (ms)
    'ACTIVATE_ALL': 50,
    'ACTIVATE': 100,
    'ANIMATION_BEGIN': 300,
    'ANIMATION_DONE': 0,
    'ANIMATION_STEP': 200
}


# Define your classes here
class ButterflyDot(BasicDot):
    DOT_NAME = "butterfly"

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        if self.get_kind() == 1:
            return "{}/{}".format(self.get_name(), "butterfly-0")
        elif self.get_kind() == 2:
            return "{}/{}".format(self.get_name(), "butterfly-1")
        elif self.get_kind() == 3:
            return "{}/{}".format(self.get_name(), "butterfly-2")
        elif self.get_kind() == 4:
            return "{}/{}".format(self.get_name(), "coocoon-cracked")


class InfoPanel(tk.Frame):
    def __init__(self, root):
        """Constructor
        """
        tk.Frame.__init__(self)
        self.score_str = tkinter.StringVar()
        self.obj = []
        self.obj.append(tkinter.StringVar())
        self.obj.append(tkinter.StringVar())
        self.obj.append(tkinter.StringVar())
        self.obj.append(tkinter.StringVar())

        self.remaining_moves_str = tkinter.StringVar()
        self.score_str.set(0)
        self.remaining_moves_str.set(20)
        self.play_music()

    def play_music(self):
        file = 'music.mp3'
        pygame.mixer.init()
        track = pygame.mixer.music.load(file)
        pygame.mixer.music.play(loops=100)

    def pause_music(self):
        pygame.mixer.music.pause()

    def replay_music(self):
        pygame.mixer.music.unpause()

    # Exit hints
    def show(self):
        if (tkinter.messagebox.askokcancel('Exit hints', 'Are you sure you want to quit the game?')):
            self.client_exit()

    # Exit
    def client_exit(self):
        exit()

    def init_window(self, root, app):
        menubar = tk.Menu(root)
        # File Menu & Dialogs
        filemenu = tk.Menu(menubar, tearoff=0)
        new_game_menu = filemenu.add_command(label="New Game", command=app.reset)
        filemenu.add_command(label="Exit", command=self.show)
        menubar.add_cascade(label="File", menu=filemenu)
        # Task 3 – Advanced Features
        filemenu2 = tk.Menu(menubar, tearoff=0)
        filemenu2.add_command(label="Pause", command=self.pause_music)
        filemenu2.add_command(label="RePlay", command=self.replay_music)
        menubar.add_cascade(label="Music Control", menu=filemenu2)
        root.config(menu=menubar)

        tk.Label(self, textvariable=self.remaining_moves_str, font=("黑体", 30, "bold")).grid(row=0, column=0)
        tk.Label(self, textvariable=self.score_str, font=("黑体", 30, "bold")).grid(row=1, column=1)

        render0 = ImageTk.PhotoImage(Image.open("images\\dots\\20x20\\butterfly\\butterfly-0.gif"))
        img0 = tk.Label(self, image=render0)
        img0.image = render0
        img0.grid(row=1, column=6)
        tk.Label(self, textvariable=self.obj[0]).grid(row=2, column=6)

        render1 = ImageTk.PhotoImage(Image.open("images\\dots\\20x20\\butterfly\\butterfly-1.gif"))
        img1 = tk.Label(self, image=render1)
        img1.image = render1
        img1.grid(row=1, column=7)
        tk.Label(self, textvariable=self.obj[1]).grid(row=2, column=7)

        render2 = ImageTk.PhotoImage(Image.open("images\\dots\\20x20\\butterfly\\coocoon-cracked.gif"))
        img2 = tk.Label(self, image=render2)
        img2.image = render2
        img2.grid(row=1, column=8)
        tk.Label(self, textvariable=self.obj[2]).grid(row=2, column=8)

        render3 = ImageTk.PhotoImage(Image.open("images\\dots\\20x20\\butterfly\\butterfly-2.gif"))
        img3 = tk.Label(self, image=render3)
        img3.image = render3
        img3.grid(row=1, column=9)
        tk.Label(self, textvariable=self.obj[3]).grid(row=2, column=9)

        load = Image.open("images\\companions\\useless.gif")
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self, image=render)
        img.image = render
        img.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=tk.W + tk.E + tk.N + tk.S, padx=5, pady=5)

    def set_score(self, score):
        self.score_str.set(score)

    def set_objectives(self, list):
        for x in range(len(list)):
            self.obj[x].set(list[x])

    def set_remaining_moves(self, remaining_moves):
        self.remaining_moves_str.set(remaining_moves)


class IntervalBar(tk.Canvas):
    def __init__(self, root):
        tk.Canvas.__init__(self, root)
        self.now_step = 0
        self.step = []
        self.step.append(self.create_rectangle(10, 2, 60, 20, fill="white"))
        self.step.append(self.create_rectangle(60, 2, 110, 20, fill="white"))
        self.step.append(self.create_rectangle(110, 2, 160, 20, fill="white"))
        self.step.append(self.create_rectangle(160, 2, 210, 20, fill="white"))
        self.step.append(self.create_rectangle(210, 2, 260, 20, fill="white"))
        self.step.append(self.create_rectangle(260, 2, 310, 20, fill="white"))

    def next_step(self):
        for k in range(6):
            if k == self.now_step:
                self.itemconfig(self.step[k], fill="cornflowerblue")
            else:
                self.itemconfig(self.step[k], fill="white")
        self.now_step = (self.now_step + 1) % 6


# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master, infoPanel, intervalBar):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """
        self._master = master
        self._infoPanel = infoPanel
        self._infoPanel.init_window(master, self)
        self._intervalBar = intervalBar

        self._playing = True

        self._image_manager = ImageManager('images/dots/', loader=load_image)

        # Game
        counts = [10, 15, 25, 25]
        random.shuffle(counts)
        # randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], counts)

        self._objectives = ObjectiveManager(objectives)
        self._infoPanel.set_objectives([self._objectives.get_status()[i][1] for i in range(4)])

        # Game
        dead_cells = {(2, 2), (2, 3), (2, 4),
                      (3, 2), (3, 3), (3, 4),
                      (4, 2), (4, 3), (4, 4),
                      (0, 7), (1, 7), (6, 7), (7, 7)}
        self._game = DotGame({ButterflyDot: 1}, objectives=self._objectives, kinds=(1, 2, 3, 4), size=(8, 8),
                             dead_cells=dead_cells)

        # The following code may be useful when you are implementing task 2:
        for i in range(0, 4):
            for j in range(0, 2):
                position = i, j
                self._game.grid[position].set_dot(ButterflyDot(3))
        self._game.grid[(7, 3)].set_dot(ButterflyDot(1))

        # Grid View
        self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
        self._grid_view.pack()
        self._grid_view.draw(self._game.grid)
        self.draw_grid_borders()

        # Events
        self.bind_events()

        # Set initial score again to trigger view update automatically
        self._refresh_status()

    def draw_grid_borders(self):
        """Draws borders around the game grid"""

        borders = list(self._game.grid.get_borders())

        # this is a hack that won't work well for multiple separate clusters
        outside = max(borders, key=lambda border: len(set(border)))

        for border in borders:
            self._grid_view.draw_border(border, fill=border != outside)

    def bind_events(self):
        """Binds relevant events"""
        self._grid_view.on('start_connection', self._drag)
        self._grid_view.on('move_connection', self._drag)
        self._grid_view.on('end_connection', self._drop)

        self._game.on('reset', self._refresh_status)
        self._game.on('complete', self._drop_complete)

        self._game.on('connect', self._connect)
        self._game.on('undo', self._undo)

    def _animation_step(self, step_name):
        """Runs for each step of an animation
        
        Parameters:
            step_name (str): The name (type) of the step    
        """
        # print(step_name)
        self._refresh_status()
        self.draw_grid()

    def animate(self, steps, callback=lambda: None):
        """Animates some steps (i.e. from selecting some dots, activating companion, etc.
        
        Parameters:
            steps (generator): Generator which yields step_name (str) for each step in the animation
        """

        if steps is None:
            steps = (None for _ in range(1))

        animation = create_animation(self._master, steps,
                                     delays=ANIMATION_DELAYS, delay=DEFAULT_ANIMATION_DELAY,
                                     step=self._animation_step, callback=callback)
        animation()

    def _drop(self, position):  # pylint: disable=unused-argument
        """Handles the dropping of the dragged connection

        Parameters:
            position (tuple<int, int>): The position where the connection was
                                        dropped
        """
        if not self._playing:
            return

        if self._game.is_resolving():
            return

        self._grid_view.clear_dragged_connections()
        self._grid_view.clear_connections()

        self.animate(self._game.drop())

    def _connect(self, start, end):
        """Draws a connection from the start point to the end point

        Parameters:
            start (tuple<int, int>): The position of the starting dot
            end (tuple<int, int>): The position of the ending dot
        """

        if self._game.is_resolving():
            return
        if not self._playing:
            return
        self._grid_view.draw_connection(start, end,
                                        self._game.grid[start].get_dot().get_kind())

    def _undo(self, positions):
        """Removes all the given dot connections from the grid view

        Parameters:
            positions (list<tuple<int, int>>): The dot connects to remove
        """
        for _ in positions:
            self._grid_view.undo_connection()

    def _drag(self, position):
        """Attempts to connect to the given position, otherwise draws a dragged
        line from the start

        Parameters:
            position (tuple<int, int>): The position to drag to
        """

        if self._game.is_resolving():
            return
        if not self._playing:
            return

        tile_position = self._grid_view.xy_to_rc(position)

        if tile_position is not None:
            cell = self._game.grid[tile_position]
            dot = cell.get_dot()

            if dot and self._game.connect(tile_position):
                self._grid_view.clear_dragged_connections()
                return

        kind = self._game.get_connection_kind()

        if not len(self._game.get_connection_path()):
            return

        start = self._game.get_connection_path()[-1]

        if start:
            self._grid_view.draw_dragged_connection(start, position, kind)

    @staticmethod
    def remove(*_):
        """Deprecated in 1.1.0"""
        raise DeprecationWarning("Deprecated in 1.1.0")

    def draw_grid(self):
        """Draws the grid"""
        self._grid_view.draw(self._game.grid)

    def reset(self):
        """Resets the game"""
        print("hello,start reset ")
        self._game.reset()
        self._infoPanel.set_score(0)
        self._infoPanel.set_remaining_moves(20)
        self._infoPanel.set_objectives([self._objectives.get_status()[i][1] for i in range(4)])
        self._playing = True

    def check_game_over(self):
        """Checks whether the game is over and shows an appropriate message box if so"""
        state = self._game.get_game_state()

        if state == self._game.GameState.WON:
            showinfo("Game Over!", "You won!!!")
            self._playing = False
        elif state == self._game.GameState.LOST:
            showinfo("Game Over!",
                     f"You didn't reach the objective(s) in time. You connected {self._game.get_score()} points")
            self._playing = False

    def _drop_complete(self):
        """Handles the end of a drop animation"""
        self.check_game_over()
        self._infoPanel.set_objectives(([self._objectives.get_status()[i][1] for i in range(4)]))
        remaining_steps = self._game.get_moves()
        if remaining_steps > 0:
            self._intervalBar.next_step()
            self._infoPanel.set_remaining_moves(remaining_steps)
            # Useful for when implementing a companion
            # if self._game.companion.is_fully_charged():
            #     self._game.companion.reset()
            #
            #     self._intervalBar.next_step()
            #     self._refresh_status()
            #
            #     return self.animate(steps)
            # Need to check whether the game is over
            # raise NotImplementedError()  # no mercy for stooges

    def _refresh_status(self):
        """Handles change in score"""

        # Normally, this should raise the following error:
        # raise NotImplementedError()
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information
        # Sometimes I believe Python ignores all my comments :(
        score = self._game.get_score()
        self._infoPanel.set_score(score)
        # print("Score is now {}.".format(score))


def main():
    """Sets-up the GUI for Dots & Co"""
    # Write your GUI instantiation code here
    root = tk.Tk()
    root.title("My Dots Game")
    w, h = root.maxsize()
    root.geometry("{}x{}".format(w, h))
    # root.geometry("900x900+600+400")
    info = InfoPanel(root)
    info.pack()
    bar = IntervalBar(root)
    bar.pack()
    DotsApp(root, infoPanel=info, intervalBar=bar)
    root.mainloop()


if __name__ == "__main__":
    main()
