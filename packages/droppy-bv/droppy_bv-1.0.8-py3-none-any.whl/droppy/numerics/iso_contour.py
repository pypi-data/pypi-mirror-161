import numpy as np
from matplotlib import pyplot as plt
from matplotlib._contour import QuadContourGenerator
from droppy import pyplotTools as dplt

class ContourGenerator():
    """Compute iso contour of bivariate function f(x,y). Uses matplotlib engine.

    Useful when iso contour value are needed, but not the plot itself.

    Limited interest for plotting purpose (using directly plt.contourf is generally more straight forward)
    """

    def __init__(self, fun, x , y):
        """ContourGenerator initialisation

        Parameters
        ----------
        fun : function
            f(x,y) (vectorized)
        x : np.ndarray (1D)
            Range of x
        y : np.ndarray (1D)
            Range of y
        """

        self.x = x
        self.y = y
        self.m = np.meshgrid( x, y )
        self.z = fun( self.m[0].flatten() , self.m[1].flatten() ).reshape(len(y),len(x))
        self.qc = QuadContourGenerator( self.m[0], self.m[1] , self.z ,  None,  True,  0 )

    def __call__(self, value) :
        vertices, kinds = self.qc.create_contour( value )
        if len(vertices) == 0 :
            return [] , []
        else:
            x = np.concatenate( [ np.append( c[:,0] , np.nan) for c in vertices ] )
            y = np.concatenate( [ np.append( c[:,1]  , np.nan) for c in vertices ] )
        return x, y


    def contourf(self, ax = None, **kwargs) :
        """Wrapper to plt.contourf, with x, y, z already prepared
        """
        if ax is None :
            fig, ax = plt.subplots()
        return ax.contourf( self.x , self.y , self.z, **kwargs)

    def contour(self, ax = None, **kwargs) :
        """Wrapper to plt.contour, with x, y, z already prepared
        """
        if ax is None :
            fig, ax = plt.subplots()
        return ax.contour( self.x , self.y , self.z, **kwargs)


    def plot(self, values, ax = None, **kwargs):

        if ax is None :
            fig, ax = plt.subplots()

        c = dplt.getColorMappable( np.min(values), np.max(values))

        for v in values :
            x, y = self( v )
            ax.plot( x, y , "-", color = c.to_rgba(v), **kwargs )
        ax.set(xlim = [np.min(self.x), np.max(self.x) ], ylim = [ np.min(self.y) , np.max(self.y)])
        return ax
