from tal.io.capture_data import NLOSCaptureData
from tal.constants import SPEED_OF_LIGHT
from typing import Union
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def xy_at_different_t(data: Union[NLOSCaptureData, NLOSCaptureData.HType],
        size_x: int = 8, size_y: int = 8,
        t_start: int = None, t_end: int = None, t_step :int = 1):
    t_to_time = lambda t: f'Bin #{t_start + t * t_step}'
    if isinstance(data, NLOSCaptureData):
        assert data.H_format == NLOSCaptureData.HFormat.T_Sx_Sy, \
            'xy_at_different_t does not suppoort this data format'
        txy = data.H
        if data.t_start is not None and data.delta_t is not None:
            t_to_time = lambda t: f'Bin #{t_start + t * t_step}, {(data.t_start + t * data.delta_t) * 1e12 / SPEED_OF_LIGHT} ps'
    else:
        assert data.ndim == 3 and data.shape[1] == data.shape[2], \
            'xy_at_different_t does not suppoort this data format'
        txy = data
    txy = txy[t_start:t_end:t_step, ...]
    nx, ny, nt = data.shape    
    step = 1
    plot_size = size_x * size_y
    while nt // step > plot_size:
        step *= 2
    data_min, data_max = np.min(data), np.max(data)
    fig, axs = plt.subplots(size_x + 1, size_y, figsize=(24, 24))

    for i in tqdm(range(plot_size)):
        t_bin = i * step
        image = txy[t_bin]
        row = i // size_y
        col = i % size_y
        mappable = axs[row, col].imshow(image.astype(np.float32), cmap='jet', vmin=data_min, vmax=data_max)
        fig.colorbar(mappable, ax=axs[row, col])
        axs[row, col].axis('off')
        axs[row, col].set_title(t_to_time(t_start + t_bin * t_step), fontsize=24)

    plt.show()