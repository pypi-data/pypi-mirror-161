"""
# Game Of Life

Simple way to play Conway's game of life in python.
You can import your own map as json file name "save.json", using `get_MAP` methode.
All you custom maps (in the save.json file) are available in the list `custom_maps`.
Other custom maps are available such as: `my_map_1` and `my_map_2`, created using `Map` class : 

>>> from simple_game_of_life import Map
>>> m = Map(100)
>>> my_map_1 = m.mini_random_MAP((25, 20))
>>> my_map_2 = m.kind(kind="line 10")


NOTE : Two artificials borders are created for each map, 
The first one is visible while playing, it's in black.
The second one is white (invisible) just after the black border, no cell can born here


## Installation

Run the following command to install:
```$ pip install simple-game-of-life ```


## Usage

for a random map :
>>> from simple_game_of_life import GameOfLife
>>> game = GameOfLife(50) 
>>> game.start_animation()


for a custom map : 
>>> from simple_game_of_life import GameOfLife
>>> from random import choice
>>> custom_map = GameOfLife.get_MAP() # custom_map already saved in the json file
>>> game = GameOfLife(custom_map=choice(my_custom_map))
>>> game.start_animation()
>>> # Note you can also import custom_map like that :
>>> # from simple_game_of_life import custom_map 

to implement a pattern :
>>> from simple_game_of_life import GameOfLife, Map
>>> glider = [[0,1,0],
              [0,0,1],
              [1,1,1]]
>>> m = Map(100)
>>> my_map = m.my_pattern(glider)
>>> game = GameOfLife(custom_map=my_map)
>>> game.start_animation()


## Other usage

`GameOfLife` classe :
    - You can save a map by using `saved_MAP` methode.
    - You can get a map by using `get_MAP` methode.
    - You can reset all saved map by using `reset_MAP` methode.
    - You can get all frames by using `get_history` methode.
    - You can set a new animation with the same instance using `new_animation` methode.


`Map` classe :
    - `full_random_MAP` : all the map gonna be random.
    - `mini_random_MAP` : a portion of the map gonna be random.
    - `my_pattern` : insert your pattern into an empty map.
    - `kind` : insert well know pattern into an empty map, (currenly 5 patterns are available).


You can also calculate the average time of instancing, using `timeit` function:

>>> game = timeit(GameOfLife, loop=100, size_or_side=50, frames=200) # loop : number of loop
>>> game.start_animation()

"""

###################################################################################################

# ! REGLE (fr)

# En vertu des règles du jeu de la vie de Conway, une cellule « naît »
# lorsque trois de ses huit voisines sont vivantes,
# et reste en vie aussi longtemps qu'elle possède deux ou trois voisines vivantes
# dans le cas contraire elle meurt (par isolement ou surpopulation)


#! RULE (en)

# By me :)
# According to rules of Conway's  game of life, a cell "born"
# when three of its eight neighbors are alives,
# and stay alive as long as it has two or three neighbors alives
# otherwise it die (by isolation or overpopulation)

# By google translate (deepl actualy)
# According to Conway's rules of life,
# a cell is "born" when three of its eight neighbors are alive,
# and remains alive as long as it has two or three living neighbors
# otherwise it dies (by isolation or overpopulation)

##################################################################################################

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import json

from lexicon import *


class Map:
    def __init__(self, size_or_side):
        """simple way to create a map :
                - `full_random_MAP` : all the map gonna be random.
                - `mini_random_MAP` : a portion of the map gonna be random.
                - `my_pattern` : insert your pattern into an empty map
                - `kind` : insert well know pattern into an empty map, (currenly 5 patterns are available)

        Args:
            size_or_side ((iterable, lenght = 2) or int):
            either size of a matrix 
            or side of a square matrix. 

            kind (str, optional): 
            Lexicon of well know pattern, ex 'line 10' is a line of 10 living cell. 
            Defaults to None.
        """
        self.x, self.y = _size_or_side(size_or_side)
        self._init_map()

    def _init_map(self):
        self.map = np.zeros((self.x, self.y))

    def _insert(self, pattern):
        assert _is_iterable(pattern)
        self._init_map()
        pattern = np.array(pattern)
        x = len(pattern)
        y = len(pattern[0])
        x_rest = self.x % 2 - x % 2
        y_rest = self.y % 2 - y % 2
        x_map = self.x // 2 - x // 2
        y_map = self.y // 2 - y // 2
        self.map[x_map+x_rest: -x_map, y_map + y_rest:-y_map] = pattern

    def full_random_MAP(self, seed=None):
        """all the map gonna be random.

        Args:
            size_or_side ((iterable, lenght = 2) or int): 
            either size of a matrix 
            or side of a square matrix.
            
            seed (_type_, optional): set the seed, by using `np.random.seed`. Defaults to None.

        Returns:
            map : all the map gonna be random.
        """

        if seed != None:
            np.random.seed(seed)

        map_ = np.random.randint(0, 2, (self.x, self.y))
        return map_

    def mini_random_MAP(self, size_or_side, seed=None):
        """a portion of the map gonna be random.

        Args:
            size_or_side ((iterable, lenght = 2) or int): 
            either size of a matrix 
            or side of a square matrix.
            
            seed (_type_, optional): set the seed, by using `np.random.seed`. Defaults to None.

        Returns:
            map : a portion of the map gonna be random.
        """

        if seed is not None:
            np.random.seed(seed)

        x, y = _size_or_side(size_or_side)
        pattern = np.random.randint(0, 2, (x, y))
        self._insert(pattern)

        return self.map

    def my_pattern(self, pattern):
        """insert your pattern into an empty map

        Args:
            pattern (matrix): the pattern you whant to insert into a empty map

        Returns:
            map: the map with you pattern in the middle, without border
        """
        self._insert(pattern)
        return self.map

    def kind(self, kind: str = None):
        """insert well know pattern

        Args:
            kind (str, optional): 
            Lexicon of well know pattern, ex 'line 10' is a line of 10 living cell. 
            Defaults to None.

        Returns:
            map: matrix representing the map
        """
        kind = kind.lower()

        if "line" in kind:
            try:
                n = int(kind.split()[1])
            except:
                n = 10
            pattern = np.array([1]*n).reshape((n, 1))

        elif "glider" == kind:
            pattern = glider

        elif "lwss" == kind:
            pattern = lwss
        elif "mwss" == kind:
            pattern = mwss
        elif "hwss" == kind:
            pattern = hwss

        self._insert(pattern)
        return self.map


##################################################################################################

class GameOfLife:
    """
    Simple way to play Conway's game of life in python.
    You can import your own map as json file name "save.json", using `get_MAP` methode.
    All you custom maps (in the save.json file) are available in the list `custom_maps`.
    Other custom maps are available such as: `my_map_1` and `my_map_2`, created using `Map` class : 

    >>> m = Map(100)
    >>> my_map_1 = m.mini_random_MAP((25, 20))
    >>> my_map_2 = m.kind(kind="line 10")

    Exemple of a game ::

        >>> from simple_game_of_life import GameOfLife
        >>> game = GameOfLife(50) 
        >>> game.start_animation()

        >>> from simple_game_of_life import GameOfLife
        >>> from random import choice
        >>> custom_map = GameOfLife.get_MAP() # custom_map already saved in the json file
        >>> game = GameOfLife(custom_map=choice(my_custom_map))
        >>> game.start_animation()

        >>> from simple_game_of_life import GameOfLife, Map
        >>> glider = [[0,1,0],
                [0,0,1],
                [1,1,1]]
        >>> m = Map(100)
        >>> my_map = m.my_pattern(glider)
        >>> game = GameOfLife(custom_map=my_map)
        >>> game.start_animation()


    """

    def __init__(self, size_or_side=None, custom_map=None, seed: int = None, frames: int = 500, zoom: float = 10):
        """initialise the game, by calculating all the frames.


        NOTE : Two artificials borders are created for each map, 
        The first one is visible while playing, it's in black
        The second one is white (invisible) just after the black border, no cell can born here

        Args:
            size_or_side ((iterable, lenght = 2) or int):
            either size of a matrix 
            or side of a square matrix. 
            Defaults to None.

            custom_map (iterable, matrix): 
            a custom map that you created using an iterable (dim=2, matrix), or by using `Board` classe . 
            Defaults to None.

            seed (int, optional): 
            set the seed, by using `np.random.seed`. 
            Defaults to None.

            frames (int, optional):
            number of frames calculated. 
            Defaults to 500.

            zoom (float, optional): 
            allow to create larger plot, if zoom=10 (square matrix) then the figure size will be (5, 5) inch. 
            Defaults to 10.
        """

        _assert_test(size_or_side, custom_map)

        if size_or_side is not None:
            self.x, self.y = _size_or_side(size_or_side)

        if _is_iterable(custom_map):
            if type(custom_map) != np.ndarray:
                custom_map = np.array(custom_map)
            self.x, self.y = len(custom_map), len(custom_map[0])
        self.custom_map = custom_map

        self.seed = seed
        self.frames = frames
        self.zoom = zoom
        self.is_history_avalide = False

        board = np.zeros((self.x+2, self.y+2))
        self.map = np.full((self.x+4, self.y+4), 1)
        self.map[1:-1, 1:-1] = board

        self._init_plot()
        self._init_saved_MAP()
        self._set_MAP_and_history()

    def _init_plot(self):

        x_persent = round(self.x/(self.x + self.y) * self.zoom)
        y_persent = round(self.y/(self.x + self.y) * self.zoom)

        plt.close()
        fig, ax = plt.subplots(
            figsize=(x_persent, y_persent))
        im = ax.imshow(self.random_MAP(), cmap="Greys")
        ax.set(title="Jeu De La Vie")
        ax.axis(False)

        self.fig = fig
        self.ax = ax
        self.im = im

    def random_MAP(self):

        if self.seed != None:
            np.random.seed(self.seed)

        inner_map = np.random.randint(0, 2, (self.x, self.y))
        self.map[2:-2, 2:-2] = inner_map

        return self.map

    def _create_border(self, inner_map):
        self.map[2:-2, 2:-2] = inner_map
        return self.map

    @staticmethod
    def _inner_MAP(full_map):
        return full_map[2:-2, 2:-2]

    @staticmethod
    def _board_MAP(full_map):
        return full_map[1:-1, 1:-1]

    @staticmethod
    def _transition_MAT(map):
        return (map[:-2, :-2] + map[:-2, 1:-1] + map[:-2, 2:] +
                map[1:-1, :-2] + map[1:-1, 2:] +
                map[2:, :-2] + map[2:, 1:-1] + map[2:, 2:]
                )

    def next_MAP(self, full_map):
        inner_map = self._inner_MAP(full_map)
        next_inner_map = self._transition_MAT(self._board_MAP(full_map))
        next_inner_map[(next_inner_map < 2) |
                       (next_inner_map > 3)] = 0
        next_inner_map[next_inner_map == 3] = 1

        # todo next_inner_map == 2 with out while loop
        filtre = inner_map == 1

        for i in range(self.x):
            for j in range(self.y):
                bool_ = filtre[i, j]
                if bool_ and next_inner_map[i, j] == 2:
                    next_inner_map[i, j] = 1

        next_inner_map[next_inner_map == 2] = 0
        self.map[2:-2, 2:-2] = next_inner_map

        return self.map

    def set_history(self, full_map):
        self.is_history_avalide = True
        x, y = len(full_map), len(full_map[0])
        history = np.zeros((self.frames, x, y))
        map_precedente = full_map
        history[0, :, :] = full_map
        for i in range(1, self.frames):
            map_precedente = history[i-1, :, :]
            history[i, :, :] = self.next_MAP(map_precedente)

        self.history = history
        return history

    def _set_MAP_and_history(self):

        if self.custom_map is None:
            self.set_history(self.random_MAP())
        else:
            self.custom_map = self._create_border(self.custom_map)
            self.set_history(self.custom_map)

    def get_history(self):
        assert self.is_history_avalide, "the history must be set, please use `set_history` methode"
        return self.history

    def new_animation(self, new_size_or_side=None, new_custom_map=None, frames: int = 100):
        """allow new animation with the same instance 

        Args:
            size_or_side ((iterable, lenght = 2) or int):
            size or side of the new map, for random map. Defaults to None.

            new_custom_map (iterable, matrix):
            new custom map. Defaults to None.

            frames (int, optional):
            number of frames calculated. Defaults to 100.

        """
        _assert_test(new_size_or_side, new_custom_map)
        self._init_plot()
        self.frames = frames

        if new_custom_map is not None:
            assert _is_iterable(new_custom_map)
            self.custom_map = new_custom_map
            self.x, self.y = len(new_custom_map), len(new_custom_map[0])
        if new_size_or_side is not None:
            self.x, self.y = _size_or_side(new_size_or_side)
            self.custom_map = None

        board = np.zeros((self.x+2, self.y+2))
        self.map = np.full((self.x+4, self.y+4), 1)
        self.map[1:-1, 1:-1] = board
        self._set_MAP_and_history()

    def _animation(self, i):
        self.ax.set_title(f"frames n°:{i+1}")
        cur_map = self.history[i]
        self.im.set_data(cur_map)
        return self.im,

    def start_animation(self, interval_between_two_frames: int = 100, plot: bool = True, save: bool = False, fps: int = 30, file_name: str = None):
        """ Start the animation, by default by plotting, and no video is saved

        NOTE :         
            For saving : 
            You need first to install ffmpeg :
            First search : Homebrew website (https://brew.sh/)
            Copy past the command in a Terminal
            Then in a Terminal : brew install ffmpeg

        Args:
            interval_between_two_frames (int, optional):
            Interval_between_two_frames in milisecond. Defaults to 100.

            plot (bool, optional): 
            Allow plotting. Defaults to True.

            save (bool, optional):
            Allow save .Defaults to False.

            fps (int, optional):  
            Frames per second if saved.Defaults to 30.

            file_name (str, optional): 
            file name for saved, must end by ".mp4", ".mov", ".avi", ".flv" or ".wmv", otherwise it's save with ".mp4".
            Defaults to None.
        """

        anim = FuncAnimation(self.fig,
                             self._animation,
                             frames=self.frames,
                             interval=interval_between_two_frames,
                             repeat=False)

        if plot:
            plt.show()

        # Save :
        # You need first to install ffmpeg :
        # First search : Homebrew website (https://brew.sh/)
        # Copy past the command in a Terminal
        # Then in a Terminal : brew install ffmpeg
        if save:
            from matplotlib.animation import FFMpegWriter

            if file_name is None:
                from pathlib import Path
                path = Path(__file__).parent
                path /= f"Game-of-life_{self.x}x{self.y}_{self.frames}frames.mp4"
            else:
                path = file_name
                if not path.endswith((".mp4", ".mov", ".avi", ".flv", ".wmv")):
                    path += ".mp4"
            writervideo = FFMpegWriter(fps=fps)
            anim.save(path, writer=writervideo)

    @staticmethod
    def _init_saved_MAP():
        try:
            with open("save.json", "r") as f:
                maps = json.load(f)
            return maps
        except:
            return []

    @staticmethod
    def get_MAP():
        return GameOfLife._init_saved_MAP()

    def save_MAP(self):
        if self.is_history_avalide:
            maps = self.get_MAP()
            with open("save.json", "w") as f:
                map_ = self._inner_MAP(self.history[0]).tolist()
                if map_ not in maps:
                    maps.append(map_)
                json.dump(maps, f, indent=1)

    @staticmethod
    def reset_MAP():
        with open("save.json", "w") as _:
            pass
            # dont need to do anything, save.json will be reset

###################################################################################################


def _size_or_side(size_or_side):

    assert (_is_iterable(size_or_side) and len(size_or_side) == 2) or (
        type(size_or_side) == int and size_or_side > 0), """
        size_or_side must be the size or side of a matrix. Ex : (30,15) or 15 or (15,15) 
        """

    if type(size_or_side) == int:
        x = y = size_or_side
    else:
        x, y = size_or_side

    return x, y


def timeit(cls, loop: int = 10, **kw):
    """Ex :
            >>> game = timeit(GameOfLife, loop=100, size_or_side=50, frames=200)
            >>> game.start_animation()

    Args:
        loop (int, optional): number of loop. Defaults to 10.

    Returns:
        GameOfLife: instance of GameOfLife classe
    """

    from time import time
    from statistics import mean
    n = 1
    # `n` from :
    # let n and i be a natural number != 0
    # if i is n*10% of loop => i/loop = n*0.1 => i/loop/0.1 = n ∈ N*

    T_tot = time()
    L = []
    print(f"calculating the average time of instancing over {loop} loop")
    for i in range(1, loop + 1):
        T = time()
        game = cls(**kw)
        L.append(time()-T)
        if i / loop / 0.1 >= n:  # take the first iteration greater than n*10%
            n += 1
            print(f"processing {i / loop * 100:.2f}%")
    print(f"average of {mean(L):.2f}s per loop",
          "\n", f"Total time : {time()-T_tot:.2f}")
    return game


def _is_iterable(iter_):
    try:
        len(iter_)
        return True
    except:
        return False


def _assert_test(size_or_side, custom_map):
    assert (size_or_side is not None) or (
        custom_map is not None), "you must give a `size_or_side` (random_map), or a `custom_map`"
    assert (size_or_side is None) or (
        custom_map is None), "you must choose between `size_or_side` (random_map) and a `custom_map`"


###################################################################################################

custom_maps = GameOfLife.get_MAP()


m = Map(100)
my_map_1 = m.mini_random_MAP((25, 20))
my_map_2 = m.kind(kind="line 10")

maps = [my_map_1, my_map_2]

if __name__ == "__main__":
    from random import choice

    MAP = choice(maps)

    game = GameOfLife(custom_map=MAP, frames=500)
    game.start_animation(interval_between_two_frames=25)
