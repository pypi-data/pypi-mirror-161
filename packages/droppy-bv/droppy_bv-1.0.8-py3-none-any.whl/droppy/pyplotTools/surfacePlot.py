
from matplotlib import pyplot as plt
import numpy as np

def mapFunction( x , y , func , ax = None, arrayInput = False, n = 10, colorbar = False, colorbar_label = False,  **kwargs ) :
    """Plot 2D function on a regular grid

    Parameters
    ----------
    x : 1d array
        Discrete value of X axis .
    y : 1d array
        Discrete value of Y axis .
    func : function
        Function to plot.
    ax : plt.Axes, optional
        Where to plot. The default is None.
    arrayInput : bool, optional
        Does the function work two arguments, or on tuple : False if func(x,y) , True if func( [x,y] ). The default is False.
    n : int, optional
        Number of colors. The default is 10.
    colorbar : bool, optional
        Add color bar if True. The default is False.
    colorbar_label : str, optional
        label of the color bar. The default is False.
    **kwargs : any
        Argument passed to plt.contourf().

    Returns
    -------
    ax : plt.Axes
        The graph

    Example
    -------
    >>> def func( x , y ) :
    >>>    return x**2-y**2
    >>>
    >>> x = np.linspace( 0.1 , 2.0 , 10)
    >>> y = np.linspace( 0.1 , 3.0 , 15)
    >>> mapFunction( x , y , func, n = 100, colorbar = True, colorbar_label = 'Density' )

    """

    if ax is None :
        fig , ax = plt.subplots()

    X , Y = np.meshgrid( x , y )

    if not arrayInput :
        Z = func( X.flatten() , Y.flatten() ).reshape(X.shape)
    else :
        Z = func( np.stack( [ X.flatten() , Y.flatten() ]) )

    cax = ax.contourf( X , Y , Z , n , **kwargs)

    if colorbar  :
        cbar = ax.get_figure().colorbar(cax)
        if colorbar_label is not False:
            cbar.set_label(colorbar_label)
    return ax


if __name__ == "__main__" :

    def func( x , y ) :
        return x**2-y**2

    x = np.linspace( 0.1 , 2.0 , 10)
    y = np.linspace( 0.1 , 3.0 , 15)
    mapFunction( x , y , func, n = 100, colorbar = True, colorbar_label = 'Density' )
