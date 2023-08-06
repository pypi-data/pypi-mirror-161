from pathlib import Path
import json
from collections import defaultdict
from argparse import ArgumentParser
import pydicom.dataset


def read_dicom(fpath: Path):
    """Reads a DICOM file and returns as dictionary stripped from large binary
    fields

    Parameters
    ----------
    path : Path
        File system path to dicom file

    Returns
    -------
    dict[str, Any]
        Dicom fields and their values. Binrary data fields and the length of
        the binary string they hold
    """
    dcm = pydicom.dcmread(str(fpath))
    js = dcm.to_json_dict()
    header = {k: v for k, v in js.items()
              if not v['vr'].startswith('O')}
    # Replace data byte string with its length, so it can be recreated with
    # dummy data when it is loaded
    data = {k: {'vr': v['vr'], 'BinaryLength': len(v['InlineBinary'])} 
            for k, v in js.items()
            if v['vr'].startswith('O')}
    return header, data


def generate_python_code(dpath: Path, image_type: str):
    """Return 

    Parameters
    ----------
    dpath : Path
        Path to the directory holding the DICOM files
    image_type : str
        Name of the image type, used to name the generator that derives the
        image

    Returns
    -------
    str
        Python code that generates a version of the imported image with
        dummy data.
    """
    collated_hdr = defaultdict(dict)
    collated_data = defaultdict(dict)
    num_vols = 0
    for i, fpath in enumerate(dpath.iterdir()):
        if fpath.name.startswith('.'):
            continue
        header, data = read_dicom(fpath)
        for k, v in header.items():
            collated_hdr[k][i] = v
        for k, v in data.items():            
            collated_data[k][i] = v
        num_vols += 1
    constant_hdr = {k: v[0] for k, v in collated_hdr.items()
                    if (len(v) == num_vols
                        and all(v[0] == x for x in v.values()))}
    varying_hdr = {k: v for k, v in collated_hdr.items()
                   if k not in constant_hdr}

    constant_hdr.update(ANONYMOUS_TAGS)
    
    return FILE_TEMPLATE.format(
        num_vols=num_vols,
        image_type=image_type,
        constant_hdr=json.dumps(constant_hdr, indent='    '),
        varying_hdr=json.dumps(varying_hdr),
        collated_data=json.dumps(collated_data))


FILE_TEMPLATE = """from medimages4tests.dicom.base import generate_dicom, default_dicom_dir


def sample_image(out_dir=default_dicom_dir(__file__)):
    return generate_dicom(out_dir, num_vols, constant_hdr,
                          collated_data, varying_hdr)


num_vols = {num_vols}


constant_hdr = {constant_hdr}


varying_hdr = {varying_hdr}


collated_data = {collated_data}


"""

ANONYMOUS_TAGS = {
    "00200010": {
        "vr": "SH",
        "Value": ["PROJECT_ID"]
    },
    "00104000": {
        "vr": "LT",
        "Value": ["Patient comments string"]
    },
    "00100020": {
        "vr": "LO",
        "Value": ["Session Label"]
    },
    "00100010": {
        "vr": "PN",
        "Value": [{"Alphabetic": "Session Identifier"}]
    },
    "00081048": {
        "vr": "PN",
        "Value": [{"Alphabetic": "Some Phenotype"}]
    },
    "00081030": {
        "vr": "LO",
        "Value": ["Researcher^Project"]
    },
    "00080081": {
        "vr": "ST",
        "Value": ["Address of said institute"]
    },
    "00080080": {
        "vr": "LO",
        "Value": ["An institute"]
    }}


if __name__ == '__main__':
    parser = ArgumentParser(description=(
        "Generates a module containing extracted metadata from a DICOM dataset"
        "in Python dictionaries so that a dummy DICOM dataset with similar "
        "header configuration can be generated in pytest fixtures"))
    parser.add_argument(
        'dicom_dir', help="The directory containing the source dicoms")
    parser.add_argument(
        'fixture_file',
        help="The file to save the extracted header information and byte data in")
    args = parser.parse_args()

    fpath = Path(args.fixture_file)

    with open(fpath, 'w') as f:
        f.write(generate_python_code(Path(args.dicom_dir),
                                     image_type=fpath.stem))
