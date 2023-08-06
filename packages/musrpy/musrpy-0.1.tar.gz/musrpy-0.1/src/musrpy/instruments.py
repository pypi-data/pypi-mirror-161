import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import uproot as up
from models import FitFunction
# from src.musrpy.models import FitFunction

class MuonInstrument:
    """Class representing a muon instrument. Instance attributes are name of instrument, number of detectors, and how
    detectors are grouped.
    """

    emu_standard_groups = {
        "forward_outer": (0, 16),
        "forward_middle": (16, 32),
        "forward_inner": (32, 48),
        "backward_outer": (48, 64),
        "backward_middle": (64, 80),
        "backward_inner": (80, 96),
        "forward_total": (0, 48),
        "backward_total": (48, 96)
    }

    chronus_standard_groups = {
        "forward": (0, 303),
        "backward": (303, 606)
    }

    chronus_tf_groups = {
        "trans1": [23, 24, 25, 26, 55, 56, 57, 58, 93, 94, 95, 96, 97, 136, 137, 138, 139, 140, 141, 184, 185, 186, 187,
                   188, 189, 237, 238, 239, 240, 241, 242, 293, 294, 295, 296, 297, 298, 299, 326, 327, 328, 329, 358,
                   359, 360, 361, 396, 397, 398, 399, 400, 439, 440, 441, 442, 443, 444, 487, 488, 489, 490, 491, 492,
                   540, 541, 542, 543, 544, 545, 596, 597, 598, 599, 600, 601, 602],
        "trans2": [27, 28, 29, 30, 59, 60, 61, 62, 63, 98, 99, 100, 101, 102, 142, 143, 144, 145, 146, 147, 190, 191,
                   192, 193, 194, 195, 196, 243, 244, 245, 246, 247, 248, 249, 300, 301, 302, 0, 1, 330, 331, 332, 333,
                   362, 363, 364, 365, 366, 401, 402, 403, 404, 405, 445, 446, 447, 448, 449, 450, 493, 494, 495, 496,
                   497, 498, 499, 546, 547, 548, 549, 550, 551, 552, 603, 604, 605, 303, 304],
        "trans3": [2, 3, 4, 5, 31, 32, 33, 34, 64, 65, 66, 67, 68, 103, 104, 105, 106, 107, 108, 148, 149, 150, 151,
                   152, 153, 197, 198, 199, 200, 201, 202, 250, 251, 252, 253, 254, 255, 256, 305, 306, 307, 308, 334,
                   335, 336, 337, 367, 368, 369, 370, 371, 406, 407, 408, 409, 410, 411, 451, 452, 453, 454, 455, 456,
                   500, 501, 502, 503, 504, 505, 553, 554, 555, 556, 557, 558, 559],
        "trans4": [6, 7, 8, 35, 36, 37, 38, 69, 70, 71, 72, 73, 109, 110, 111, 112, 113, 154, 155, 156, 157, 158, 159,
                   203, 204, 205, 206, 207, 208, 209, 257, 258, 259, 260, 261, 262, 263, 309, 310, 311, 338, 339, 340,
                   341, 372, 373, 374, 375, 376, 412, 413, 414, 415, 416, 457, 458, 459, 460, 461, 462, 506, 507, 508,
                   509, 510, 511, 512, 560, 561, 562, 563, 564, 565, 566],
        "trans5": [9, 10, 11, 12, 39, 40, 41, 42, 74, 75, 76, 77, 78, 114, 115, 116, 117, 118, 119, 160, 161, 162, 163,
                   164, 165, 210, 211, 212, 213, 214, 215, 216, 264, 265, 266, 267, 268, 269, 270, 312, 313, 314, 315,
                   342, 343, 344, 345, 377, 378, 379, 380, 381, 417, 418, 419, 420, 421, 422, 463, 464, 465, 466, 467,
                   468, 513, 514, 515, 516, 517, 518, 519, 567, 568, 569, 570, 571, 572, 573],
        "trans6": [13, 14, 15, 43, 44, 45, 46, 79, 80, 81, 82, 120, 121, 122, 123, 124, 166, 167, 168, 169, 170, 171,
                   217, 218, 219, 220, 221, 222, 271, 272, 273, 274, 275, 276, 277, 278, 316, 317, 318, 346, 347, 348,
                   349, 382, 383, 384, 385, 423, 424, 425, 426, 427, 469, 470, 471, 472, 473, 474, 520, 521, 522, 523,
                   524, 525, 574, 575, 576, 577, 578, 579, 580, 581],
        "trans7": [16, 17, 18, 19, 47, 48, 49, 50, 83, 84, 85, 86, 87, 125, 126, 127, 128, 129, 130, 172, 173, 174, 175,
                   176, 177, 223, 224, 225, 226, 227, 228, 229, 279, 280, 281, 282, 283, 284, 285, 319, 320, 321, 322,
                   350, 351, 352, 353, 386, 387, 388, 389, 390, 428, 429, 430, 431, 432, 433, 475, 476, 477, 478, 479,
                   480, 526, 527, 528, 529, 530, 531, 532, 582, 583, 584, 585, 586, 587, 588],
        "trans8": [20, 21, 22, 51, 52, 53, 54, 88, 89, 90, 91, 92, 131, 132, 133, 134, 135, 178, 179, 180, 181, 182,
                   183, 230, 231, 232, 233, 234, 235, 236, 286, 287, 288, 289, 290, 291, 292, 323, 324, 325, 354, 355,
                   356, 357, 391, 392, 393, 394, 395, 434, 435, 436, 437, 438, 481, 482, 483, 484, 485, 486, 533, 534,
                   535, 536, 537, 538, 539, 589, 590, 591, 592, 593, 594, 595]
    }

    chronus_tf_groups_2 = {
        "trans1": [23, 24, 25, 26, 55, 56, 57, 58, 93, 94, 95, 96, 97, 136, 137, 138, 139, 140, 141, 184, 185, 186, 187,
                   188, 189, 237, 238, 239, 240, 241, 242, 293, 294, 295, 296, 297, 298, 299],
        "trans2": [27, 28, 29, 30, 59, 60, 61, 62, 63, 98, 99, 100, 101, 102, 142, 143, 144, 145, 146, 147, 190, 191,
                   192, 193, 194, 195, 196, 243, 244, 245, 246, 247, 248, 249, 300, 301, 302, 0, 1],
        "trans3": [2, 3, 4, 5, 31, 32, 33, 34, 64, 65, 66, 67, 68, 103, 104, 105, 106, 107, 108, 148, 149, 150, 151,
                   152, 153, 197, 198, 199, 200, 201, 202, 250, 251, 252, 253, 254, 255, 256],
        "trans4": [6, 7, 8, 35, 36, 37, 38, 69, 70, 71, 72, 73, 109, 110, 111, 112, 113, 154, 155, 156, 157, 158, 159,
                   203, 204, 205, 206, 207, 208, 209, 257, 258, 259, 260, 261, 262, 263],
        "trans5": [9, 10, 11, 12, 39, 40, 41, 42, 74, 75, 76, 77, 78, 114, 115, 116, 117, 118, 119, 160, 161, 162, 163,
                   164, 165, 210, 211, 212, 213, 214, 215, 216, 264, 265, 266, 267, 268, 269, 270],
        "trans6": [13, 14, 15, 43, 44, 45, 46, 79, 80, 81, 82, 120, 121, 122, 123, 124, 166, 167, 168, 169, 170, 171,
                   217, 218, 219, 220, 221, 222, 271, 272, 273, 274, 275, 276, 277, 278],
        "trans7": [16, 17, 18, 19, 47, 48, 49, 50, 83, 84, 85, 86, 87, 125, 126, 127, 128, 129, 130, 172, 173, 174, 175,
                   176, 177, 223, 224, 225, 226, 227, 228, 229, 279, 280, 281, 282, 283, 284, 285],
        "trans8": [20, 21, 22, 51, 52, 53, 54, 88, 89, 90, 91, 92, 131, 132, 133, 134, 135, 178, 179, 180, 181, 182,
                   183, 230, 231, 232, 233, 234, 235, 236, 286, 287, 288, 289, 290, 291, 292],
        "trans9": [326, 327, 328, 329, 358, 359, 360, 361, 396, 397, 398, 399, 400, 439, 440, 441, 442, 443, 444, 487,
                   488, 489, 490, 491, 492, 540, 541, 542, 543, 544, 545, 596, 597, 598, 599, 600, 601, 602],
        "trans10": [330, 331, 332, 333, 362, 363, 364, 365, 366, 401, 402, 403, 404, 405, 445, 446, 447, 448, 449, 450,
                    493, 494, 495, 496, 497, 498, 499, 546, 547, 548, 549, 550, 551, 552, 603, 604, 605, 303, 304],
        "trans11": [305, 306, 307, 308, 334, 335, 336, 337, 367, 368, 369, 370, 371, 406, 407, 408, 409, 410, 411, 451,
                    452, 453, 454, 455, 456, 500, 501, 502, 503, 504, 505, 553, 554, 555, 556, 557, 558, 559],
        "trans12": [309, 310, 311, 338, 339, 340, 341, 372, 373, 374, 375, 376, 412, 413, 414, 415, 416, 457, 458, 459,
                    460, 461, 462, 506, 507, 508, 509, 510, 511, 512, 560, 561, 562, 563, 564, 565, 566],
        "trans13": [312, 313, 314, 315, 342, 343, 344, 345, 377, 378, 379, 380, 381, 417, 418, 419, 420, 421, 422, 463,
                    464, 465, 466, 467, 468, 513, 514, 515, 516, 517, 518, 519, 567, 568, 569, 570, 571, 572, 573],
        "trans14": [316, 317, 318, 346, 347, 348, 349, 382, 383, 384, 385, 423, 424, 425, 426, 427, 469, 470, 471, 472,
                    473, 474, 520, 521, 522, 523, 524, 525, 574, 575, 576, 577, 578, 579, 580, 581],
        "trans15": [319, 320, 321, 322, 350, 351, 352, 353, 386, 387, 388, 389, 390, 428, 429, 430, 431, 432, 433, 475,
                    476, 477, 478, 479, 480, 526, 527, 528, 529, 530, 531, 532, 582, 583, 584, 585, 586, 587, 588],
        "trans16": [323, 324, 325, 354, 355, 356, 357, 391, 392, 393, 394, 395, 434, 435, 436, 437, 438, 481, 482, 483,
                    484, 485, 486, 533, 534, 535, 536, 537, 538, 539, 589, 590, 591, 592, 593, 594, 595]
    }

    def __init__(self, name: str, num_detectors: int, detector_groups: dict):
        """Dictionary of detector groups has following formats:
        {"detector_group_one": (start_slice, end_slice),
        "detector_group_two": ...  }
        For example, the first 16 detectors would be (0, 16), and

        {"detector_group_one": [detector_ids],
        "detector_group_two": ...  }.


        :param name: Name of muon instrument
        :param num_detectors: Total number of detectors for the instrument
        :param detector_groups: Dictionary of detector groups. Names are keys, values are slices.
        """
        self.num_detectors = num_detectors
        self.groups = detector_groups
        self.name = name
        self.model_dict = {}
        self.mac = None
        self.v1190 = None
        self.data = None
        self.num_events = None
        self.path = None
        self.simana_histograms = None
        self.sim_histograms = None

    def __repr__(self):
        return f"MuonInstrument({self.name})"

    def group_data(self):
        """Groups the detector histograms according to the instrument grouping.

        """
        dataframe = self.data.copy()
        for grouping in self.groups:
            if isinstance(self.groups[grouping], tuple):
                start, end = self.groups[grouping]
                dataframe[grouping] = self.data.iloc[:, 1:(self.num_detectors + 1)].iloc[:, start:end].sum(axis=1)
            elif isinstance(self.groups[grouping], list):
                grouping_list = self.groups[grouping]
                dataframe[grouping] = self.data.iloc[:, 1:(self.num_detectors + 1)].iloc[:, grouping_list].sum(axis=1)
            else:
                print("Group must be defined using list or tuple")
                return
        dataframe.drop(list(range(self.num_detectors)), axis=1, inplace=True)
        self.data = dataframe

    def load_data(self, mac: int, v1190: int, path: str, bins: int | None = 2000):
        """Loads data from ROOT histogram and parses into pandas dataframe with shape
        time detector1 detector2 ...
          .       .         .
          .       .         .
          .       .         .

        Path must be to the folder containing the mac file and the data folder:

        directory
        ---data
           ---his_123_123.v1190.root
           ---musr_123.root
        ---123.mac
        ---123.v1190

        :param mac: mac file of simulation
        :param v1190: v1190 file of simulation
        :param path: Path to directory containing mac file and data folder
        :param bins: Approximate number of bins for the histogram
        :return: Dataframe of detector counts
        """
        detectors = []
        with open(f"{path}/{mac}.mac", "r") as f:
            # Grabs number of events from mac file
            for line in f.readlines():
                line_parsed = line.replace(r"\n", "")
                if "/run/beamOn" in line_parsed and "#" not in line_parsed:
                    self.num_events = int(line.replace(r"\n", "").split(" ")[1])
        with up.open(fr"{path}/data/his_{mac}_{v1190}.v1190.root") as f:
            for detector_num in range(self.num_detectors):
                detector_hist = f[f.keys()[2 + detector_num]].to_hist()
                if bins > detector_hist.shape[0]:
                    bins = detector_hist.shape[0]
                    print(f"Bins must be less than or equal to the number of bins {bins} defined in the musrSimAna "
                          f"steering file. Bins set to {bins}")
                detector_hist = detector_hist[::complex(0, round(detector_hist.shape[0] / bins))]
                if detector_num == 0:
                    # gets the times from the first detector histogram
                    detectors.append(detector_hist.axes.centers[0])
                    detectors.append(detector_hist.values())
                else:
                    detectors.append(detector_hist.values())
        data = pd.DataFrame(np.stack(detectors, axis=1), columns=["time"] + list(range(self.num_detectors)))
        self.data = data
        self.mac = mac
        self.v1190 = v1190
        self.path = path

    def load_and_group_data(self, mac: int, v1190: int, path: str, bins: int = 2000):
        """Combines load_data and group_data into a single method.

        :param mac: mac file of simulation
        :param v1190: v1190 file of simulation
        :param path: Path to directory containing mac file and data folder
        :param bins: Approximate number of bins in the histogram
        :return: Dataframe of detector group counts
        """
        self.load_data(mac, v1190, path=path, bins=bins)
        self.group_data()

    def fit(self, name: str, function: str,
            start_time: float = 0, end_time: float = 15, initial_guess: list = None, bounds: tuple = None):
        """Fits curve to detector group histograms. Uses scipy's curve_fit method.
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html

        :param name: Name of detector group/pair to fit.
        :param function: Function to fit to data
        :param start_time: Start time to regress from
        :param end_time: End time to regress from
        :param initial_guess: List of initial parameters for regression.
        :param bounds: Option to place bounds on parameters during fit
        """
        if hasattr(self, f"pair_{name}"):
            group_model = FitFunction(function)
            group_model.fit(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                            getattr(self, f"pair_{name}").asymmetry[0][(self.data["time"] >= start_time)
                                                                       & (self.data["time"] <= end_time)],
                            start_time=start_time, end_time=end_time, initial_guess=initial_guess, bounds=bounds)
        elif name in self.groups:
            group_model = FitFunction(function)
            group_model.fit(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                            self.data[name][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                            start_time=start_time, end_time=end_time, initial_guess=initial_guess, bounds=bounds)
        else:
            print("Enter valid group or pair!")
            return
        self.model_dict[name] = group_model

    def plot_counts(self, group: str | list[str], plot_fit: bool,
                    start_time: float = 0, end_time: float = 15, save_path: str = None, show_plot: bool = False,
                    initial_guess: list = None, bounds: tuple = None):
        """Plots detector counts against time for a group. Option to plot fitted curve to data.

        :param group: Detector grouping or list of groups to plot
        :param plot_fit: Fits and plots curve
        :param start_time: time to start plotting from
        :param end_time: time to end plotting at
        :param save_path: Optional directory to save figures
        :param show_plot: Option to output plot to terminal
        :param initial_guess: Option to change starting point for iteration. Defaults defined in models.py
        :param bounds: Option to place bounds on parameters.
        """
        if isinstance(group, str):
            groups = [group]
        elif isinstance(group, list):
            groups = group
        else:
            print("Group must be a string or list of strings")
            return
        fig, ax = plt.subplots(dpi=200)
        for grouping in groups:
            ax.scatter(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                       self.data[grouping][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                       s=1, label=f"{grouping}")
            if plot_fit:
                self.fit(grouping, "ExpDecayOsc", start_time=start_time, end_time=end_time, initial_guess=initial_guess,
                         bounds=bounds)
                ax.plot(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                        self.model_dict[grouping].curve(
                            self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                            *self.model_dict[grouping].model[0]),
                        "r-", label=self.model_dict[grouping].graph_label)
            ax.set_title(f"{self.name}, {self.mac}.mac, {self.v1190}.v1190")
            ax.set_xlabel(r"time ($\mu$s)")
            ax.set_ylabel("n")
            ax.legend(loc="upper center", fontsize="x-small")
            plt.tight_layout()
        if save_path is None:
            pass
        else:
            os.makedirs(f"{save_path}/{self.mac}_{self.v1190}_plots", exist_ok=True)
            fig.savefig(
                f"{save_path}/{self.mac}_{self.v1190}_plots/{self.mac}_{self.v1190}_{'_'.join(str(x) for x in groups)}.png",
                dpi=200)
        if show_plot:
            plt.show()

    def plot_asymmetry(self, pair: str, plot_fit: bool,
                       start_time: float = 0, end_time: float = 15, save_path: str = None, show_plot: bool = False,
                       initial_guess: list = None, bounds: tuple = None):
        """Plots asymmetry for a pair of groups. Option to plot fitted curve to data.

        :param pair: Group pair to plot
        :param plot_fit: Fits and plots curve
        :param start_time: time to start plotting from
        :param end_time: time to end plotting at
        :param save_path: Optional directory to save figures
        :param show_plot: Option to output plot to terminal
        :param initial_guess: Option to change starting point for iteration. Defaults defined in models.py
        :param bounds: Option to place bounds on parameters.
        """
        if getattr(self, f"pair_{pair}").asymmetry is None:
            getattr(self, f"pair_{pair}").get_asymmetry()
        plt.scatter(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                    getattr(self, f"pair_{pair}").asymmetry[0][(self.data["time"] >= start_time)
                                                               & (self.data["time"] <= end_time)], s=1)
        if plot_fit:
            self.fit(pair, "Sinusoid", start_time=start_time, end_time=end_time,
                     initial_guess=initial_guess, bounds=bounds)
            plt.plot(self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                     self.model_dict[pair].curve(
                         self.data["time"][(self.data["time"] >= start_time) & (self.data["time"] <= end_time)],
                         *self.model_dict[pair].model[0]),
                     "r-", label=self.model_dict[pair].graph_label)
        plt.title(f"{self.name}, {self.mac}, pair_{pair} asymmetry")
        plt.xlabel(r"time ($\mu$s)")
        plt.ylabel("asymmetry")
        if save_path is None:
            pass
        else:
            os.makedirs(f"{save_path}/{self.mac}_plots", exist_ok=True)
            plt.savefig(f"{save_path}/{self.mac}_plots/{self.mac}_pair_{pair}_asymmetry.png", dpi=200)
        if show_plot:
            plt.show()

    def get_histograms(self) -> tuple[list, list]:
        with up.open(fr"{self.path}/data/his_{self.mac}_{self.v1190}.v1190.root") as f1:
            simana_histograms = [hist[:-2] for hist in f1.keys()]
        with up.open(fr"{self.path}/data/musr_{self.mac}.root") as f2:
            sim_histograms = [hist for hist in f2["t1"].keys()]
        self.simana_histograms = simana_histograms
        self.sim_histograms = sim_histograms
        return self.sim_histograms, self.simana_histograms

    def plot_histogram(self, hist_name: str,
                       bins: int | tuple[int, int] | None = None,
                       data_range: tuple[float, float] | tuple[tuple[float, float], tuple[float, float]] | None = None,
                       show_plot: bool = True,
                       save_path: str | None = None) -> None | tuple:
        if self.sim_histograms is None or self.simana_histograms is None:
            self.get_histograms()
        if hist_name in self.simana_histograms:
            with up.open(fr"{self.path}/data/his_{self.mac}_{self.v1190}.v1190.root")[f"{hist_name};1"] as f:
                if f.axes.__len__() == 2:
                    fig, ax = plt.subplots(dpi=200)
                    h = f.to_hist()
                    if data_range is None:
                        data_range = ((h.axes[0].edges.min(), h.axes[0].edges.max()),
                                      (h.axes[1].edges.min(), h.axes[1].edges.max()))
                    if bins is None:
                        bins = (h.axes.size[0], h.axes.size[1])
                    h = h[complex(0, data_range[0][0]):complex(0, data_range[0][1]),
                          complex(0, data_range[1][0]):complex(0, data_range[1][1])]
                    h[::complex(0, int(h.shape[0] / bins[0])),
                      ::complex(0, int(h.shape[1] / bins[1]))].plot(ax=ax)
                    ax.set_title(f"{f.title}, {f.name}, {self.mac}.mac", fontsize="small")
                    plt.tight_layout()
                    hist_data = f.to_numpy()
                else:
                    if f.axis().labels() is None:
                        fig, ax = plt.subplots(dpi=200)
                        h = f.to_hist()
                        if data_range is None:
                            data_range = (h.axes.edges[0].min(), h.axes.edges[0].max())
                        if bins is None:
                            bins = 100
                        h = h[complex(0, data_range[0]):complex(0, data_range[1])]
                        h[::complex(0, int(h.shape[0] / bins))].plot(ax=ax)
                        ax.set_xlabel(f.axis().all_members["fTitle"])
                        ax.set_ylabel("N")
                        ax.set_title(f"{f.title}, {f.name}, {self.mac}.mac", fontsize="small")
                        plt.tight_layout()
                        hist_data = f.to_numpy()
                    else:
                        fig, ax = plt.subplots(dpi=200)
                        labels, heights = f.axis().labels(), f.values()
                        ax.bar(labels, heights, yerr=[np.sqrt(x) for x in heights], capsize=4)
                        ax.set_ylabel("N")
                        ax.set_title(f'{f.title}, {f.name}, {self.mac}.mac', fontsize="small")
                        plt.xticks(rotation=-25, ha="left", size=7)
                        plt.tight_layout()
                        hist_data = labels, heights
        elif hist_name in self.sim_histograms:
            with up.open(fr"{self.path}/data/musr_{self.mac}.root") as f:
                fig, ax = plt.subplots(dpi=200)
                #  Use pandas to implement data_range.
                values = f["t1"][hist_name].array(library="pd")
                if data_range is None:
                    data_range = (values.min(), values.max())
                if bins is None:
                    bins = 100
                ax.hist(values[(values >= data_range[0]) & (values <= data_range[1])], bins=bins)
                ax.set_xlabel(hist_name)
                ax.set_ylabel("N")
                ax.set_title(f"{hist_name}, {self.mac}.mac", fontsize="small")
                plt.tight_layout()
                hist_data = values
        else:
            print("Enter valid histogram!")
            return
        if save_path is None:
            pass
        else:
            os.makedirs(f"{save_path}/{self.mac}_plots", exist_ok=True)
            fig.savefig(f"{save_path}/{self.mac}_plots/{self.mac}_{f.name}.png", dpi=200)
        if show_plot:
            plt.show()
        plt.clf()
        return hist_data

    def create_pair(self, pair_name: str, group_1: str, group_2: str):
        """Creates a pairing of detector groups. Asymmetry between the groups can then be calculated.

        :param pair_name: Name of pair
        :param group_1: First detector group in pair
        :param group_2: Second detector group in pair
        """
        if hasattr(self, f"pair_{pair_name}"):
            print("Pair already exists with this name!")
        else:
            setattr(self, f"pair_{pair_name}", Pair(pair_name, self, group_1, group_2))


class Pair:
    """Object representing a pairing of detector groups."""

    def __init__(self, name: str, instrument: MuonInstrument, group_1: str, group_2: str):
        """A pairing of detector groups.

        :param group_1: First detector group in the pair, known as "forward"
        :param group_2: Second detector group in the pair, known as "backward
        """
        self.name = name
        self.instrument = instrument
        self.group_1 = group_1
        self.group_2 = group_2
        self.alpha = None
        self.asymmetry = None

    def __repr__(self):
        return f"Pair_{self.name}({self.group_1}, {self.group_2})"

    def get_alpha(self) -> float:
        """Estimates alpha (balance parameter) between the two groups. Used in calculation for asymmetry.

        Defined as sum(forward) / sum(backward)
        """
        self.alpha = self.instrument.data[self.group_1].sum() / self.instrument.data[self.group_2].sum()
        return self.alpha

    def get_asymmetry(self, alpha: float = None) -> pd.DataFrame:
        """Calculates the asymmetry between the two groups.

        Defined as (forward - alpha * backward) / (forward + alpha * backward)

        :param alpha: The balance parameter used in the calculation. By default, it is estimated using get_alpha method.
        """
        if alpha is None:
            alpha = self.get_alpha()
        self.asymmetry = pd.DataFrame([0 if x == y == 0 else (x - alpha * y) / (x + alpha * y) for x, y in
                                       zip(self.instrument.data[self.group_1], self.instrument.data[self.group_2])])
        return self.asymmetry
