"""
Provides an object-oriented interface for the logic.
This architecture is due to Emilio Rolandi.

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
from starcode_labyrinth import drawing

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2022, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '0.2.1'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'benjamin.paassen@dfki.de'


levels = [{
    'map' : np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,2,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 6,
    'start_theta' : 0,
    'min_turns' : 6
  },
  {
    'map' : np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,2,1,1,1,1,1,1,0,0],
            [0,0,0,0,0,0,0,0,0,0,1,0,0],
            [0,0,0,0,0,0,0,0,0,0,1,0,0],
            [0,1,1,1,1,1,1,1,0,0,1,0,0],
            [0,0,0,0,0,0,0,1,0,0,1,0,0],
            [0,0,0,0,0,0,0,1,0,0,1,0,0],
            [0,0,0,0,0,0,0,1,0,0,1,0,0],
            [0,0,0,0,0,0,0,1,0,0,1,0,0],
            [0,0,0,0,0,0,0,1,1,1,1,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 6,
    'start_theta' : 0,
    'min_turns' : 32
  },
  {
    'map' : np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,0,0,0,0,0],
            [0,1,0,0,0,0,0,1,0,0,0,0,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0],
            [0,1,1,1,1,1,0,2,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 6,
    'start_theta' : 0,
    'min_turns' : 18
  },
  {
    'map' : np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,1,0,0,0,0,0,0,0,0,0,0,1],
            [0,1,0,1,1,1,1,1,1,1,1,0,1],
            [0,1,0,1,0,0,0,0,0,0,1,0,1],
            [0,1,0,1,0,1,1,1,1,0,1,0,1],
            [0,1,0,1,0,1,0,0,2,0,1,0,1],
            [0,1,0,1,0,1,0,0,0,0,1,0,1],
            [0,1,0,1,0,1,1,1,1,1,1,0,1],
            [0,1,0,1,0,0,0,0,0,0,0,0,1],
            [0,1,0,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 90,
    'min_turns' : 78
  },
  {
    'map' : np.array([
            [0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,1,0,0,0,0,0,0,0,0,0,0,1],
            [0,1,0,1,1,1,1,1,1,1,1,0,1],
            [0,1,0,1,0,0,0,0,0,0,1,0,1],
            [0,1,0,1,0,0,0,0,0,0,1,0,1],
            [0,1,0,1,0,0,0,0,0,0,1,0,1],
            [0,1,0,1,1,1,1,1,2,0,1,0,1],
            [0,1,0,0,0,0,0,0,0,0,1,0,1],
            [0,1,1,1,1,1,1,1,1,1,1,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 0,
    'min_turns' : 79
  },
  {
    'map' : np.array([
            [0,0,0,0,0,1,1,1,1,0,0,0,0],
            [0,1,1,1,0,1,0,0,1,0,0,1,2],
            [0,1,0,1,0,1,1,0,1,0,0,1,0],
            [0,1,0,1,0,0,1,0,1,0,0,1,0],
            [0,1,0,1,1,0,1,0,1,0,0,1,0],
            [0,1,0,0,1,0,1,0,1,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,0],
            [0,1,0,0,1,1,1,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 90,
    'min_turns' : 71
  },
  {
    'map' : np.array([
            [0,0,0,1,0,1,1,1,1,0,0,0,0],
            [1,1,1,1,0,1,0,0,1,0,1,1,2],
            [0,1,0,1,0,1,1,0,1,0,0,1,0],
            [0,1,0,1,0,0,1,0,1,0,0,1,0],
            [0,1,0,1,1,0,1,0,1,0,0,1,0],
            [0,1,0,0,1,0,1,0,1,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,0,1,0],
            [0,1,0,0,1,0,1,0,0,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,0],
            [0,1,0,0,1,1,1,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 1,
    'start_theta' : 90,
    'min_turns' : 71
  },
  {
    'map' : np.array([
             [0,0,0,0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,1,0,0,0,0,0],
             [0,0,0,0,0,1,0,1,0,0,0,0,0],
             [0,0,0,0,0,1,1,1,1,1,1,1,0],
             [0,0,0,0,1,1,0,0,1,0,1,0,0],
             [0,1,1,0,0,1,0,0,0,0,1,0,0],
             [0,0,1,0,0,1,0,0,0,0,1,1,0],
             [0,0,1,1,1,1,1,1,0,0,1,0,0],
             [0,0,0,1,0,0,0,0,0,0,1,0,0],
             [0,0,0,0,0,0,0,0,0,0,2,0,0],
             [0,0,0,0,0,0,0,0,0,0,0,0,0]]),
    'start_x' : 1,
    'start_y' : 5,
    'start_theta' : 0,
    'min_turns' : 26
  },
  {
    'map' : np.array([
             [0,0,0,0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,1,0,1,0,0,0,0,0,0],
             [0,0,0,0,1,0,1,0,0,0,0,0,0],
             [0,0,0,0,1,1,1,1,1,1,1,0,0],
             [0,0,0,1,1,0,0,0,0,1,1,1,0],
             [1,1,1,0,1,1,0,0,0,1,0,0,0],
             [0,1,0,0,1,0,0,0,0,1,0,0,0],
             [0,1,1,1,1,0,0,1,1,1,0,0,0],
             [0,0,0,0,0,0,0,0,0,1,1,1,0],
             [0,0,2,1,1,1,1,1,1,1,0,0,0],
             [0,0,0,0,0,1,0,1,0,1,0,0,0],
             [0,0,0,0,0,0,0,1,0,0,0,0,0]]),
    'start_x' : 0,
    'start_y' : 6,
    'start_theta' : 0,
    'min_turns' : 34
  }
]



class State:
    """ Represents the state of an agent navigating a 2D labyrinth.

    Attributes
    ----------
    map: ndarray
        A 2D array representing the map, where 0 represents blockade,
        1 represents a free field, and 2 represents a goal field.
    x: int
        The current x position of the agent on the map. We count
        x from left to right.
    y: int
        The current y position of the agent on the map. We count
        y from bottom to top.
    theta: int
        The current orientation of the agent in degrees, either
        0, 90, 180, or 270.
    trace: list
        A list of past positions and orientations of the agent.

    """
    def __init__(self, level):
        """ Initializes a new state from a level.

        Parameters
        ----------
        level: dict
            A dictionary with the keys 'map', 'start_x',
            'start_y', 'start_theta', and (optionally) 'min_turns'.
            Alternatively, this can be a single integer in the range
            0-6, in which case a level from the state.levels array
            is used.

        """
        if isinstance(level, int):
            level = levels[level]

        self.map   = level['map']
        self.x     = level['start_x']
        self.y     = level['start_y']
        self.theta = level['start_theta']
        if 'min_turns' in level:
            self.min_turns = level['min_turns']
        else:
            self.min_turns = None
        self.trace = [(self.x, self.y, self.theta)]

    def is_goal(self):
        """ Returns True if the agent is currently located on a goal
        position and False if it is not.

        Returns
        -------
        goal: bool
            True if the agent is currently located on a goal
            position and False if it is not.

        """
        return self.map[self.map.shape[0]-self.y-1, self.x] == 2


    def is_free(self):
        """ Returns True if the field in front of the agent is
        free and False if the field is blocked.

        Returns
        -------
        free: bool
            True if the field in front of the agent is
            free and False if the field is blocked.

        """
        m, n = self.map.shape
        # translate x and y coordinates into row and column indices
        i = m-self.y-1
        j = self.x
        # check whether the field is free, depending on the
        # orientation
        if self.theta == 0:
            return j < n-1 and self.map[i, j+1] > 0.5
        elif self.theta == 180:
            return j > 0 and self.map[i, j-1] > 0.5
        elif self.theta == 90:
            return i > 0 and self.map[i-1, j] > 0.5
        elif self.theta == 270:
            return i < m-1 and self.map[i+1, j] > 0.5
        else:
            raise ValueError('Unknown orientation: %s' % str(self.theta))


    def move(self):
        """ Moves the agent towards its current orientation,
        if that is possible.

        Returns
        -------
        executed: bool
            True if the move was executed and False if it
            was not.

        """
        if self.is_free():
            if self.theta == 0:
                self.x += 1
            elif self.theta == 180:
                self.x -= 1
            elif self.theta == 90:
                self.y += 1
            elif self.theta == 270:
                self.y -= 1
            else:
                raise ValueError('Unknown orientation: %s' % str(theta))
            self.trace.append((self.x, self.y, self.theta))
            return True
        else:
            return False


    def turn_left(self):
        """ Turns the agent left. In other words, theta
        is increased by 90 degrees.

        Returns
        -------
        executed: bool
            Always True.

        """
        self.theta += 90
        while self.theta >= 360:
            self.theta -= 360
        self.trace.append((self.x, self.y, self.theta))
        return True


    def turn_right(self):
        """ Turns the agent right. In other words, theta
        is decreased by 90 degrees.

        Returns
        -------
        executed: bool
            Always True.

        """
        self.theta -= 90
        while self.theta < 0:
            self.theta += 360
        self.trace.append((self.x, self.y, self.theta))
        return True


    def draw_state(self, ax = None):
        """ Draws the current state.

        Parameters
        ----------
        ax: axis handle (default = None)
            An axis handle into which the state should be drawn. If not
            provided, a new figure is opened.

        """
        drawing.draw_state(self.map, self.x, self.y, self.theta, None, ax = ax)

    def draw_trace(self):
        """ Draws the trace of all of the agent's motion so far.

        """
        trace_with_mem = [(x, y, theta, None) for (x, y, theta) in self.trace]
        drawing.draw_trace(trace_with_mem, { 'map' : self.map })
