.. image:: https://github.com/timcera/plottoolbox/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/timcera/plottoolbox/actions/workflows/python-package.yml
    :height: 20

.. image:: https://coveralls.io/repos/timcera/plottoolbox/badge.png?branch=master
    :target: https://coveralls.io/r/timcera/plottoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/plottoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/plottoolbox

.. image:: http://img.shields.io/badge/license-BSD-lightgrey.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/plottoolbox/

.. image:: http://img.shields.io/pypi/dd/plottoolbox.svg
    :alt: plottoolbox downloads
    :target: https://pypi.python.org/pypi/plottoolbox/

plottoolbox - Quick Guide
=========================
The plottoolbox is a Python script to manipulate time-series on the command line
or by function calls within Python.  Uses pandas (http://pandas.pydata.org/)
or numpy (http://numpy.scipy.org) for any heavy lifting.

Requirements
------------
* pandas - on Windows this is part scientific Python distributions like
  Python(x,y), Anaconda, or Enthought.

* mando - command line parser

Installation
------------
Should be as easy as running ``pip install plottoolbox`` or ``easy_install
plottoolbox`` at any command line.  Not sure on Windows whether this will bring
in pandas, but as mentioned above, if you start with scientific Python
distribution then you shouldn't have a problem.

Usage - Command Line
--------------------
Just run 'plottoolbox --help' to get a list of subcommands::

    usage: plottoolbox [-h]
                       {autocorrelation, bar, bar_stacked, barh, barh_stacked,
                       bootstrap, boxplot, double_mass, heatmap, histogram,
                       kde, kde_time, lag_plot, lognorm_xaxis, lognorm_yaxis,
                       norm_xaxis, norm_yaxis, probability_density,
                       scatter_matrix, target, taylor, time, weibull_xaxis,
                       weibull_yaxis, xy, about} ...

    positional arguments:
      {autocorrelation, bar, bar_stacked, barh, barh_stacked, bootstrap,
      boxplot, double_mass, heatmap, histogram, kde, kde_time, lag_plot,
      lognorm_xaxis, lognorm_yaxis, norm_xaxis, norm_yaxis,
      probability_density, scatter_matrix, target, taylor, time, weibull_xaxis,
      weibull_yaxis, xy, about}

    autocorrelation
        Autocorrelation plot.
    bar
        Bar plot, sometimes called a "column" plot.
    bar_stacked
        Stacked vertical bar, sometimes called a stacked column plot.
    barh
        Bar plot, sometimes called a "column" plot.
    barh_stacked
        Horizontal stacked bar plot.
    bootstrap
        Bootstrap plot randomly selects a subset of the imput time-series.
    boxplot
        Box and whiskers plot.
    double_mass
        Double mass curve - cumulative sum of x against cumulative sum of y.
    heatmap
        2D heatmap of daily data.
    histogram
        Histogram.
    kde
        Kernel density estimation of probability density function.
    kde_time
        A time-series plot with a kernel density estimation (KDE) plot.
    lag_plot
        Lag plot.
    lognorm_xaxis
        Log-normal x-axis.
    lognorm_yaxis
        Log-normal y-axis.
    norm_xaxis
        Normal x-axis.
    norm_yaxis
        Normal y-axis.
    probability_density
        Probability plot.
    scatter_matrix
        Plots all columns against each other in matrix of plots.
    target
        Creates a "target" diagram to plot goodness of fit.
    taylor
        Taylor diagram to plot goodness of fit.
    time
        Time-series plot.
    weibull_xaxis
        Weibull x-axis.
    weibull_yaxis
        Weibull y-axis.
    xy
        Creates an 'x,y' plot, also known as a scatter plot.
    about
        Display version number and system information.

    optional arguments:
      -h, --help            show this help message and exit

The default for all of the subcommands is to accept data from stdin (typically
a pipe).  If a subcommand accepts an input file for an argument, you can use
"--input_ts=input_file_name.csv", or to explicitly specify from stdin (the
default) "--input_ts='-'".

For the subcommands that output data it is printed to the screen and you can
then redirect to a file.

Usage - API
-----------
You can use all of the command line subcommands as functions.  The function
signature is identical to the command line subcommands.  The return is always
a PANDAS DataFrame.  Input can be a CSV or TAB separated file, or a PANDAS
DataFrame and is supplied to the function via the 'input_ts' keyword.

Simply import plottoolbox::

    from plottoolbox import plottoolbox

    # Then you could call the functions
    plt = plottoolbox.time(input_ts='tests/test_fill_01.csv')
