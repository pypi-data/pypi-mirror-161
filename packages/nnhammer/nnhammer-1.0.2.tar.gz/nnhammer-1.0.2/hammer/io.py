import nibabel as nib
import numpy as np
import scipy.io


def load_mat(input_file, key='scene'):
    data = scipy.io.loadmat(input_file)[key]
    return data


def read_file(input_file):
    with open(input_file, "r") as input_file:
        return [each.strip("\n") for each in input_file.readlines()]


def write_list(path, data_lst):
    with open(path, 'w') as file:
        for i in range(len(data_lst)):
            file.write(data_lst[i])
            if i != len(data_lst) - 1:
                file.write('\n')


def save_nii(path, data):
    """
    Convert and save as nii.
    Note that nii format needs a shape of WHD
    :param path:
    :param data: ndarray image
    """
    # [-1, -1, 1, 1] for RAI, default is LPI
    nii_file = nib.Nifti1Image(data, np.diag((-1, -1, 1, 1)))
    nib.save(nii_file, path)


def load_nii(input_file):
    data = nib.load(input_file)
    return data.get_fdata()


def save_mat(path, data, key="scene"):
    scipy.io.savemat(path, {key: data})
