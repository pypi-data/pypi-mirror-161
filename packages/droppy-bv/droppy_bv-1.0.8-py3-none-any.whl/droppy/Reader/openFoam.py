import os
import numpy as np
import pandas as pd


def openFoamReader(filename, *args, **kwargs):
    """ Automatic reader for OpenFoam and foamStar postProecesses files. 
    
    For common file names, detect the appropriate reader for the file based on its name. 
    Forces, moments, and body motion are implemented. 

    Returns
    -------
    data: pd.DataFrame
        a data frame which index is the time.
        Column names are either automatically determined by the header
        (foamStar postProcesses) or hard coded by the reader (OpenFoam postProcesses)
    """
    dicoReader = {
        "motions.dat": openFoamReadMotion,
        "sixDofDomainBody.dat": openFoamReadMotion,
        "surfaceElevation.dat": openFoamReadMotion,
        "fx.dat": openFoamReadMotion,
        "fy.dat": openFoamReadMotion,
        "fz.dat": openFoamReadMotion,
        "mx.dat": openFoamReadMotion,
        "my.dat": openFoamReadMotion,
        "mz.dat": openFoamReadMotion,
        "PTS_localMotion_pos.dat": openFoamReadMotion,
        "PTS_localMotion_vel.dat": openFoamReadMotion,
        "PTS_localMotion_acc.dat": openFoamReadMotion,
        "forces.dat": openFoamReadForce,
        "fFluid.dat": openFoamReadForce,
        "mFluid.dat": openFoamReadForce,
        "fCstr.dat": openFoamReadForce,
        "mCstr.dat": openFoamReadForce,
        "acc.dat": openFoamReadForce,
    }
    fname = os.path.basename(filename)
    return dicoReader.get(fname, openFoamReadMotion)(filename, *args, **kwargs)
    # .get(fname, openFoamReadMotion) means that the method openFoamReadMotion is used by default (if filename is not in dicoReader)


def foamStarReadHeader(filename: str, maxLines: int = 5, add_units: bool = False):
    """ Read the header of an output file which has been constructed with foamStar style
    
    If the header is foamStar style, then it should have: 
    - info about the system in the first few lines
    - names of the columns
    - units

    For example: 
    ```
    # motion info (body)
    # time surge sway heave roll pitch yaw surge_vel sway_vel heav_vel omega_x omega_y omega_z surge_acc sway_acc heave_acc roll_acc pitch_acc yaw_acc
    # [s] [m] [m] [m] [deg] [deg] [deg] [m/s] [m/s] [m/s] [rad/s] [rad/s] [rad/s] [m/s2] [m/s2] [m/s2] [rad/s2] [rad/s2] [rad/s2]
    ```

    Last two lines are used to construct the column names, while other are discarded. 

    Parameters
    ----------
    filename: str
        filename, including path.
    add_units: bool, default: False
        if True, then the units are added to the column names: "surge [m]"
    maxLines: int
        maximal number of lines in the header (should not be modified, except if exotic header)

    Returns
    -------
    names: List[str]
        names to be used as column names for a reader.
    """
    with open(filename, "r") as fil:
        header = [
            l.strip().split()
            for l in [fil.readline() for line in range(maxLines + 1)]
            if l.startswith("#")
        ]
    names = header[-2][2:]
    if add_units:
        units = header[-1][2:]
        names = [name + " " + unit for (name, unit) in zip(names, units)]
    return names

def openFoamReadForce(filename, headerStyle=None, *args, **kwargs):
    """ Reader for foamStar and OpenFoam forces postProcesses.
    
    foamStar implements a fluidForces postProcess which writes a forces.dat 
    file, which structure is simpler than the OpenFoam forces.dat file. 
    To differenciate between both, we can read the first few lines: 
    
    - ` # forces ` is an OpenFoam file
    - ` # fluidForces (body)` is a foamStar file 

    Parameters
    ----------
    filename: str
    headerStyle: None or "foamStar"
        if "foamStar", the reader is automaticallly assuming a foamStar-style format
        (no parenthesis in the output file)
    """
    with open(filename, "r") as stream:
        first_line = stream.readline().split()
    if (headerStyle=="foamStar") or ("fluidForces" in first_line): 
        return openFoamReadForce_foamStarStyle(filename, *args, **kwargs)
    else: 
        return openFoamReadForce_OpenFoamStyle(filename, *args, **kwargs)
    #TODO: add this function


def openFoamReadForce_foamStarStyle(filename: str, add_units: bool=False):
    """
    Read openFoam "forces" file that uses the foamStar style (with parenthesis)

    Parameters
    ----------
    filename: str
    add_units: bool, default: False
        if True, then the units are added to the column names: "fx [N]"
    """
    names = foamStarReadHeader(filename, add_units=add_units)
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        delim_whitespace=True,
        dtype=float,
        index_col=0,
        names=names,
    )
    return df

def openFoamReadForce_OpenFoamStyle(filename, field="total"):
    """
    Read openFoam "forces" file that uses the OpenFoam style (with parenthesis)

    Parameters
    ----------
    filename: str
    field: str, default: "total"
        define if you want the "total" of the forces and moments or only the "pressure" component.
    """
    with open(filename, "r") as fil:
        data = [
            l.strip().strip().replace("(", " ").replace(")", " ").split()
            for l in fil.readlines()
            if not l.startswith("#")
        ]
    xAxis = np.array([float(l[0]) for l in data])
    nx = len(xAxis)
    ns = len(data[0]) - 1
    parsedArray = np.zeros((nx, ns))
    if field == "total" or field == "pressure":
        dataArray = np.zeros((nx, 6))
        labels = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]

    for i, l in enumerate(data):
        parsedArray[i, :] = [float(k) for k in l[1:]]

    if ns == 12:
        if field == "total":
            for i in range(3):
                dataArray[:, i] = parsedArray[:, 0 + i] + parsedArray[:, 3 + i]
                dataArray[:, i + 3] = parsedArray[:, 6 + i] + parsedArray[:, 9 + i]
        else:
            dataArray = parsedArray
            labels = [
                "Fx-Pressure",
                "Fy-Pressure",
                "Fz-Pressure",
                "Fx-Viscous",
                "Fy-Viscous",
                "Fz-Viscous",
                "Mx-Pressure",
                "My-Pressure",
                "Mz-Pressure",
                "Mx-Viscous",
                "My-Viscous",
                "Mz-Viscous",
            ]
    elif ns == 18:
        if field == "total":
            for i in range(3):
                dataArray[:, i] = (
                    parsedArray[:, 0 + i]
                    + parsedArray[:, 3 + i]
                    + parsedArray[:, 6 + i]
                )
                dataArray[:, i + 3] = (
                    parsedArray[:, 9 + i]
                    + parsedArray[:, 12 + i]
                    + parsedArray[:, 15 + i]
                )
        elif field == "pressure":
            for i in range(3):
                dataArray[:, i] = parsedArray[:, 0 + i]
                dataArray[:, i + 3] = parsedArray[:, 9 + i]

        else:
            dataArray = parsedArray
            labels = [
                "Fx-Pressure",
                "Fy-Pressure",
                "Fz-Pressure",
                "Fx-Viscous",
                "Fy-Viscous",
                "Fz-Viscous",
                "Fx-Porous",
                "Fy-Porous",
                "Fz-Porous",
                "Mx-Pressure",
                "My-Pressure",
                "Mz-Pressure",
                "Mx-Viscous",
                "My-Viscous",
                "Mz-Viscous",
                "Mx-Porous",
                "My-Porous",
                "Mz-Porous",
            ]
    else:
        dataArray = parsedArray
        if field != "total":
            labels = ["Unknown{}".format(j) for j in range(ns)]
    return pd.DataFrame(index=xAxis, data=dataArray, columns=labels)


def openFoamReadMotion(
    filename: str,
    headerStyle: str = "foamStar",
    add_units: bool = False,
    headerMaxLines: int = 5,
    namesLine: int = 1,
):
    """
    Read motion and internal loads from foamStar

    Parameters
    ----------
    filename: str
        filename, including path.
    headerStyle: str, default: "foamStar"
        indicate style of the header.
        If not foamStar, then the line number where to extract the column name should be given (default is second line)
    add_units: bool, default: False
        if True, then the units are added to the column names: "surge [m]"
    headerMaxLines: int
        maximal number of lines in the header (should not be modified, except if exotic header)
    """
    if headerStyle == "foamStar":
        names = foamStarReadHeader(filename, add_units=add_units, maxLines=headerMaxLines)
    else:
        with open(filename, "r") as fil:
            header = [
                l.strip().split()
                for l in [fil.readline() for line in range(headerMaxLines + 1)]
                if l.startswith("#")
            ]
            names = header[namesLine][2:]
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        delim_whitespace=True,
        dtype=float,
        index_col=0,
        names=names,
    )
    return df


def openFoamReadDisp(filename):
    """
    Read displacement signal from foamStar
    """

    with open(filename, "r") as fil:
        data = [
            l.strip().strip().replace("(", " ").replace(")", " ").split()
            for l in fil.readlines()
            if not l.startswith("#")
        ]
    data = np.array(list(filter(None, data)))
    data = data.astype(np.float)

    labels = ["Dx", "Dy", "Dz", "Rx", "Ry", "Rz"]

    xAxis = data[:, 0]
    dataArray = data[:, 1:]

    return pd.DataFrame(index=xAxis, data=dataArray, columns=labels)


def OpenFoamWriteDisp(df, filename):
    """
    Write displacement signal for foamStar
    """

    with open(filename, "w") as f:
        f.write("(\n")
        for index, row in df.iterrows():
            f.write(
                "({:21.15e}  (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) )\n".format(
                    index, *row
                )
            )
        f.write(")")


def OpenFoamWriteForce(df, filename):
    """
    Write force in foamStar format
    """

    ns = df.shape[1]

    if not (ns in [6, 12, 18]):
        print("ERROR: forces datafame should contain 6, 12 or 18 components!")
        os._exit(1)

    with open(filename, "w") as f:
        f.write("# Forces\n")
        f.write(
            "# CofR                : ({:21.15e} {:21.15e} {:21.15e})\n".format(0, 0, 0)
        )
        if ns == 6:
            f.write("# Time                forces(pressure) moment(pressure)\n")
        elif ns == 12:
            f.write(
                "# Time                forces(pressure viscous) moment(pressure viscous)\n"
            )
        elif ns == 18:
            f.write(
                "# Time                forces(pressure viscous porous) moment(pressure viscous porous)\n"
            )

        for index, row in df.iterrows():
            if ns == 6:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
            elif ns == 12:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
            elif ns == 18:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
