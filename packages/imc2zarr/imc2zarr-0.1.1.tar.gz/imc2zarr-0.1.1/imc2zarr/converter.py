from pathlib import Path
from contextlib import closing
import json

import xarray as xr

from .imclib.imcraw import ImcRaw


class Imc2Zarr:

    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

    def convert(self):
        with closing(ImcRaw(self.input_dir)) as imc:
            # assign output filename based on IMC run timestamp
            input_name = self.input_dir.name
            if self.input_dir.is_file():
                input_name = input_name[: -len(self.input_dir.suffix)]
            self.output_fn = self.output_dir.joinpath(
                "{}_{}".format(input_name, imc.code)
            )
            # save acquisitions into Zarr
            self._convert2zarr(imc)
            # save raw met and snapshots
            self._save_auxiliary_data(imc)

    def _convert2zarr(self, imc: ImcRaw):
        ds = xr.Dataset()
        # set meta for root
        ds.attrs['meta'] = [json.loads(json.dumps(imc.meta_summary, default=str))]
        ds.attrs['raw_meta'] = imc.rawmeta
        ds.to_zarr(self.output_fn, mode='w')
        # loop over all acquisitions to read and store channel data
        for q in imc.acquisitions:
            data = imc.get_acquisition_data(q)
            nchannels, ny, nx = data.shape
            q_name = 'Q{}'.format(str(q.id).zfill(3))
            ds_q = xr.Dataset()
            arr = xr.DataArray(
                data,
                dims=('channel', 'y', 'x'),
                name='data',
                coords={
                    'channel': range(nchannels),
                    'y': range(ny),
                    'x': range(nx)
                },
            )
            arr.attrs['meta'] = [json.loads(json.dumps(q.meta_summary, default=str))]
            ds_q[q_name] = arr
            ds_q.attrs['meta'] = arr.attrs['meta']
            # append acquisition to existing dataset
            ds_q.to_zarr(self.output_fn, group=q_name, mode='a')

    def _save_auxiliary_data(self, imc: ImcRaw):
        # save raw meta as xml file
        imc.save_meta_xml(self.output_fn)
        # save snapshots
        snapshot_dir = self.output_fn.joinpath('snapshots')
        imc.save_snapshot_images(snapshot_dir)
