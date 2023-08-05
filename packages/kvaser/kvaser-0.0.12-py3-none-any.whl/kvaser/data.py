import pkg_resources
import pandas as pd


def getdata(dataset:str='d', list:bool=False):
    """Load example data from the 'kvaser' package

    Parameters
    ----------
    filename: str
       Name of the filename of the data
    list: bool

    Examples
    --------
    >>> # Surgical unit data
    >>> kvaser.getdata('surgunit').head()
       bloodclot  prognostic  enzyme  liver function  survival
    0        6.7          62      81            2.59       200
    1        5.1          59      66            1.70       101
    2        7.4          57      83            2.16       204
    3        6.5          73      41            2.01       101
    4        7.8          65     115            4.30       509
    >>> # Example data for risk-regression model
    >>> kvaser.getdata().head()
       y  a         x         z
    0  0  0 -0.626454  1.134965
    1  0  0  0.183643  1.111932
    2  0  0 -0.835629 -0.870778
    3  1  0  1.595281  0.210732
    4  1  1  0.329508  0.069396

    """
    if list:
        return(pkg_resources.resource_listdir('kvaser', 'data'))
    filename = 'data/' + dataset + '.csv.gz'
    inp = pkg_resources.resource_filename('kvaser', filename)
    data = pd.read_csv(inp, sep=',', header=0)
    return(data)
