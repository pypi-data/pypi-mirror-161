# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from importlib import resources


def f(self, t, temp):
    body_data = pd.read_csv(resources.open_text('humanthermalmodel', 'body_data.csv'))
    print(self.height)
    d_temp = np.array([

    ])
    return d_temp


def basal_met(height=1.72, weight=74.43, age=20,
            sex="male", equation="harris-benedict"):
    """
    Calculate basal metabolic rate [W].

    Parameters
    ----------
    height : float, optional
        Body height [m]. The default is 1.72.
    weight : float, optional
        Body weight [kg]. The default is 74.43.
    age : float, optional
        Age [years]. The default is 20.
    sex : str, optional
        Choose male or female. The default is "male".
    equation : str, optional
        Choose harris-benedict or ganpule. The default is "harris-benedict".

    Returns
    -------
    BMR : float
        Basal metabolic rate [W].

    """

    if equation=="harris-benedict":
        if sex=="male":
            bmr = 88.362 + 13.397*weight + 500.3*height - 5.677*age
        else:
            bmr = 447.593 + 9.247*weight + 479.9*height - 4.330*age

    elif equation=="harris-benedict_origin":
        if sex=="male":
            bmr = 66.4730 + 13.7516*weight + 500.33*height - 6.7550*age
        else:
            bmr = 655.0955 + 9.5634*weight + 184.96*height - 4.6756*age

    elif equation=="japanese" or equation=="ganpule":
        # Ganpule et al., 2007, https://doi.org/10.1038/sj.ejcn.1602645
        if sex=="male":
            bmr = 0.0481*weight + 2.34*height - 0.0138*age - 0.4235
        else:
            bmr = 0.0481*weight + 2.34*height - 0.0138*age - 0.9708
        bmr *= 1000 / 4.186

    bmr *= 0.048  # [kcal/day] to [W]

    return bmr