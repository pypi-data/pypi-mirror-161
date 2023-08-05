# Game Of Life

Simple way to play Conway's game of life in python.<br>
You can import your own map as json file name "save.json", using `get_MAP` methode.<br>
All you custom maps (in the save.json file) are available in the list `custom_maps`.<br>
Other custom maps are available such as: `my_map_1` and `my_map_2`, created using `Map` class : <br>
```python
from simple_game_of_life import Map
m = Map(100)
my_map_1 = m.mini_random_MAP((25, 20))
my_map_2 = m.kind(kind="line 10")
```

<br>
<br>
NOTE : Two artificials borders are created for each map, <br>
The first one is visible while playing, it's in black.<br>
The second one is white (invisible) just after the black border, no cell can born here


## Installation

Run the following command to install:
```$ pip install simple-game-of-life ```

## Usage

for a random map
```python
from simple_game_of_life import GameOfLife
game = GameOfLife(50) 
game.start_animation()
```

for a custom map
```python
from simple_game_of_life import GameOfLife
from random import choice
custom_map = GameOfLife.get_MAP() # custom_map already saved in the json file
game = GameOfLife(custom_map=choice(my_custom_map))
game.start_animation()
# Note you can also import custom_map like that :
# from simple_game_of_life import custom_map 
```

to implement a pattern :
```python
from simple_game_of_life import GameOfLife, Map
glider = [[0,1,0],
          [0,0,1],
          [1,1,1]]
m = Map(100)
my_map = m.my_pattern(glider)
game = GameOfLife(custom_map=my_map)
game.start_animation()
```