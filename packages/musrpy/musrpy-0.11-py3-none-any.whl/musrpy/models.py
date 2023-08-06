import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


def exp_decay_osc(x: float, initial: float, asym: float, frequency: float, phase: float) -> float:
    """
    Decaying sinusoid
    """
    return initial * np.exp(-0.455 * x) * (1 + asym * np.cos(frequency * x + phase))


def sinusoid(x: float, amplitude: float, frequency: float, phase: float, offset: float) -> float:
    """
    General sinusoidal curve
    https://en.wikipedia.org/wiki/Sinusoidal_model
    """
    return amplitude * np.cos(frequency * x + phase) + offset


def exp_decay(x, initial: float, decay: float) -> float:
    """
    Exponential decay model
    https://en.wikipedia.org/wiki/Exponential_decay
    """
    return initial * np.exp(-decay * x)


def linear(x, m: float, c: float) -> float:
    """
    Straight line y=mx+c
    """
    return m * x + c


functions = {
    "ExpDecayOsc": (exp_decay_osc,
                    [100, 0.2, 8.5, 1],
                    "y = {0:.3f}*exp(-0.455*x)(1 + {1:.3f}*cos({2:.3f}*x + {3:.3f})"),
    "ExpDecay": (exp_decay,
                 [100, 0.455],
                 "y = {0:.3f}*exp(-{1:.3f}*x)"),
    "Sinusoid": (sinusoid,
                 [0.2, 8.5, 0.1, 0.1],
                 "y = {0:.3f}*cos({1:.3f}*x + {2:.3f}) + {3:.3f}"),
    "Linear": (linear,
               [1, 1],
               "y = {0:.3f}*x + {:.3f}")
}


class FitFunction:

    def __init__(self, function: str):
        self.function = function
        self.initial_guess = functions[function][1]
        self.model = None
        self.graph_label = None
        self.rmse = None

    def curve(self, x, *parameters):
        return functions[self.function][0](x, *parameters)

    def fit(self, time: pd.DataFrame, data: pd.DataFrame,
            initial_guess: list = None, bounds: tuple = None, start_time: float = 0, end_time: float = 15):
        if initial_guess is None:
            initial_guess = self.initial_guess
        if bounds is None:
            bounds = (-np.inf, np.inf)
        self.model = curve_fit(functions[self.function][0],
                               time[(time >= start_time) & (time <= end_time)],
                               data[(time >= start_time) & (time <= end_time)],
                               p0=initial_guess, bounds=bounds)
        self.rmse = np.sqrt(((self.curve(time, *self.model[0]) - data) ** 2).mean())
        self.graph_label = functions[self.function][2].format(*self.model[0])
