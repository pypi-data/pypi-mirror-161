from typing import List
import FlowMePy as fm
import numpy as np
import os
import pandas as pd
import json
import pkg_resources


class FmFcsMeta:

    def __init__(self, fcs):

        self.exp_name = fcs.cache_name()
        self.cytometer_name = fcs.cytometer_name()
        self.med_label = fcs.med_label()
        self.gate_marker_info = pd.DataFrame(fcs.gate_marker_info(), columns=[
                                             "gate_name", "parent_name", "x_axis_marker", "y_axis_marker"])
        # combine gate name & gate ploygons into one object --> order of gate_marker_info is the same as in gate_polygons
        self.gate_polygons = list(
            zip(self.gate_marker_info["gate_name"], fcs.gate_polygons()))


class FmFcsCache:
    """Caches data and gates from FCS files.
    """

    def __init__(self, filepath: str):
        """FCS cache.
        This class is designed to cache fcs data.
        In contrast to FmFcsLoader, it does not hold
        C++ classes and is therefore perfectly suited for 
        parallel processing.

        Arguments:
            filepath {str} -- absolute filepath to the fcs files.
        """

        self.filepath = filepath
        self.events = None
        self.gates = None
        self.autogate = None
        self.meta = None

    def load(self, autogate: bool = False):
        """Cache the FCS file.
        """

        with FmFcsLoader(self.filepath) as fcs:
            self.events = fcs.events()
            self.gates = fcs.gate_labels()
            self.meta = fcs.metadata()

            if autogate:
                self.autogate = fcs.auto_gate_labels()

        return self


class FmFcsLoader:
    """The FCS loader.
    The lazy loading allows for creating multiple instances
    without loosing resources. A more greedy - but convenient
    class would be FmFcsCache which directly loads samples and
    therefore allows parallel loading.
    """

    def __init__(self, filepath: str, trainpath: str = "", filter_gatename : str = ""):
        """A convenience class that eases the use of FlowMePy
        The constructor is leight-weight - hence loading is only
        performed if any member is called (i.e. events()).

        Arguments:
            filepath {str} -- the absolute file path
        """

        self._filepath = filepath
        self._train_path = trainpath
        self._filter_gatename = filter_gatename # the name of the gate used to filter events in FlowMe
        self._fcs = None         # the C++ fcs object
        self._events = None      # dataframe with all events
        self._gate = None        # bool matrix with gate information
        self._autogate = None    # bool matrix with auto gate information
        self._markerdict = None  # dictionary for standardizing markernames

        self._tube_index = 0


        if not self._train_path:

            self._train_path = pkg_resources.resource_filename(
                'FlowMePy', 'cloud/')

        if not os.path.exists(filepath):
            print("WARNING: %s does not exist" % filepath)

    def metadata(self):

        if self._fcs is None:
            self.load()

        return FmFcsMeta(self._fcs)

    def auto_gate_labels(self):

        if self._autogate is None:

            fcs = self.load()

            if fcs.auto_gate(self._train_path):
                labels = np.array(fcs.auto_gate_labels(), copy=True)
                names = fcs.auto_gate_names()

                # convert to data frame
                self._autogate = pd.DataFrame(
                    labels,
                    columns=names)
            else:
                self._autogate = pd.DataFrame()

        return self._autogate

    def set_tube_index(self, tube_idx: int):

        fcs = self.load()
        fcs.set_tube_index(tube_idx)
        
        if tube_idx != self._tube_index:
            self._tube_index = tube_idx
            self._events = None
            self._gate = None

    def get_tube_names(self) -> List[str]:

        fcs = self.load()
        return fcs.tube_names()

    def __enter__(self):

        self.load()

        # cache values
        self._events = self.events()
        self._gates = self.gate_labels()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.fcs = None

    def gate_labels(self):
        """Returns gate labels

        Returns:
            pandas.DataFrame -- Gate labels is a MxN data frame 
            with M ... # events and N ... # of gates.
        """

        if self._gate is None:

            fcs = self.load()

            labels = np.array(fcs.gate_labels(), copy=True)
            names = fcs.gate_names()

            # convert to data frame
            self._gate = pd.DataFrame(
                labels,
                columns=names)

        return self._gate

    def markerdict(self):
        if self._markerdict is None:
            # due to quick and dirty solution of data copying, we need to navigate out of flowme dir
            # to access configs
            stream = pkg_resources.resource_stream(__name__, '../configs/markerdict.json')
            #The input encoding should be UTF-8, UTF-16 or UTF-32.
            self._markerdict = json.loads(stream.read()) # get the dict

        return self._markerdict 

    def events(self):
        """Returns the tranformed events.
        This function reads events from an fcs file compensates 

        Returns:
            pandas.DataFrame -- events is a MxN data frame with 
            M ... # events and N ... # of dimensions (antibodies)
        """

        if self._events is None:

            # load an fcs & process events
            fcs = self.load()

            # make a deep copy of the events
            data = np.array(fcs.events(), copy=True)

            # convert to panda data frame
            self._events = pd.DataFrame(data,
                                        columns=fcs.antibodies())
            # apply marker dict and convert markers to standard names. 
            renamed_columns = [self.markerdict()[col] if col in self.markerdict() else col for col in self._events.columns]
            self._events.columns = renamed_columns
        return self._events

    def load(self):
        """Loads the FCS file.

        NOTE: this function typically does not need to be called explicitly.

        Raises:
            FileNotFoundError: if the provided file path does not exist.

        Returns:
            FlowMePy.fcs_file -- an FCS instance
        """

        if self._fcs is None:
            # file exists?
            if not os.path.exists(self._filepath):
                raise FileNotFoundError()

            # touch the file
            self._fcs = fm.fcs_file(self._filepath, self._filter_gatename)

        return self._fcs

    def label_exclusive(self, gatename: str, others: list):
        """Returns exclusive events of the current gates.

        This method creates disjunct event groups for all gates
        provided in the list.

        Arguments:
            gatename {str} -- the gatename for the group of interest
            others {list} -- events that should be removed from 'gatename'

        Returns:
            [type] -- boolean array with exclusively gated events w.r.t 'gatename'
        """
        labels = self.gate_labels().copy()
        cl = labels[gatename]

        for g in others:

            if g is not gatename:
                cl -= labels[g]

        return cl


def load_fcs_from_list(filepaths: list):
    """Parallel loading of multiple FCS files.
    Since FCS files use a lot of resources (RAM), you
    should not load more than 50 samples at once.

    Arguments:
        filepaths {list} -- absolute FCS file paths

    Returns:
        FmFcsCache {list} -- loaded FCS data
    """
    from multiprocessing import Pool, Queue

    fcs_files = [FmFcsCache(f) for f in filepaths]

    with Pool() as pool:
        fcs_files = pool.map(FmFcsCache.load, fcs_files)

    return fcs_files


if __name__ == "__main__":

    print("you are running version: " + fm.__version__)

    # for debugging
    fd = os.path.join(os.path.dirname(__file__),
                      '../../flowme/src/data/samples/FacsDiva.xml')
    fk = os.path.join(os.path.dirname(__file__),
                      '../../flowme/src/data/samples/Kaluza.analysis')

    fcs = FmFcsLoader(fk)
    ag = fcs.auto_gate_labels()

    print(ag)

    # fcs = FmFcsCache(fd)
    # fcs.load()

    # fcs = FmFcsLoader(fd)

    # events = fcs.events()
    # gates = fcs.gate_labels()

    # f = load_fcs_from_list([fd, fk])

    pass
