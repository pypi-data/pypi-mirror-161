import os
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def choose_geometry_for_space(space):
    if space.startswith('fsavg-'):
        return 'fsavg'
    if space.startswith('onavg-'):
        return 'on1031'
    raise ValueError(f'{space} not recognized.')


def get_cortical_mask(lr, space, mask_type=None):
    if mask_type is None or (isinstance(mask_type, bool) and mask_type):
        mask_type = choose_geometry_for_space(space)
    mask_fn = os.path.join(DATA_DIR, 'cortical_masks', space, mask_type, f'{lr}h.npy')
    mask = np.load(mask_fn)
    return mask


def standardize_mask_type(mask_type):
    if mask_type is None or not mask_type or mask_type in ['no', 'none']:
        return 'no-mask'
    if mask_type in ['on1031', 'fsavg', 'fsavg6', 'fsavg5']:
        return f'{mask_type}-mask'
    raise ValueError(f'Mask type "{mask_type}" not recognized.')


def get_parcellation(lr, space, kind='aparc.a2009s', return_extra=False):
    fn = os.path.join(DATA_DIR, kind, space, 'on1031', f'{lr}h_trimmed_parc.npy')
    parcellation = np.load(fn)
    if return_extra:
        npz = np.load(os.path.join(DATA_DIR, kind, 'meta.npz'))
        return parcellation, list(npz['names']), npz['colortable']
    return parcellation


def get_mapping_indices(
        lr, source_space, target_space, source_mask=None, target_mask=None):
    """The indices for mapping from source_space to target_space.

    Parameters
    ----------
    lr : {'l', 'r'}
        Whether the mapping is for the left ('l') or right ('r') hemisphere.
    source_space : str
        The name of the space to map from.
    target_space : str
        The name of the space to map to.
    source_mask : {str, bool}
        The cortical mask type for the ``source_space``.
    target_mask : {str, bool}
        The cortical mask type for the ``target_space``.

    Returns
    -------
    indices : ndarray
        The indices for mapping from source_space to target_space.
    """
    mask1 = standardize_mask_type(source_mask)
    mask2 = standardize_mask_type(target_mask)
    mapping_fn = os.path.join(DATA_DIR, 'mapping', 'nn-dijkstra-onavg',
        f'from_{source_space}', f'to_{target_space}', f'{lr}h_{mask1}_to_{mask2}.npy')
    indices = np.load(mapping_fn)
    return indices
