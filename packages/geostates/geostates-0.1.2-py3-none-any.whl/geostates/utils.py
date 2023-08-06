import matplotlib as plt
import numpy as np

# function inspired by Jake VanderPlas' Python Data Science Handbook
def discrete_cmap(bins, base_cmap=None):
    '''Creates a N-bin discrete colormap from a continuous one.
    Parameters
    ----------
    bins : the number of bins to discretize the colorbar into
    base_cmap : the colormap to discretize

    '''

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, bins))
    cmap_name = base.name + str(bins)
    return base.from_list(cmap_name, color_list, bins)