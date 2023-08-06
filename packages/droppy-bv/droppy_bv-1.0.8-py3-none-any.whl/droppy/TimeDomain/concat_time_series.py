import numpy as np
import pandas as pd

"""Routines to help with concatenation of time-series. Nothing rocket-science here...
"""

class ConcatTimeSeries(object) :
    def __init__(self, df_list, trim_0=0, trim_1=0 ) :
        """Concatenate time trace into a long one (index is offset).

        For instance, if you have two runs of 3hours, each starting at t=0,
        this would return the concatenated run, with index from 0 to 6 hours.

        Parameters
        ----------
        df_list : list
            List of dataframe
        trim_0 : float
            trim each times series (begining)
        trim_1 : float
            trim each times series (end)

        Example
        -------
        >>> time = np.arange(0, 10 , 0.1)
        >>> se0 = pd.DataFrame( index = time, data  = {"val" : np.cos(time * np.pi * 2 / 10) } )
        >>> se1 = pd.DataFrame( index = time, data  = {"val" : 2*np.cos(time * np.pi * 2 / 10) } )
        >>> ct = ConcatTimeSeries( [se0, se1], trim_0 = 0.0, trim_1 = 0.0)
        >>> se_concat = ct()

        """

        if trim_0 + trim_1 > 0. :
            self.df_list = [ df.loc[  df.index.values[0] + trim_0 : df.index.values[-1] - trim_1, :] for df in df_list ]
        else :
            self.df_list = df_list

        # Duration of each runs
        self._durations = np.array([ df.index[-1] - df.index[0] for df in self.df_list ])

        # Starting point of each runs
        self._t0 = np.array([ df.index[0] for df in self.df_list  ])

        # Time average step of each runs
        self._dx = self._durations / np.array( [len(df)-1 for df in self.df_list]  )

        # Offset applied to each time-series
        self._offset = (self._t0 - np.insert( np.cumsum( self._durations[:-1] + self._dx[:-1]  ), 0 , 0))

        # To handle both Series and DataFrame
        self._se = isinstance( self.df_list[0], pd.Series)

        self.new_index = np.concatenate( [ df.index.values - self._offset[i] for i, df in enumerate(self.df_list)] )
        self.new_data = np.concatenate( [df.values for df in self.df_list ])

    def __call__(self, original_index_as_columns = False):
        """Return the concatenated time series

        Parameters
        ----------
        original_index_as_columns : bool, optional
            If True, the original index is output as additional columns. The default is False.

        Returns
        -------
        pd.DataFrame
            The concatenated time-series
        """
        if self._se :
            return pd.Series( index = self.new_index, data = self.new_data)
        else :
            if original_index_as_columns :
                return pd.DataFrame( index = self.new_index, data = np.c_[ self.new_data , self.original_index()], columns = list(self.df_list[0].columns) + ["original_index"])
            else:
                return pd.DataFrame( index = self.new_index, data = self.new_data, columns = self.df_list[0].columns )


    def original_index(self) :
        return np.concatenate( [ df.index.values for df in self.df_list ] )


if __name__ == "__main__":

    time = np.arange(0, 10 , 0.1)

    se0 = pd.DataFrame( index = time, data  = {"val" : np.cos(time * np.pi * 2 / 10) } )
    se1 = pd.DataFrame( index = time, data  = {"val" : 2*np.cos(time * np.pi * 2 / 10) } )

    ct = ConcatTimeSeries( [se0, se1], trim_0 = 0.0, trim_1 = 0.0)

    se_concat = ct()
    se_concat.plot()


