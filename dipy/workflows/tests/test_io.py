import logging
import os
import numpy.testing as npt
import nibabel as nib
from dipy.data import get_fnames
from dipy.testing import assert_true
from dipy.data.fetcher import dipy_home
from dipy.workflows.io import IoInfoFlow, FetchFlow, SplitFlow
from nibabel.tmpdirs import TemporaryDirectory
from tempfile import mkstemp
fname_log = mkstemp()[1]

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(message)s',
                    filename=fname_log,
                    filemode='w')


def test_io_info():
    fimg, fbvals, fbvecs = get_fnames('small_101D')
    io_info_flow = IoInfoFlow()
    io_info_flow.run([fimg, fbvals, fbvecs])

    fimg, fbvals, fvecs = get_fnames('small_25')
    io_info_flow = IoInfoFlow()
    io_info_flow.run([fimg, fbvals, fvecs])

    io_info_flow = IoInfoFlow()
    io_info_flow.run([fimg, fbvals, fvecs], b0_threshold=20, bvecs_tol=0.001)

    file = open(fname_log, 'r')
    lines = file.readlines()
    try:
        npt.assert_equal(lines[-3], 'INFO Total number of unit bvectors 25\n')
    except IndexError:  # logging maybe disabled in IDE setting
        pass
    file.close()


def test_io_fetch():
    fetch_flow = FetchFlow()
    with TemporaryDirectory() as out_dir:

        fetch_flow.run(['bundle_fa_hcp'])
        npt.assert_equal(os.path.isdir(os.path.join(dipy_home,
                                                    'bundle_fa_hcp')),
                         True)

        fetch_flow.run(['bundle_fa_hcp'], out_dir=out_dir)
        npt.assert_equal(os.path.isdir(os.path.join(out_dir,
                                                    'bundle_fa_hcp')),
                         True)


def test_split_flow():
    with TemporaryDirectory() as out_dir:
        split_flow = SplitFlow()
        data_path, _, _ = get_fnames()
        vol_img = nib.load(data_path)
        volume = vol_img.get_data()
        split_flow.run(data_path, out_dir=out_dir)
        assert_true(os.path.isfile(
         split_flow.last_generated_outputs['out_split']))
        split_flow._force_overwrite = True
        split_flow.run(data_path, vol_idx=0, out_dir=out_dir)
        split_path = split_flow.last_generated_outputs['out_split']
        assert_true(os.path.isfile(split_path))
        split_img = nib.load(split_path)
        split_data = split_img.get_data()
        npt.assert_equal(split_data.shape, volume[..., 0].shape)
        npt.assert_array_almost_equal(split_img.affine, vol_img.affine)


if __name__ == '__main__':
    test_io_fetch()
    test_io_info()
    test_split_flow()
