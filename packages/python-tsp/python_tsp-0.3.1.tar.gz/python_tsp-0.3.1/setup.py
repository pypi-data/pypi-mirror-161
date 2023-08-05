# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_tsp',
 'python_tsp.distances',
 'python_tsp.exact',
 'python_tsp.heuristics']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'requests>=2.28.0,<3.0.0', 'tsplib95>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'python-tsp',
    'version': '0.3.1',
    'description': 'Simple library to solve the Traveling Salesperson Problem in pure Python.',
    'long_description': "=================\nPython TSP Solver\n=================\n\n``python-tsp`` is a library written in pure Python for solving typical Traveling\nSalesperson Problems (TSP). It can work with symmetric and asymmetric versions.\n\n\nInstallation\n============\n.. code:: bash\n\n  pip install python-tsp\n\n\nExamples\n========\n\nGiven a distance matrix as a numpy array, it is easy to compute a Hamiltonian\npath with least cost. For instance, to use a Dynamic Programming method:\n\n.. code:: python\n\n   import numpy as np\n   from python_tsp.exact import solve_tsp_dynamic_programming\n\n   distance_matrix = np.array([\n       [0,  5, 4, 10],\n       [5,  0, 8,  5],\n       [4,  8, 0,  3],\n       [10, 5, 3,  0]\n   ])\n   permutation, distance = solve_tsp_dynamic_programming(distance_matrix)\n\nThe solution will be ``[0, 1, 3, 2]``, with total distance 17. Notice it is\nalways a closed path, so after node 2 we go back to 0.\n\nTo solve the same problem with a metaheuristic method:\n\n.. code:: python\n\n   from python_tsp.heuristics import solve_tsp_simulated_annealing\n\n   permutation, distance = solve_tsp_simulated_annealing(distance_matrix) \n\nKeep in mind that, being a metaheuristic, the solution may vary from execution\nto execution, and there is no guarantee of optimality. However, it may be a\nway faster alternative in larger instances.\n\nIf you with for an open TSP version (it is not required to go back to the\norigin), just set all elements of the first column of the distance matrix to\nzero:\n\n.. code:: python\n\n   distance_matrix[:, 0] = 0\n   permutation, distance = solve_tsp_dynamic_programming(distance_matrix)\n\nand in this case we obtain ``[0, 2, 3, 1]``, with distance 12. Notice that in\nthis case the distance matrix is actually asymmetric, and the methods here are\napplicable as well.\n\nThe previous examples assumed you already had a distance matrix. If that is not\nthe case, the ``distances`` module has prepared some functions to compute an \nEuclidean distance matrix or a\n`Great Circle Distance <https://en.wikipedia.org/wiki/Great-circle_distance>`_.\n\nFor example, if you have an array where each row has the latitude and longitude\nof a point,\n\n.. code:: python\n\n   import numpy as np\n   from python_tsp.distances import great_circle_distance_matrix\n\n   sources = np.array([\n       [ 40.73024833, -73.79440675],\n       [ 41.47362495, -73.92783272],\n       [ 41.26591   , -73.21026228],\n       [ 41.3249908 , -73.507788  ]\n   ])\n   distance_matrix = great_circle_distance_matrix(sources)\n\nSee the `project's repository <https://github.com/fillipe-gsm/python-tsp>`_ \nfor more examples and a list of available methods.\n",
    'author': 'Fillipe Goulart',
    'author_email': 'fillipe.gsm@tutanota.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fillipe-gsm/python-tsp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
