"""
Provides functions to give feedback to students who try to develop
an agent.

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

from starcode_labyrinth import logic
from starcode_labyrinth import drawing

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2022, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '0.2.1'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'benjamin.paassen@dfki.de'



def evaluate_agent(agent, levels = None, start_memory = None):
    """ Executed an agent on the given list of levels until a
    level fails and gives feedback for each executed level.
    For successful levels, the feedback is given via print.
    For failed levels, the feedback is given by drawing the trace
    where it fails. Note that prints will be in German.

    Parameters
    ----------
    agent: fun
        A function taking two input arguments and returning two
        output arguments. The inputs are whether the field in front
        of the agent is free (True) or blocked (False) and the current
        memory. The outputs are expected to be the next action
        (either 'left', 'right', or 'go') and the next memory state.
    levels: list (default = default levels)
        A list of levels as specified in the 'draw_level' function.
    start_memory: object (default = None)
        The initial memory for the agent.

    """
    if levels is None:
        levels = logic.levels

    if len(levels) < 1:
        raise ValueError('We need at least one level for evaluation.')

    for l in range(len(levels)):
        level = levels[l]
        X = level['map']
        n, m = X.shape
        # execute the agent on the current level
        trace = logic.execute_agent(agent, level, start_memory)
        # check if the execution was a success
        x, y, theta, mem = trace[-1]
        success = X[n-y-1, x] == 2
        if success:
            # if it was, give textual feedback on the number of turns needed
            if len(trace) - 1 == level['min_turns']:
                print('Level %d geschafft nach %d Zügen. Glückwunsch, besser geht es nicht!' % (l+1, len(trace)-1))
            else:
                print('Level %d geschafft nach %d Zügen. Optimal wären %d Züge.' % (l+1, len(trace)-1, level['min_turns']))
        else:
            # otherwise, draw the trace and stop the evaluation
            print('Level %d nicht geschafft nach %d Zügen. Hier sind alle bis dahin ausgeführten Züge.' % (l+1, len(trace)-1))
            drawing.draw_trace(trace, level)
            break
