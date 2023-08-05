from collections import OrderedDict
import os
import csv

from .metadefs import *

"""
This module should help parsing the MCD xml metadata
"""
PARSER = "parser"
META_CSV = "_meta.csv"
"""
Definition of all the meta objects
Each entity will have a class corresponding to it, with helpermethods
that e.g. allow to retrieve images etc.

This is implemented as parent-child relationships where each entry has a list of parents
and a nested dictionary of children of the form (child_type: childID: childobject)

Further each object is registered in the global root node, making them easy accessible.
"""


class Meta(object):
    """
    Represents an abstract metadata object.
    """

    def __init__(self, mtype, meta, parents, symbol=None):
        """
        Initializes the metadata object, generates the
        parent-child relationships and updates to object list
        of the root

        :param mtype: the name of the object type
        :param meta: the metadata dictionary
        :param parents:  the parents of this object
        :param symbol: the short symbol for this metadata, e.g. 's' for slide

        """
        self.mtype = mtype
        self.id = meta.get(ID, None)
        # if self.id:
        #     self.id = int(self.id)
        self.childs = dict()
        self.symbol = symbol

        self.properties = meta
        self.parents = parents
        for p in parents:
            self._update_parents(p)

        if self.is_root:
            self.objects = dict()
        else:
            # update the root objects
            root = self.get_root()
            self._update_dict(root.objects)

    @property
    def is_root(self):
        return len(self.parents) == 0

    def _update_parents(self, p):
        self._update_dict(p.childs)

    def _update_dict(self, d):
        mtype = self.mtype
        mdict = d.get(mtype, None)
        if mdict is None:
            mdict = OrderedDict()
            d[mtype] = mdict
        mdict.update({self.id: self})

    def get_root(self):
        """
        Gets the root node of this metadata
        tree
        """
        if self.is_root:
            return self
        else:
            return self.parents[0].get_root()

    @property
    def metaname(self):
        pname = self.parents[0].metaname
        return "_".join([pname, self.symbol + self.id])

    def get_property(self, prop, default_val=None):
        if prop in self.properties:
            val = self.properties[prop]
        else:
            val = default_val
        return val


# Definition of the subclasses
class Slide(Meta):
    def __init__(self, meta, parents):
        Meta.__init__(self, SLIDE, meta, parents, "s")


class Panorama(Meta):
    def __init__(self, meta, parents):
        self.acquisitionrois = []
        Meta.__init__(self, PANORAMA, meta, parents, "p")


class AcquisitionRoi(Meta):
    def __init__(self, meta, parents):
        self.roipoints = []
        Meta.__init__(self, ACQUISITIONROI, meta, parents, "r")


class Acquisition(Meta):
    def __init__(self, meta, parents):
        self.meta_summary = OrderedDict()
        self.channels = []
        Meta.__init__(self, ACQUISITION, meta, parents, "a")

    def get_channels(self):
        return self.childs[ACQUISITIONCHANNEL]

    def get_channel_orderdict(self):
        chan_dic = self.get_channels()
        out_dic = dict()
        for k, chan in chan_dic.items():
            channel_name = chan.properties[CHANNELNAME]
            channel_label = chan.properties.get(CHANNELLABEL, channel_name)
            channel_order = int(chan.properties.get(ORDERNUMBER))
            out_dic.update({channel_order: (channel_name, channel_label)})
        return out_dic

    @property
    def data_offset_start(self):
        return int(self.properties[DATASTARTOFFSET])

    @property
    def data_offset_end(self):
        return int(self.properties[DATAENDOFFSET])

    @property
    def data_size(self):
        return self.data_offset_end - self.data_offset_start #+ 1

    @property
    def data_nrows(self):
        nrow = int(
            self.data_size / (self.n_channels * int(self.properties[VALUEBYTES]))
        )
        return nrow

    @property
    def maxx(self):
        return int(self.get_property(MAXX))

    @property
    def maxy(self):
        return int(self.get_property(MAXY))

    @property
    def n_channels(self):
        return len(self.get_channels())

    @property
    def value_bytes(self):
        return abs(int(self.properties[VALUEBYTES]))

    @property
    def expected_data_size(self):
        return self.n_channels * self.maxx * self.maxy * self.value_bytes

    @property
    def expected_data_nrows(self):
        nrow = int(
            self.expected_data_size / (self.n_channels * int(self.properties[VALUEBYTES]))
        )
        return nrow


class RoiPoint(Meta):
    def __init__(self, meta, parents):
        Meta.__init__(self, ROIPOINT, meta, parents, "rp")


class Channel(Meta):
    def __init__(self, meta, parents):
        Meta.__init__(self, ACQUISITIONCHANNEL, meta, parents, "c")


# A dictionary to map metadata keys to metadata types
# The order reflects the dependency structure of them and the
# order these objects should be initialized
OBJ_DICT = OrderedDict(
    [
        (SLIDE, Slide),
        (PANORAMA, Panorama),
        (ACQUISITIONROI, AcquisitionRoi),
        (ACQUISITION, Acquisition),
        (ROIPOINT, RoiPoint),
        (ACQUISITIONCHANNEL, Channel),
    ]
)

# A dictionary to map id keys to metadata keys
# Used for initializaiton of the objects
ID_DICT = {
    SLIDEID: SLIDE,
    PANORAMAID: PANORAMA,
    ACQUISITIONROIID: ACQUISITIONROI,
    ACQUISITIONID: ACQUISITION,
}