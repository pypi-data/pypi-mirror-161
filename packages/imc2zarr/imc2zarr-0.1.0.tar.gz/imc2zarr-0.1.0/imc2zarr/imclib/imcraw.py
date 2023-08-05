import os
from pathlib import Path
import uuid
from collections import OrderedDict
from dateutil.parser import parse as dateparser

from .imcdataparser import ImcDataParser
from .mcdmeta import Slide, Panorama, AcquisitionRoi, Acquisition
from .metadefs import *

"""
    ImcRaw: holds metadata about raw IMC scan and all of its components 
"""


class ImcRaw:

    def __init__(self, input_dir, code=None):
        self.input_dir = input_dir
        self.code = code
        self.mcd_fn = None
        self.txt_fns = []  # text filenames
        # parse files
        self._find_files()
        self._parse_files()
        self._build_object_lists()
        self._assign_imc_meta_summary()

    def _assign_imc_meta_summary(self):
        # assign run timestamp from the first acquisition
        self.timestamp = dateparser(self.acquisitions[0].get_property(STARTTIMESTAMP))
        # assign code
        if not self.code:
            self.code = self.timestamp.strftime('%Y%m%d-%H%M%S-%f')
        self.rawmeta = self._parser.xml_str.replace("\n", "")
        self.mcd_sw_version = self.slides[0].get_property(SWVERSION)
        # set meta summary
        self.meta_summary = OrderedDict()
        self.meta_summary['description'] = self.slides[0].get_property(DESCRIPTION)
        self.meta_summary['n_acquisitions'] = len(self.acquisitions)
        self.meta_summary['mcd_sw_version'] = self.mcd_sw_version
        self.meta_summary['run_date'] = self.acquisitions[0].get_property(STARTTIMESTAMP)
        self.meta_summary['laser_power'] = self.acquisitions[0].get_property(ABLATIONPOWER)
        # fill structure info
        _acquisitions = []
        for q in self.acquisitions:
            q_name = 'Q{}'.format(str(q.id).zfill(3))
            _acquisitions.append(q_name)
        self.meta_summary['acquisitions'] = _acquisitions
        _panoramas = []
        for p in self.slides[0].panoramas:
            panorama = {'id': p.id,
                        SLIDEX1POSUM: p.get_property(SLIDEX1POSUM),
                        SLIDEX2POSUM: p.get_property(SLIDEX2POSUM),
                        SLIDEX3POSUM: p.get_property(SLIDEX3POSUM),
                        SLIDEX4POSUM: p.get_property(SLIDEX4POSUM),
                        SLIDEY1POSUM: p.get_property(SLIDEY1POSUM),
                        SLIDEY2POSUM: p.get_property(SLIDEY2POSUM),
                        SLIDEY3POSUM: p.get_property(SLIDEY3POSUM),
                        SLIDEY4POSUM: p.get_property(SLIDEY4POSUM),
                        PIXELSCALECOEF: p.get_property(PIXELSCALECOEF),
                        'acquisition_rois': []
                        }
            for r in p.acquisitionrois:
                acquisition_roi = {'id': r.id,
                                   'acquisitions': []}
                for q in r.acquisitions:
                    acquisition = {'id': q.id,
                                   'channels': []}
                    for c in q.channels:
                        # format: marker -> target
                        acquisition['channels'].append({
                            'metal': c.get_property(CHANNELNAME),
                            'target': c.get_property(CHANNELLABEL)})
                    acquisition_roi['acquisitions'].append(acquisition)
                panorama['acquisition_rois'].append(acquisition_roi)
            _panoramas.append(panorama)
        self.meta_summary['panoramas'] = _panoramas

    def _find_files(self):
        # check whether the input_dir points to an mcd file
        if self.input_dir.is_file():
            if self.input_dir.suffix != '.mcd':
                raise Exception('Input file does not seem to be a valid mcd file')
            self.mcd_fn = self.input_dir
        else:
            # check if mcd file exists
            files = list(self.input_dir.glob('*.mcd'))
            if not files:
                raise Exception('No mcd file was found in the input folder')
            elif len(files) > 1:
                raise Exception('More than one mcd files were found in the input folder')
            self.mcd_fn = files[0]
            # text files
            self.txt_fns = list(self.input_dir.glob('*.txt'))

    def _parse_files(self):
        try:
            self._parser = ImcDataParser(self.mcd_fn, textfilenames=self.txt_fns)
            self._parser.read_mcd_xml()
            self._parser.parse_mcd_xml()
        except Exception as e:
            raise Exception('Error parsing raw files: {}'.format(str(e)))

    def _build_object_lists(self):
        self.slides = list(self._parser.meta.objects[SLIDE].values())
        self.panoramas = list(self._parser.meta.objects[PANORAMA].values())
        self.acquisitions = list(self._parser.meta.objects[ACQUISITION].values())
        for s in self.slides:
            s.panoramas = list(s.childs[PANORAMA].values())
            for p in s.panoramas:
                if len(p.childs):
                    p.acquisitionrois = list(p.childs[ACQUISITIONROI].values())
                    for r in p.acquisitionrois:
                        r.roipoints = list(r.childs[ROIPOINT].values())
                        # sort RoiPoints by OrderNumber
                        r.roipoints.sort(key=lambda x: x.get_property(ORDERNUMBER))
                        r.acquisitions = list(r.childs[ACQUISITION].values())
                        # sort Acquisitions by OrderNumber
                        r.acquisitions.sort(key=lambda x: x.get_property(ORDERNUMBER))
                        for q in r.acquisitions:
                            q.channels = list(q.childs[ACQUISITIONCHANNEL].values())
                            # sort Channels by OrderNumber
                            q.channels.sort(key=lambda x: x.get_property(ORDERNUMBER))
                            self._assign_acquisition_meta_summary(q, r, p)

    def _assign_acquisition_meta_summary(self, q: Acquisition, r: AcquisitionRoi, p: Panorama):
        # meta from acquisition
        q.meta_summary['q_id'] = q.id
        q.meta_summary['q_num'] = q.get_property(ORDERNUMBER)
        q.meta_summary['q_timestamp'] = q.get_property(STARTTIMESTAMP)
        q.meta_summary['q_description'] = q.get_property(DESCRIPTION)
        q.meta_summary['q_maxx'] = q.maxx
        q.meta_summary['q_maxy'] = q.maxy
        q.meta_summary['q_stage_x'] = float(r.roipoints[0].get_property(SLIDEXPOSUM))
        q.meta_summary['q_stage_y'] = float(r.roipoints[0].get_property(SLIDEYPOSUM))
        q.meta_summary['q_laser_power'] = q.get_property(ABLATIONPOWER)
        q.meta_summary['q_resolution_xy'] = 1.0  # always 1 um
        q.meta_summary['q_n_channels'] = len(q.channels)
        channel_meta = []
        for c in q.channels:
            # format: marker -> target
            channel_meta.append({
                'metal': c.get_property(CHANNELNAME),
                'target': c.get_property(CHANNELLABEL)})
        q.meta_summary['q_channels'] = channel_meta
        # meta from panorama
        q.meta_summary['p_id'] = p.id
        # meta from acquisition_roi
        q.meta_summary['r_id'] = r.id

    def get_acquisition_data(self, q: Acquisition):
        return self._parser.get_acquisition_data(q)

    def close(self):
        self._parser.close()

    def save_snapshot_images(self, out_folder):
        out_folder.mkdir(parents=True, exist_ok=True)
        for s in self.slides:
            self._parser.save_snapshot_image(s, out_folder)
        for p in self.panoramas:
            self._parser.save_snapshot_image(p, out_folder)
        for q in self.acquisitions:
            self._parser.save_snapshot_image(q, out_folder)

    def save_meta_xml(self, out_folder):
        fn = "mcd_schema.xml"
        fn = out_folder.joinpath(fn)
        with open(fn, "w") as f:
            f.write(self.rawmeta)
