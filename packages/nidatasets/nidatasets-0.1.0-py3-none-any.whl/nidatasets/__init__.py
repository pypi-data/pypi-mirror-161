import os
from collections.abc import Iterable
import numpy as np
from scipy.stats import zscore
import datalad.api as dl

from surface_spaces import get_cortical_mask

DIR = os.path.dirname(os.path.realpath(__file__))
DATA_ROOT = os.path.join(DIR, 'data')


class Dataset(object):
    def __init__(self, name, space, flavor, dl_source, fp_version='21.0.2'):
        self.name = name
        self.fp_version = fp_version
        self.dl_source = dl_source
        self.dl_dset = dl.install(
            path=os.path.join(DIR, 'datalad', self.name),
            source=self.dl_source)
        self.space = space
        self.flavor = flavor

    def load_data(self, sid, task, run, lr, space, flavor):
        fn = os.path.join(f'{self.name}_{self.fp_version}', space, *flavor,
            f'{sid}_{task}_{run:02d}_{lr}h.npy')

        local_fn = os.path.join(DATA_ROOT, fn)
        if os.path.exists(local_fn):
            ds = np.load(local_fn)
        else:
            result = self.dl_dset.get(fn)[0]
            if result['status'] not in ['ok', 'notneeded']:
                raise ValueError(
                    f"datalad `get` status is {result['status']}, likely due to "
                    "problems downloading the file.")
            ds = np.load(result['path'])

        return ds

    def get_data(
            self, sid, task, run, lr, z=True, mask=False,
            space=None, flavor=None):

        if isinstance(run, Iterable):
            ds = [self.get_data(sid, task, run_, lr, z, mask, space, flavor)
                for run_ in run]
            ds = np.concatenate(ds, axis=0)
            return ds

        if space is None:
            space = self.space
        if flavor is None:
            flavor = self.flavor

        ds = self.load_data(sid, task, run, lr, space=space, flavor=flavor)

        if mask:
            m = get_cortical_mask(lr, space, mask)
            ds = ds[:, m]
        if z:
            ds = np.nan_to_num(zscore(ds, axis=0))

        return ds


class ForrestDataset(Dataset):
    def __init__(
            self, space='onavg-ico32',
            flavor=('2step_normals_equal', 'no-gsr'), fp_version='21.0.2'):

        super().__init__(
            name='forrest',
            space=space,
            flavor=flavor,
            dl_source='https://gin.g-node.org/feilong/nidata-forrest',
            fp_version=fp_version,
        )
        self.subjects = ['01', '02', '03', '04', '05', '06', '09', '10', '14', '15', '16', '17', '18', '19', '20']
        self.tasks = ["forrest", "movielocalizer", "objectcategories", "retmapccw", "retmapclw", "retmapcon", "retmapexp"]
