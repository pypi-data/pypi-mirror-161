import tempfile
from pathlib import Path
import pydicom


def test_dicom_creation(dicom_module):

    out_dir = Path(tempfile.mkdtemp())

    # Generate DICOM files
    dicom_module.sample_image(out_dir)

    assert len(list(out_dir.glob('*.dcm'))) == dicom_module.num_vols

    for p in out_dir.glob('*.dcm'):
        pydicom.dcmread(p)  # Check dicom file can be read
