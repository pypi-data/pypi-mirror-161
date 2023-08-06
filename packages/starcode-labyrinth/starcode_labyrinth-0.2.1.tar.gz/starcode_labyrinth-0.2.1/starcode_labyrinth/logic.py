"""
Provides the game logic functions for a labyrinth.

"""

# Copyright (C) 2022
# Benjamin Paaßen
# starcode

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2022, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '0.2.1'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'benjamin.paassen@dfki.de'

# a list of standard levels. Each entry of the list is a
# dictionary describing the level with the following keys:
#    'map': A two-dimensional integer array representing the map,
#        where X[i, j] = 0 if cell X[i, j] in the labyrinth is
#        blocked, X[i, j] = 1 if it is free, and 2 if it is the goal.
#    'start_x': The initial x position of the agent.
#    'start_y': The initial y position of the agent.
#    'start_theta': The initial orientation of the agent (in degrees).
#        0 degrees means pointing to the right,
#        90 degrees means pointing upwards, 180 degrees means pointing
#        to the left, and 270 degrees means pointing downwards.
#    'min_turns' : The minimum number of actions needed to complete
#        the level.
levels = [
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 2, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 0,
    'min_turns' : 2
  },
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 2, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 180,
    'min_turns' : 4
  },
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 2, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 1,
    'start_y' : 2,
    'start_theta' : 0,
    'min_turns' : 4
  },
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 1, 0, 1, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 2, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 1,
    'start_y' : 3,
    'start_theta' : 90,
    'min_turns' : 7
  },
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 1, 0, 1, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 2, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 2,
    'start_y' : 5,
    'start_theta' : 90,
    'min_turns' : 12
  },
  {
    'map' : np.array([
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 1, 0, 1, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 2, 0],
                    [0, 0, 0, 0, 0]
    ]),
    'start_x' : 2,
    'start_y' : 5,
    'start_theta' : 270,
    'min_turns' : 12
  }
]

LEFT  = 'left'
RIGHT = 'right'
GO    = 'go'

def execute_agent(agent, level, start_memory = None, max_turns = None):
    """ Executes the given agent with the given initial memory
    on the given level.

    Parameters
    ----------
    agent: fun
        A function taking two input arguments and returning two
        output arguments. The inputs are whether the field in front
        of the agent is free (True) or blocked (False) and the current
        memory. The outputs are expected to be the next action
        (either 'left', 'right', or 'go') and the next memory state.
    level: dict
        A dictionary describing the level with the following keys:
        'map': A two-dimensional integer array representing the map,
        where X[i, j] = 0 if cell X[i, j] in the labyrinth is
        blocked, X[i, j] = 1 if it is free, and 2 if it is the goal.
        'start_x': The initial x position of the agent.
        'start_y': The initial y position of the agent.
        'start_theta': The initial orientation of the agent (in degrees).
        0 degrees means pointing to the right,
        90 degrees means pointing upwards, 180 degrees means pointing
        to the left, and 270 degrees means pointing downwards.
        'min_turns': The minimum number of actions needed to complete
        the level.
    start_memory: object (default = None)
        The initial memory for the agent.
    max_turns: int (default = max(level['min_turns'] + 20, 4 * level['min_turns']))
        The number of turns after which the execution is stopped.
        This is to prevent endless loops.

    Returns
    -------
    trace: list
        A list of states of an agent's behavior on a level.
        Each state should be a tuple x[t], where x[t][0] is
        the agent's x position at time t, x[t][1] is the
        agent's y position at time t, x[t][2] is the agent's
        orientation (in degrees) at time t, and x[t][3] is the
        agent's memory at time t.

    """
    # extract the initial conditions
    X     = level['map']
    n, m  = X.shape
    x     = level['start_x']
    y     = level['start_y']
    theta = level['start_theta']
    mem   = start_memory

    if max_turns is None:
        max_turns = max(level['min_turns'] + 20, 4 * level['min_turns'])

    # execute the agent until goal is found or the maximum number of
    # turns is run. Store all states in a sequence
    states = []
    for t in range(max_turns+1):
        # record the current state
        states.append((x, y, theta, mem))
        # check if the current position in the map is the goal. If so: break
        if X[n-y-1, x] == 2:
            break
        # check if the space in front of the agent is free or not
        if theta == 0:
            free = x < m-1 and X[n-y-1, x+1] > 0.5
        elif theta == 180:
            free = x > 0 and X[n-y-1, x-1] > 0.5
        elif theta == 90:
            free = y < n-1 and X[n-y-2, x] > 0.5
        elif theta == 270:
            free = y > 0 and X[n-y, x] > 0.5
        else:
            raise ValueError('Unknown orientation: %s' % str(theta))
        # apply the agent function
        next_action, mem = agent(free, mem)
        # apply the action (if possible)
        if next_action == LEFT:
            theta += 90
            if theta >= 360:
                theta -= 360
        elif next_action == RIGHT:
            theta -= 90
            if theta < 0:
                theta += 360
        elif next_action == GO:
            # execute go action only if free
            if free:
                if theta == 0:
                    x += 1
                elif theta == 180:
                    x -= 1
                elif theta == 90:
                    y += 1
                elif theta == 270:
                    y -= 1
                else:
                    raise ValueError('Unknown orientation: %s' % str(theta))
        else:
            raise ValueError('Unknown action: %s' % str(next_action))
    return states
