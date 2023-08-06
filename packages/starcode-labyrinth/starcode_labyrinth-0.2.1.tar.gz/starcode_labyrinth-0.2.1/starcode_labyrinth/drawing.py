"""
Provides drawing functions for labyrinths.

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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import matplotlib

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2022, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '0.2.1'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'benjamin.paassen@dfki.de'


def draw_state(X, agent_x, agent_y, agent_theta, mem = None, ax = None):
    """ Draws the current state of a labyrinth search.

    Parameters
    ----------
    X: numpy.ndarray
        A two-dimensional integer array representing the map,
        where X[i, j] = 0 if cell X[i, j] in the labyrinth is
        blocked, X[i, j] = 1 if it is free, and 2 if it is the goal.
    agent_x: int
        The x position of the agent on the map.
    agent_y: int
        The y position of the agent on the map.
    agent_theta: int
        The orientation of the agent (in degrees).
        0 degrees means pointing to the right,
        90 degrees means pointing upwards, 180 degrees means pointing
        to the left, and 270 degrees means pointing downwards.
    mem: object (default = None)
        Some memory content which will be printed on the title
        (if it is not None).
    ax: axis handle (default = None)
        An axis handle into which the state should be drawn. If not
        provided, a new figure is opened.

    """

    draw_new_figure = ax is None

    if draw_new_figure:
        fig = plt.figure(figsize = (4, 4))
        ax = fig.add_subplot(111)

    # draw the map
    n, m = X.shape

    for i in range(m):
        for j in range(n):
            if X[n-j-1, i] == 0:
                rect = Rectangle((i, j), 1, 1, edgecolor = 'none', facecolor = 'tab:gray')
                ax.add_patch(rect)
            elif X[n-j-1, i] == 2:
                # draw a star
                plt.plot([i+0.24, i+0.76], [j+0.35, j+0.65], color = 'tab:orange')
                plt.plot([i+0.24, i+0.76], [j+0.65, j+0.35], color = 'tab:orange')
                plt.plot([i+0.5, i+0.5], [j+0.2, j+0.8], color = 'tab:orange')

    # draw agent
    triangle = np.array([[-0.3, -0.3], [+0.3,0], [-0.3, +0.3]])

    poly = plt.Polygon(triangle, color='tab:blue')
    transform = matplotlib.transforms.Affine2D().rotate(agent_theta / 180 * np.pi).translate(agent_x + 0.5, agent_y + 0.5) + ax.transData
    poly.set_transform(transform)

    ax.add_patch(poly)

    # draw x and y ticks as well as grid lines
    ax.set_xticks(list(range(m)))
    ax.set_yticks(list(range(n)))
    ax.set_xlim([0, m])
    ax.set_ylim([0, n])
    plt.grid()
    # show memory conent
    if mem is not None:
        plt.title('memory: %s' % str(mem))

    if draw_new_figure:
        plt.show()


def draw_level(level, ax = None):
    """ Draws a level, that is, the initial state of an agent
    when trying it.

    Parameters
    ----------
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
    ax: axis handle (default = None)
        An axis handle into which the state should be drawn. If not
        provided, a new figure is opened.

    """
    draw_state(level['map'], level['start_x'], level['start_y'], level['start_theta'], None, ax)


def draw_levels(levels):
    """ Draws all levels in the given list of levels and plots them
    as a new figure.

    Parameters
    ----------
    levels: list
        A list of levels as specified in the 'draw_level' function.

    """
    if len(levels) < 1:
        raise ValueError('We need at least one level to draw.')

    # draw at most six levels in a row
    num_rows = len(levels) // 6 + 1
    num_cols = min(6, len(levels))

    # create a new figure
    fig = plt.figure(figsize = (4 * num_cols, 4 * num_rows))
    # draw every single level
    for l in range(len(levels)):
        ax = fig.add_subplot(num_rows, num_cols, l + 1)
        draw_level(levels[l], ax)

    plt.show()


def draw_trace(trace, level):
    """ Draws a trace of an agent's execution behavior on the given level.

    Parameters
    ----------
    trace: list
        A list of states of an agent's behavior on a level.
        Each state should be a tuple x[t], where x[t][0] is
        the agent's x position at time t, x[t][1] is the
        agent's y position at time t, x[t][2] is the agent's
        orientation (in degrees) at time t, and x[t][3] is the
        agent's memory at time t.
    level: dict
        A level description as specified in the draw_level
        function.

    """
    if len(trace) < 1:
        raise ValueError('We need at least one level to draw.')
    # draw at most six levels in a row
    num_rows = len(trace) // 6 + 1
    num_cols = min(6, len(trace))
    # create a new figure
    fig = plt.figure(figsize = (4 * num_cols, 4 * num_rows))
    # draw every single level
    t = 1
    for (x, y, o, mem) in trace:
        ax = fig.add_subplot(num_rows, num_cols, t)
        draw_state(level['map'], x, y, o, mem, ax)
        t += 1
    plt.show()
