# Starcode Labyrinth

Copyright (C) 2022 - Benjamin Paassen  
starcode  

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses/.

## Introduction

This module provides functions to draw labyrinth maps and execute
agents in form of finite state machines on them. This module is
intended for teaching, in particular during the courses of
[starcode](https://www.starcode.info/).

## Overview

The key concept for this module is that of an agent which navigates
a labyrinth. To initialize a new agent, you need to initialize
a new game state as follows:

```python
from starcode_labyrinth import state

my_state = state.State(level = 0)
```

The state object receives a level as input. Our package offers
several standard levels which are part of the didactic concept of
starcode. You can also provide your own levels, if you wish. Please
refer to the source code documentation for more details.

Once you have initialized your game state, you can tell the agent
to `move()`, `turn_left()`, or `turn_right()`.

```python
my_state.move()
my_state.turn_left()
my_state.turn_right()
```

To display the agent's current state, use the `draw_state()` function.

```python
my_state.draw_state()
```

![An example state where the agent looks right along a corridor towards the goal.](example_state.png)

To display the entire motion up to this point, use the `draw_trace()` function.

```python
my_state.draw_trace()
```

![An example trace where the agent took a step to the right, then turned left, and then turned right again, such that the agent ended up in the state displayed above.](example_trace.png)

As additional functions, we provide `is_free()` which returns `True`
if and only if the agent could move ahead, and `is_goal()` if and only if the agent is currently located at a goal position (the orange star in the pictures).
