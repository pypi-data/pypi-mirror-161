import sys
import os
import re
from itertools import count
import mmap
import h5py
import numpy as np


def is_hdf5(f_name):
    """Predicate, which checks whether file has HDF5 extension.

    Parameters
    ----------
    f_name : str
        Name of file.

    Returns
    -------
    bool
        True if file has HDF5 extension.
    """
    if f_name:
        ext = os.path.splitext(f_name)[-1]
        return ext in ['.h5', '.hdf5']
    else:
        return False


def store_data(data_array, f_output=None, groups=None, filters=None,
               append=False):
    """Helper function to store data in output file or print to stdout.

    Parameters
    ----------
    data_array : nested list of store objects
        2D array of data sources, rows along data inputs,
        columns along data items.
    f_output : str, default=None
        Output file, default is stdout.
    filters : list of dicts, optional
        List of filter dictionaries as passed to store.write(),
        one per data item.
    groups : list of str, optional
        List of output root directories, one per data input.
    append : bool, default=False
        If True, append output to existing database.

    Returns
    -------
    None
    """

    # set up default groups = output all to root directory
    groups = [None] * len(data_array) if groups is None else groups

    if len(groups) != len(data_array):
        sys.exit("Error: Number of groups has to match number of inputs")

    if is_hdf5(f_output):
        f = h5py.File(f_output, 'r+' if append else 'w')
    elif f_output and f_output != '-':
        f = open(f_output, 'a' if append else 'w')
    else:
        f = sys.stdout

    for grp, data_list in zip(groups, data_array):

        # set up default filters = keep all
        filters = [None] * len(data_list) if filters is None else filters

        if len(filters) != len(data_list):
            sys.exit("Error: Number of filters has to match number of items")

        for fltr, data in zip(filters, data_list):
            data.write(f, fltr=fltr, root=grp)

    if f_output and f_output != '-':
        f.close()


class keep_all:
    """Filter object represented by the identity. Wraps labels of occurrence
    labelled data into tuple.

    Attributes
    ----------
    label : str or tuple
        Label of the Store object to be filtered.

    Parameters
    ----------
    label : str or tuple
        Label of the Store object to be filtered.
    """
    def __init__(self, label):
        self.label = label

    def __getitem__(self, elem):
        if self.label == "occurrence":
            return (elem,)
        else:
            return elem


class Store:
    """Base class for the storage interface for real valued data.

    Parameters
    ----------
    title : str
        Title of the dataset.
    description : str
        Description of the dataset.
    label : list of str
        Description of label items.
    units : str
        Units of data.
    fmt : str or list of str
        Global format string of data or list of format string per column.

    Attributes
    ----------
    title : str
        Title of the dataset.
    meta : dict
        Metadata, with members: description, label, units.
    fmt : str or list of str
        Global format string of data or list of format string per column.
    """
    def __init__(self, title, description, label=None, units=None, fmt=None):

        self.title = title

        self.meta = {
            'description': description,
            'label': label,
            'units': units
        }

        self.fmt = fmt

    def __iter__(self):
        """Iterator which iterates over all data items, to be overwritten by
        child class.

        Parameters
        ----------
        None

        Yields
        ------
        tuple
            Pair of label and data.
        """
        pass

    def __getitem__(self, key):
        """Access data by label.

        Parameters
        ----------
        key : tuple
            Tuple containing the label items.

        Returns
        -------
        np.array
            Numpy array containing the data.
        """
        for label, data in iter(self):
            if label == key:
                return data

        raise KeyError()

    def format_label(self, label=None, counter=None, **kwargs):
        """Standard label formatter

        Parameters
        ----------
        label : iterable
            Iterable containing label items.
        counter : itertools count object
            Count object counting the current occurrence.

        Returns
        -------
        tuple
            Tuple of label items.
        """""
        if label is None:
            if counter is None:
                return ()
            else:
                return next(counter)
        else:
            return tuple(label)

    def format_data(self, data, **kwargs):
        """Standard data formatter for real valued data.

        Parameters
        ----------
        data : array
            Data array.

        Returns
        -------
        np.array
            Numpy array containing formatted data.
        """
        return np.array(data, dtype=float)

    def filter_items(self, fltr=None):
        """Filter items based on filter dictionary.

        Parameters
        ----------
        fltr : dict, default=None
            Dictionary containing the items to be kept as keys and their
            destination as values.

        Returns
        -------
        iterator
            Iterator over filtered items.
        """
        fltr = fltr or keep_all(self.meta['label'])

        if isinstance(fltr, keep_all):
            it = ((fltr[key], val) for key, val in iter(self))
        else:
            it = ((fltr[key], val) for key, val in iter(self)
                  if key in fltr.keys())

        return it

    def write(self, file, fltr=None, root=None):
        """Write all data to HDF5 database or plain text file

        Parameters
        ----------
        file : file descriptor
            HDF5 or plain text file object pointing to the output file.
        fltr : dict, optional
            Filter dictionary containing {src: dest} entries to select only
            Specific data "src" for output to "dest".
        root : str, optional
            Root output data directory.

        Returns
        -------
        None
        """
        it = self.filter_items(fltr)

        for label, data in it:
            if isinstance(file, h5py._hl.files.File):
                self.write_h5(file, label, data, root_path=root or '/')
            else:
                self.write_txt(file, label, data)

    def write_txt(self, f, label, data):
        """Default plain text dataset writer.

        Parameters
        ----------
        f : text file object
            Output file object.
        label : tuple
            Tuple of data label items.
        data : np.array
            Numpy array containing data.

        Returns
        -------
        None
        """
        header = '\n'.join(
            ["{} ({})".format(self.title, '/'.join(map(str, label)))] +
            ["{}: {}".format(key, '/'.join(val))
                if key == 'label' and val != 'occurrence' else
             "{}: {}".format(key, val) for key, val in self.meta.items()]
        )

        # write data
        np.savetxt(f, data, fmt=self.fmt or '%.18e', header=header)

    def write_h5(self, h, label, data, root_path=''):
        """Default HDF5 dataset writer.

        Parameters
        ----------
        h : HDF5 file object
            HDF5 output file object.
        label : tuple
            Tuple of data label items.
        data : np.array
            Numpy array containing data.
        root_path : str, optional
            Path to the HDF5 root directory.

        Returns
        -------
        None
        """
        path = self.create_h5_path(h, label, root_path)
        h[path].create_dataset(self.title, data=data).attrs.update(**self.meta)

    def create_h5_path(self, h, group, root_path=''):
        """Create HDF5 group directories and decorate with description of
        label items.

        Parameters
        ----------
        h : file object
            HDF5 file object.
        group : list
            List of group label hierarchie.
        root_path : str, optional
            Root directory of hierarchie.

        Returns
        -------
        str
            Group path.
        """
        try:
            root = h[root_path]
        except KeyError:
            h.create_group(root_path)
            root = h[root_path]

        grp_path = ""

        for idx, lab in enumerate(self.meta['label'], start=1):
            grp_path = '/'.join([str(grp) for grp in group[:idx]])
            try:
                root.create_group(grp_path).attrs["description"] = lab
            except ValueError:
                pass

        return '/'.join([root_path, grp_path])


class StoreType:
    """Mixin for Store class to add datatype specific members.
    """
    title: str
    meta: dict
    fmt: list

    create_h5_path: str


class Int(StoreType):
    """Storage mixin for integer valued data.
    """
    def format_data(self, data, **kwargs):
        return np.array(data, dtype=int)


class Cmplx(StoreType):
    """Storage mixin for complex valued data.
    """
    def format_data(self, real, imag, **kwargs):
        return np.array(real, dtype=float) + 1.j * np.array(imag, dtype=float)


class PlainTextExtractor(Store):
    """Plain text extractor class.

    Parameters
    ----------
    txt_file : str
        Name of extractor input.
    *args
        Arguments to be passed on to parent constructor.
    **kwargs
        Keyword arguments to be passed on to parent constructor.

    Attributes
    ----------
    txt_file : str
        Name of extractor input.
    """
    def __init__(self, txt_file, *args, **kwargs):
        self.txt_file = txt_file
        super().__init__(*args, **kwargs)

    def __iter__(self):
        # to be implemented by the child class
        pass


class RegexExtractor(PlainTextExtractor):
    """Regex extractor class.

    Parameters
    ----------
    *args
        Arguments to be passed on to parent constructor.
    **kwargs
        Keyword arguments to be passed on to parent constructor.

    Attributes
    ----------
    row_pattern : str
        Regular expression matching a single row of data. Has to contain one
        capture group per data atom.
    sec_pattern : str
        Regular expression matching the whole data section.
    """
    def __init__(self, *args, **kwargs):
        # to be implemented by child class
        self.row_pattern = None
        self.sec_pattern = None
        super().__init__(*args, **kwargs)

    def __iter__(self):

        counter = count(1)

        with open(self.txt_file, 'r+b') as f:
            # use mmap to buffer file contents
            # as a result, search pattern has to be encoded to byte string
            content = mmap.mmap(f.fileno(), 0)
            it = re.finditer(self.sec_pattern.encode(), content)

        for m in it:
            # get dictionary of matches
            named = m.groupdict()
            # format data
            try:  # check for data array
                data = self.format_data(
                    re.findall(self.row_pattern.encode(), named["array"]),
                    **named
                )

            except KeyError:  # in case of single line of data
                data = self.format_data(None, **named)

            # generate label
            label = self.format_label(counter=counter, **named)

            yield (label, data)


class H5AttrExtractor(Store):
    """HDF5 attribute extractor class.

    Parameters
    ----------
    h_file : str
        Name of extractor input.
    h_attr : str
        Name of attribute to extract.
    h_grps : list of str
        HDF5 group paths to extract data from.
    *args
        Arguments to be passed on to parent constructor.
    **kwargs
        Keyword arguments to be passed on to parent constructor.

    Attributes
    ----------
    h_file : str
        Name of extractor input.
    h_attr : str
        Name of attribute to extract.
    h_grps : list of str
        HDF5 group paths to extract data from.
    """
    def __init__(self, h_file, h_attr, h_grps, *args, **kwargs):
        self.h_file = h_file
        self.h_attr = h_attr
        self.h_grps = h_grps
        super().__init__(*args, **kwargs)

    def __iter__(self):
        with h5py.File(self.h_file, 'r') as h:
            for grp in self.h_grps:
                label = self.format_label(re.findall(r'\/(\w+)', '/'))
                data = self.format_data(h[grp].attrs.get(self.h_attr))
                yield (label, data)


class H5Extractor(Store):
    """HDF5 dataset extractor class.

    Parameters
    ----------
    h_file : str
        Name of extractor input.
    h_dset : str
        Name of dataset to extract.
    h_grps : list of str
        HDF5 group paths to extract data from.
    *args
        Arguments to be passed on to parent constructor.
    **kwargs
        Keyword arguments to be passed on to parent constructor.

    Attributes
    ----------
    h_file : str
        Name of extractor input.
    h_dset : str
        Name of dataset to extract.
    h_grps : list of str
        HDF5 group paths to extract data from.
    """
    def __init__(self, h_file, h_dset, h_grps, *args, **kwargs):
        self.h_file = h_file
        self.h_dset = h_dset
        self.h_grps = h_grps
        super().__init__(*args, **kwargs)

    def __iter__(self):
        with h5py.File(self.h_file, 'r') as h:
            for grp in self.h_grps:
                label = self.format_label(re.findall(r'\/(\w+)', '/'))
                data = self.format_data(h[grp][self.h_dset][...])
                yield (label, data)
