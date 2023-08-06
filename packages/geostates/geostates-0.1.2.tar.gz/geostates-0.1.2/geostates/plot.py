import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import geopandas as gpd
import pandas as pd
import math

from .utils import discrete_cmap

from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable


def plot_states(df, column=None, extra_regions=False, labels='postal', linestyle='solid', cmap='copper_r',
                legend=None, bins=10):
    """Plot a choropleth map of the United States.

    Parameters
    ----------

    df : dataframe
       The geodataframe including the column of the value to plot.

    column : str
       Name of the column for the value to plot

    extra_regions : bool, default=False
       Adds Guam and Puerto Rico to the plot.

    labels : string, default 'postal'
       Labels each of the regions on the plot. Options are 'postal',
       'values', and 'both'.
       Postal displays the two letter abbreviations for each of the
       regions on the plot.
       Values displays the numerical values for the target that are
       being plotted (these values are rounded to four decimal
       places).
       Both plots both the two letter abbreviations for each of the
       regions and the target values that are being plotted (these
       values are rounded to four decimal places).

    linestyle : string, default 'dashed'
       Line style to place around the inset plots. Options are
       'solid', 'dashed', and 'none'.

    cmap : str, default=None
       Specifies the matplotlib colormap to use.

    legend : bool, default=False
       Adds a legend object to the map.

    bins : int, default=10
       Specifies how many bins to group values into for a legend or
       discrete colorbar.

    Returns
    -------
    A choropleth plot of the United States.

    """

    # -------------------------------------GENERATE THE PLOT AND INSET PLOTS--------------------------------

    # create the plot figure

    # ax.inset_axes([right/left, up/down, width, height])
    fig, continental_states_ax = plt.subplots(figsize=(20, 10))

    # create an axis with two insets
    alaska_ax = continental_states_ax.inset_axes([.08, .012, .20, .28])
    hawaii_ax = continental_states_ax.inset_axes([.28, .014, .15, .19])

    # set the x and y limits for the continental United States plot
    continental_states_ax.set_xlim(-130, -64)
    continental_states_ax.set_ylim(22, 53)

    # set the x and y limits for the Alaska plot
    alaska_ax.set_xlim(-180, -127)
    alaska_ax.set_ylim(51, 72)

    # set the x and y limits for the Hawaii plot
    hawaii_ax.set_xlim(-160, -154.6)
    hawaii_ax.set_ylim(18.8, 22.5)

    # ----------------------------------------BEGIN SET PARAMETER VALUES--------------------------------

    # parameter for displaying extra regions or not
    if extra_regions == True:

        # create two inset plots for the extra regions
        puerto_rico_ax = continental_states_ax.inset_axes([.512, .03, .11, .11])
        guam_ax = continental_states_ax.inset_axes([.612, .03, .10, .15])

        # set the x and y limits for the Puerto Rico plot
        puerto_rico_ax.set_xlim(-67.4, -65.1)
        puerto_rico_ax.set_ylim(17.55, 18.9)

        # set the x and y limits for the Guam plot
        guam_ax.set_xlim(144.55, 145)
        guam_ax.set_ylim(13.2, 13.7)

        df.loc[['PR']].plot(ax=puerto_rico_ax, cmap=cmap)
        df.loc[['GU']].plot(ax=guam_ax, cmap=cmap)

        # set axis array
        axis_list_full = [alaska_ax, hawaii_ax, puerto_rico_ax, guam_ax, continental_states_ax]
        axis_list = [alaska_ax, hawaii_ax, puerto_rico_ax, guam_ax]

    else:

        # set axis array
        axis_list_full = [alaska_ax, hawaii_ax, continental_states_ax]
        axis_list = [alaska_ax, hawaii_ax]

    # ---------------------------------------------------------------------------------------------------

    # for loop to remove axis tick marks from graphs
    for axis in axis_list_full:
        axis.set_yticks([])
        axis.set_xticks([])

    # --------------------------------------CHANGE LINESTYLE--------------------------------------------

    # parameters for changing the linestyle of inset plots

    if linestyle == 'dashed':

        # for loop to change axis lines to dotted lines
        for axis in axis_list:

            for spine in ['right', 'left', 'top', 'bottom']:
                axis.spines[spine].set_linestyle('--')
                axis.spines[spine].set_color('grey')
                axis.spines[spine].set_alpha(.5)


    elif linestyle == 'solid':

        # for loop to change axis lines to solid lines
        for axis in axis_list:

            for spine in ['right', 'left', 'top', 'bottom']:
                axis.spines[spine].set_linestyle('-')
                axis.spines[spine].set_color('grey')
                axis.spines[spine].set_alpha(.5)


    elif linestyle == 'none':

        # for loop to change axis lines to remove lines
        for axis in axis_list:
            axis.set_axis_off()

    else:

        raise ValueError('Linestyle must be \'dashed\', \'solid\', or \'none\'')

    # ---------------------------------------ADD LABELS------------------------------------------------

    # -------PRIVATE METHODS-----

    # create a function to compute the x coordinate of the x centroid of a state
    def centroid_x(state_name):

        '''Computes the x value of the centroid of a State's polygon
        Parameters
        ----------
        state_name : the name of the state we would like to get the x centroid value of

        '''

        state = df.loc[state_name]
        centroid_x = round(state['geometry'].centroid.x, 4)
        return centroid_x

    # create a function to compute the y coordinate of the y centroid of a state
    def centroid_y(state_name):

        '''Computes the y value of the centroid of a State's polygon
        Parameters
        ----------
        state_name : the name of the state we would like to get the y centroid value of

        '''

        state = df.loc[state_name]
        centroid_y = round(state['geometry'].centroid.y, 4)
        return centroid_y

    # function for extracting value from dataframe and converting it into a string
    def get_value(df, column):

        '''Extracts the value being plotted and converts it into a string to be used
        as a label.
        Parameters
        ----------
        df : the dataframe input into the function
        column : the column input into the function

        '''

        value = df.loc[column]
        value_s = str(value)
        return value_s

    # function for extracting a specific state from the dataframe
    def state_df(state):

        '''Extracts and individual state from the dataframe.
        Parameters
        ----------
        state : the state to extract from the dataframe

        '''

        state_df = df.loc[state]
        return state_df

    # ----------------------------

    # for loop to add state label annotations to the continental plot

    # for loop for labeling states where centroid values provide good locations for annotations

    if labels == 'postal':

        # define the states to label
        rows = df.index.drop(['AK', 'HI', 'PR', 'GU', 'RI', 'DC', 'DE', 'FL', 'MI', 'LA', 'CA', 'MD', 'NJ', 'MA'])

        # create a for loop to label all of the states in the list rows
        for row in rows:
            test = df.loc[row]

            continental_states_ax.annotate(test.name, xy=(centroid_x(row), centroid_y(row)), color='white',
                                           ha='center', va='center')

        # custom state labels for states in which using polygon centroids does not provide a good center for labels

        # state label annotation for Florida
        continental_states_ax.annotate('FL', xy=(centroid_x('FL') + .75, centroid_y('FL')), color='white',
                                       ha='center', va='center')

        # state label annotation for Michigan
        continental_states_ax.annotate('MI', xy=(centroid_x('MI') + .58, centroid_y('MI') - .85), color='white',
                                       ha='center', va='center')

        # state label annotation for Louisiana
        continental_states_ax.annotate('LA', xy=(centroid_x('LA') - .5, centroid_y('LA')), color='white',
                                       ha='center', va='center')

        # state label annotation for California
        continental_states_ax.annotate('CA', xy=(centroid_x('CA') - .4, centroid_y('CA')), color='white',
                                       ha='center', va='center')

        # state label annotation for Massachusetts
        continental_states_ax.annotate('MA', xy=(centroid_x('MA'), centroid_y('MA') + .075), color='white',
                                       ha='center', va='center')

        # state labels for inset plots

        # state label annotation for Alaska inset plots
        alaska_ax.annotate('AK', xy=(centroid_x('AK'), centroid_y('AK')), color='white', ha='center', va='center')

        # state label annotation for Hawaii inset plot
        hawaii_ax.annotate('HI', xy=(-155.52, 19.61), color='white', ha='center', va='center')

        # state labels for New England states

        # create the label for Rhode Island
        continental_states_ax.annotate('RI', ha='center', xy=(centroid_x('RI'), centroid_y('RI')), xycoords='data',
                                       xytext=(-70, 40.5), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-25, armB=0, rad=0"))

        # create the label for New Jersey
        continental_states_ax.annotate('NJ', ha='center', xy=(centroid_x('NJ'), centroid_y('NJ')), xycoords='data',
                                       xytext=(-72.75, 39.4), textcoords='data', arrowprops=dict(arrowstyle='-'))

        # create the label for Delaware
        continental_states_ax.annotate('DE', ha='center', xy=(centroid_x('DE'), centroid_y('DE')), xycoords='data',
                                       xytext=(-73.50, 38.25), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=0, armB=0, rad=0"))

        # create the label for DC
        continental_states_ax.annotate('DC', ha='center', xy=(centroid_x('DC'), centroid_y('DC')), xycoords='data',
                                       xytext=(-74.2, 36.5), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=0, rad=0"))

        # create the label for Maryland
        continental_states_ax.annotate('MD', xy=(centroid_x('MD'), centroid_y('MD')), xycoords='data',
                                       xytext=(-74.4, 37.35), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=0, rad=0"))

        # state labels for extra region inset plots
        if extra_regions == True:
            # state label annotation for Puerto Rico inset plot
            puerto_rico_ax.annotate('PR', xy=(centroid_x('PR'), centroid_y('PR')), color='white', ha='center',
                                    va='center')

            # state label annotation for Guam inset plot
            guam_ax.annotate('GU', xy=(144.715, 13.355), color='white', ha='center', va='center')



    elif labels == 'both':

        rows = df.index.drop(['AK', 'HI', 'PR', 'GU', 'RI', 'DC', 'DE', 'FL', 'MI', 'LA', 'CA', 'MD', 'NJ', 'MA',
                              'CT'])

        for row in rows:
            test = df.loc[row]

            continental_states_ax.annotate(test.name + '\n' + get_value(test, column), xy=(centroid_x(row),
                                                                                           centroid_y(row)),
                                           color='white', ha='center', va='center')

        # custom state labels for states in which using polygon centroids does not provide a good center for labels

        # state label annotation for Florida
        continental_states_ax.annotate('FL' + '\n' + get_value(state_df('FL'), column), xy=(centroid_x('FL') + .75,
                                                                                            centroid_y('FL')),
                                       color='white', ha='center', va='center')

        # state label annotation for Michigan
        continental_states_ax.annotate('MI' + '\n' + get_value(state_df('MI'), column), xy=(centroid_x('MI') + .58,
                                                                                            centroid_y('MI') - .85),
                                       color='white', ha='center', va='center')

        # state label annotation for Louisiana
        continental_states_ax.annotate('LA' + '\n' + get_value(state_df('LA'), column), xy=(centroid_x('LA') - .5,
                                                                                            centroid_y('LA')),
                                       color='white', ha='center', va='center')

        # state label annotation for California
        continental_states_ax.annotate('CA' + '\n' + get_value(state_df('CA'), column), xy=(centroid_x('CA') - .4,
                                                                                            centroid_y('CA')),
                                       color='white', ha='center', va='center')

        # state labels for inset plots

        # state label annotation for Alaska inset plots
        alaska_ax.annotate('AK' + '\n' + get_value(state_df('AK'), column), xy=(centroid_x('AK'), centroid_y('AK')),
                           color='white', ha='center', va='center')

        # state label annotation for Hawaii inset plot
        # xy=(centroid_x('HI'), centroid_y('HI')
        hawaii_ax.annotate('HI' + '\n' + get_value(state_df('HI'), column), xy=(-155.55, 19.62),
                           color='white', ha='center', va='center')

        # state labels for New England states

        # create the label for Rhode Island
        continental_states_ax.annotate('RI' + '\n' + get_value(state_df('RI'), column), ha='center',
                                       xy=(centroid_x('RI'), centroid_y('RI')), xycoords='data',
                                       xytext=(-69.25, 40.25), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-32, armB=0, rad=0"))

        # create the label for Massachusetts
        continental_states_ax.annotate('MA' + '\n' + get_value(state_df('MA'), column), ha='center',
                                       xy=(centroid_x('MA'), centroid_y('MA')), xycoords='data',
                                       xytext=(-69, 42.5), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=30, rad=0"))

        # create the label for Connecticut
        continental_states_ax.annotate('CT' + '\n' + get_value(state_df('CT'), column), ha='center',
                                       xy=(centroid_x('CT'), centroid_y('CT')), xycoords='data',
                                       xytext=(-70.50, 39.25), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=0, rad=0"))

        # create the label for New Jersey
        continental_states_ax.annotate('NJ' + '\n' + get_value(state_df('NJ'), column), ha='center',
                                       xy=(centroid_x('NJ'), centroid_y('NJ')), xycoords='data',
                                       xytext=(-72.75, 39.25), textcoords='data', arrowprops=dict(arrowstyle='-'))

        # create the label for Delaware
        continental_states_ax.annotate('DE' + '\n' + get_value(state_df('DE'), column), ha='center',
                                       xy=(centroid_x('DE'), centroid_y('DE')), xycoords='data',
                                       xytext=(-73.50, 38), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=0, armB=0, rad=0"))

        # create the label for DC
        continental_states_ax.annotate('DC' + '\n' + get_value(state_df('DC'), column), ha='center',
                                       xy=(centroid_x('DC'), centroid_y('DC')), xycoords='data',
                                       xytext=(-74, 36), textcoords='data', arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=0, rad=0"))

        # create the label for Maryland
        continental_states_ax.annotate('MD' + '\n' + get_value(state_df('MD'), column), xy=(centroid_x('MD'),
                                                                                            centroid_y('MD')),
                                       xycoords='data', xytext=(-73, 37), textcoords='data',
                                       arrowprops=dict(arrowstyle='-',
                                       connectionstyle="arc, angleA=0, angleB=0, armA=-30, armB=0, rad=0"))

        # state labels for extra region inset plots
        if extra_regions == True:
            # state label annotation for Puerto Rico inset plot
            puerto_rico_ax.annotate('PR' + '\n' + get_value(state_df('PR'), column), xy=(centroid_x('PR'),
                                                                                         centroid_y('PR')),
                                    color='white', ha='center', va='center')

            # state label annotation for Guam inset plot
            guam_ax.annotate('GU' + '\n' + get_value(state_df('GU'), column), xy=(144.715, 13.355), color='white',
                             ha='center', va='center')

    else:

        raise ValueError('Labels must be \'postal\', \'values\', or \'both\'')

    # -------------------------------------------ADD LEGEND--------------------------------------------

    # calulate the min and max value for the plot
    vmin, vmax = df[column].agg(['min', 'max'])

    if legend == 'legend':

        # create a normal legend

        # discretize the colormap
        cmap = discrete_cmap(bins, base_cmap=cmap)

        # calculate the boundaries for the range of values plotted
        bounds = np.linspace(vmin, vmax, cmap.N + 1)

        # create the handels to map the range of values to a discrete colormap
        handles = [Line2D([], [], color=cmap(i / (cmap.N - 1)), marker='s', markersize=10, ls='',
                          label=f'{bounds[i]:.0f} - {bounds[i + 1]:.0f}  ') for i in range(cmap.N)]

        # add a legend object to the plot
        # borderpad=.75, title=str(column) + ' by State'
        continental_states_ax.legend(handles=handles[::-1], loc=(.87, .06), borderpad=.6)

    elif legend == 'colorbar':

        # create a colorbar

        # discretize the colormap
        cmap = discrete_cmap(bins, base_cmap=cmap)

        # calculate the boundaries for the range of values plotted
        bounds = np.linspace(vmin, vmax, cmap.N + 1)

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

        # create an inset axis for placing the colorbar inside of the figure
        colorbar_ax = continental_states_ax.inset_axes([.93, .03, .014, .5])

        # remove the x and y ticks for the inset axis
        colorbar_ax.set_yticks([])
        colorbar_ax.set_xticks([])

        # add the colorbar to the figure
        cbar = plt.colorbar(ScalarMappable(cmap=cmap, norm=norm), cax=colorbar_ax, ticks=bounds, shrink=.5,
                            pad=-.05)

    # ----------------------PLOT THE FIGURE ONCE ALL THE PARAMETER VALUES ARE SPECIFIED----------------

    # plot the continental United States
    df.drop(index=['AK', 'HI', 'PR']).plot(column=column, cmap=cmap, ax=continental_states_ax, edgecolor='white')

    # plot the inset plots
    df.loc[['AK']].plot(column=column, cmap=cmap, ax=alaska_ax)
    df.loc[['HI']].plot(column=column, cmap=cmap, ax=hawaii_ax)

    # return the plot figure
    plt.show()
    return continental_states_ax


