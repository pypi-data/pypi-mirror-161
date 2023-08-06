# -*- coding: utf-8 -*-
import numpy as np
import copy
import types
import json
import warnings

try:
    from paraview.simple import *
    from PIL import Image
    from PIL import ImageChops
except ModuleNotFoundError:
    # print("Paraview not found!")
    pass

try:
    from PIL import Image
    from PIL import ImageChops
except ModuleNotFoundError:
    # print("Pillow not found!")
    pass

import xml.etree.ElementTree as ET
import shutil
import h5py
import os


def ResetSession():
    """ Resets Paraview session (needed if multiple plots are generated successively)"""
    pxm = servermanager.ProxyManager()
    pxm.UnRegisterProxies()
    del pxm
    Disconnect()
    Connect()

def b2rcw(cmin_input, cmax_input):
    """ BLUEWHITERED   Blue, white, and red color map.
    This function is designed to generate a blue to red colormap. The color of the colorbar is from blue to white and
    then to red, corresponding to the data values from negative to zero to positive, respectively.
    The color white always correspondes to value zero. The brightness of blue and red will change according to your
    setting, so that the brightness of the color corresponded to the color of his opposite number.
    e.g. b2rcw(-3,6)   is from light blue to deep red
    e.g. b2rcw(-3,3)   is from deep blue to deep red

    Parameters
    ----------
    cmin_input : float
        Minimum value of data
    cmax_input : float
        Maximum value of data

    Returns
    -------
        newmap : nparray of float [N_RGB x 3]
    """

    # check the input
    if cmin_input >= cmax_input:
        raise ValueError('input error, the color range must be from a smaller one to a larger one')

    # color configuration : from blue to light blue to white untill to red
    red_top     = np.array([1, 0, 0])
    white_middle= np.array([1, 1, 1])
    blue_bottom = np.array([0, 0, 1])

    # color interpolation
    color_num = 250
    color_input = np.vstack((blue_bottom, white_middle, red_top))
    oldsteps = np.array([-1,0,1])
    newsteps = np.linspace(-1, 1, color_num)

    newmap_all = np.zeros((color_num,3))*np.nan

    for j in range(3):
        newmap_all[:, j] = np.min(np.vstack((np.max(
            np.vstack((np.interp(newsteps, oldsteps, color_input[:, j]), np.zeros(color_num))), axis=0),
                                             np.ones(color_num))), axis=0)

    if (cmin_input < 0)  &  (cmax_input > 0):

        if np.abs(cmin_input) < cmax_input:
            #    |--------|---------|--------------------|
            # -cmax      cmin       0                  cmax         [cmin,cmax]

            start_point = int(np.ceil((cmin_input+cmax_input)/2.0/cmax_input*color_num)-1)
            newmap = newmap_all[start_point:color_num, :]

        elif np.abs(cmin_input) >= cmax_input:
            #    |------------------|------|--------------|
            #   cmin                0     cmax          -cmin         [cmin,cmax]

            end_point = int(np.round((cmax_input-cmin_input)/2.0/np.abs(cmin_input)*color_num)-1)
            newmap = newmap_all[1:end_point, :]

    elif cmin_input >= 0:

        #   |-----------------|-------|-------------|
        # -cmax               0      cmin          cmax         [cmin,cmax]

        start_point = int(np.round((cmin_input+cmax_input)/2.0/cmax_input*color_num)-1)
        newmap = newmap_all[start_point:color_num, :]

    elif cmax_input <= 0:
        #   |------------|------|--------------------|
        #  cmin         cmax    0                  -cmin         [cmin,cmax]

        end_point = int(np.round((cmax_input-cmin_input)/2.0/np.abs(cmin_input)*color_num)-1)
        newmap = newmap_all[1:end_point, :]

    return newmap


def crop_data_hdf5_to_datarange(ps):
    """
    Crops the data (quantity) in .hdf5 data file to datarange and overwrites the original .hdf5 data file pointed by
    the .xdmf file.

    Parameters
    ----------
    ps : dict
        Plot settings dictionary created with create_plotsettings_dict(plot_function)

    Returns
    -------
    fn_hdf5 : str
        Filename (incl. path) of data .hdf5 file (read from .xmdf file)
    <File> : .hdf5 file
        *_backup.hdf5 backup file of original .hdf5 data file
    <File> .hdf5 file
        Cropped data
    """

    fn_hdf5_end = []
    key_hdf5 = []

    # Read .xdmf input file
    tree = ET.parse(ps['fname_in'][0])
    root = tree.getroot()

    if type(ps['quantity']) == list:
        quantity = ps['quantity'][0]
    else:
        quantity = ps['quantity']

    # Get .hdf5 data filename and hdf5 key of 'quantity'
    for data_attribute in root.iter('Attribute'):
        if data_attribute.get('Name') == quantity:
            location = data_attribute[0].text[1: -1]
            fn_hdf5_end, key_hdf5 = location.split(':')

    if not fn_hdf5_end:
        raise AttributeError('ps[\'quantity\'] not found in .hdf5 dataset')

    fn_hdf5 = os.path.join(os.path.split(ps['fname_in'][0])[0], fn_hdf5_end)

    # Backup original .hdf5 datafile *_backup.hdf5
    shutil.copyfile(fn_hdf5, os.path.splitext(fn_hdf5)[0] + '_backup' + os.path.splitext(fn_hdf5)[1])

    # Read 'quantity' data from .hdf5
    f = h5py.File(fn_hdf5, 'r')
    data = f[key_hdf5][:]
    f.close()

    if ps["calculator"] is not None:
        calc_expre = ps["calculator"]
        calc_expre = calc_expre.replace("{}", "data")
        calc_expre = calc_expre.replace("^", "**")
        calc_expre = calc_expre.replace("sin", "np.sin")
        calc_expre = calc_expre.replace("cos", "np.cos")

        # crop data to datarange
        data_calc = eval(calc_expre)

    else:
        data_calc = data

    data_cropped = copy.deepcopy(data_calc)

    if ps['datarange'][0] is None:
        ps['datarange'][0] = np.min(data_calc)

    if ps['datarange'][1] is None:
        ps['datarange'][1] = np.max(data_calc)

    delta_range = float(ps['datarange'][1]) - float(ps['datarange'][0])

    data_cropped[data_calc < float(ps['datarange'][0])] = float(ps['datarange'][0])
    data_cropped[data_calc > float(ps['datarange'][1])] = float(ps['datarange'][1]) - delta_range/1000

    # Overwrite and save dataset with cropped data
    f = h5py.File(fn_hdf5, 'r+')
    del f[key_hdf5]
    f.create_dataset(name=key_hdf5, data=data_cropped)
    f.close()

    return fn_hdf5


def crop_image(fname_image, fname_image_cropped):
    """Remove surrounding empty space around an image. This implemenation
    assumes that the surrounding space has the same colour as the top leftmost
    pixel.

    Parameters
    ----------
    fname_image : str
        Filename of image to be cropped

    Returns
    -------
    <File> : .png file
        Cropped image file saved as "fname_image_cropped"
    """
    im = Image.open(fname_image)

    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()

    if not bbox:
        im_cropped = im
    else:
        im_cropped = im.crop(bbox)

    im_cropped.save(fname_image_cropped)


def create_plot_settings_dict(plotfunction_type):
    """
    Creates a dictionary with default plotsettings.

    Parameters
    ----------
    plotfunction_type : str
        Plot function the dictionary is generated for:

        - 'surface_vector_plot'
        - 'surface_vector_plot_vtu'
        - 'volume_plot'
        - 'volume_plot_vtu'

    Returns
    -------
    ps : dict
        Dictionary containing the plotsettings:
    axes : boolean
        Show orientation axes (TRUE / FALSE)
    background_color : nparray [1 x 3]
        Set background color of exported image RGB (0...1)
    calculator : str
        Format string with placeholder of the calculator expression the quantity to plot is modified with
        (e.g.: "{}^5")
    clip_coords : nparray of float [N_clips x 3]
        Coordinates of clip surface origins (x,y,z)
    clip_normals : nparray of float [N_clips x 3]
        Surface normals of clip surfaces pointing in the direction where the volume is kept for
        clip_type = ['clip' ...] (x,y,z)
    clip_type : list of str
        Type of clipping:

        - 'clip':  cut geometry but keep volume behind
        - 'slice': cut geometry and keep only the slice
    coil_dipole_scaling : list [1 x 2]
        Specify the scaling type of the dipoles (2 entries):

        coil_dipole_scaling[0]:

        - 'uniform': uniform scaling, i.e. all dipoles have the same size
        - 'scaled': size scaled according to dipole magnitude

        coil_dipole_scaling[1]:

        - scalar scale parameter of dipole size
    coil_dipole_color : str or list
        Color of the dipoles; either str to specify colormap (e.g. 'jet') or list of RGB values [1 x 3] (0...1)
    coil_axes : boolean
        Plot coil axes visualizing the principle direction and orientation of the coil (Default: True)
    colorbar_label : str
        Label of plotted data close to colorbar
    colorbar_position : list of float [1 x 2]
        Position of colorbar (lower left corner) 0...1 [x_pos, y_pos]
    colorbar_orientation : str
        Orientation of colorbar ('Vertical', 'Horizontal')
    colorbar_aspectratio : int
        Aspectratio of colorbar (higher values make it thicker)
    colorbar_titlefontsize : float
        Fontsize of colorbar title
    colorbar_labelfontsize : float
        Fontsize of colorbar labels (numbers)
    colorbar_labelformat : str
        Format of colorbar labels (e.g.: '%-#6.3g')
    colorbar_numberoflabels : int
        maximum number of colorbar labels
    colorbar_labelcolor : list of float [1 x 3]
        Color of colorbar labels in RGB (0...1)
    colormap : str or nparray

        if nparray [1 x 4*N]: custom colormap providing data and corresponding RGB values

            .. math::
               \\begin{bmatrix}
                data_{1} & R_1 & G_1 & B_1  \\\\
                data_{2} & R_2 & G_2 & B_2  \\\\
                ...      & ... & ... & ...  \\\\
                data_{N} & R_N & G_N & B_N  \\\\
               \\end{bmatrix}

        if str: colormap of plotted data chosen from included presets:

        - 'Cool to Warm',
        - 'Cool to Warm (Extended)',
        - 'Blue to Red Rainbow',
        - 'X Ray',
        - 'Grayscale',
        - 'jet',
        - 'hsv',
        - 'erdc_iceFire_L',
        - 'Plasma (matplotlib)',
        - 'Viridis (matplotlib)',
        - 'gray_Matlab',
        - 'Spectral_lowBlue',
        - 'BuRd'
        - 'Rainbow Blended White'
        - 'b2rcw'
    colormap_categories : boolean
        Use categorized (discrete) colormap
    datarange : list [1 x 2]
        Minimum and Maximum of plotted datarange [MIN, MAX] (default: automatic)
    domain_IDs : int or list of int
        Domain IDs

        surface plot: Index of surface where the data is plotted on (Default: 0)

        volume plot: Specify the domains IDs to show in plot (default: all) Attention! Has to be included in the
        dataset under the name 'tissue'! e.g. for SimNIBS:

        - 1 -> white matter (WM)
        - 2 -> grey matter (GM)
        - 3 -> cerebrospinal fluid (CSF)
        - 4 -> skull
        - 5 -> skin
    domain_label : str
        Label of the dataset which contains the domain IDs (default: 'tissue_type')
    edges : boolean
        Show edges of mesh (TRUE / FALSE)
    fname_in : str or list of str
        Filenames of input files, 2 possibilities:

        - .xdmf-file: filename of .xmdf (needs the corresponding .hdf5 file(s) in the same folder)
        - .hdf5-file(s): filename(s) of .hdf5 file(s) containing the data and the geometry. The data can be provided
          in the first hdf5 file and the geometry can be provided in the second file. However, both can be also
          provided in a single hdf5 file.
    fname_png : str
        Name of output .png file (incl. path)
    fname_vtu_volume : str
        Name of .vtu volume file containing volume data (incl. path)
    fname_vtu_surface : str
        Name of .vtu surface file containing surface data (incl. path) (to distinguish tissues)
    fname_vtu_coil : str
        Name of coil .vtu file (incl. path) (optional)
    info : str
        Information about the plot the settings are belonging to
    interpolate : boolean
        Interpolate data for visual smoothness (TRUE / FALSE)
    NanColor : list of float [3]
        RGB color values for "Not a Number" values (range 0 ... 1)
    opacitymap : nparray
        Points defining the piecewise linear opacity transfer function (transparency) (default: no transparency)
        connecting data values with opacity (alpha) values ranging from 0 (max. transparency) to 1 (no transparency)

        .. math::
           \\begin{bmatrix}
            data_{1} & opac_1 & 0.5 & 0  \\\\
            data_{2} & opac_2 & 0.5 & 0  \\\\
            ...      & ...   & ... & ...\\\\
            data_{N} & opac_N & 0.5 & 0  \\\\
           \\end{bmatrix}
    plot_function : str
        Function the plot is generated with:

        - 'surface_vector_plot'
        - 'surface_vector_plot_vtu'
        - 'volume_plot'
        - 'volume_plot_vtu'
    png_resolution : float
        Resolution parameter of output image (1...5)
    quantity : str
        Label of magnitude dataset to plot
    surface_color : nparray [1 x 3]
        Color of brain surface in RGB (0...1) for better visability of tissue borders
    surface_smoothing : bool
        Smooth the plotted surface (True/False)
    show_coil : boolean
        show coil if present in dataset as block termed 'coil' (Default: True)
    vcolor : nparray of float [N_vecs x 3]
        Array containing the RGB values between 0...1 of the vector groups in dataset to plot
    vector_mode : dict

        dict key determines the type how many vectors are shown:
        - 'All Points'
        - 'Every Nth Point'
        - 'Uniform Spatial Distribution'

        dict value (int) is the corresponding number of vectors

        - 'All Points' (not set)
        - 'Every Nth Point' (every Nth vector is shown in the grid)
        - 'Uniform Spatial Distribution' (not set)
    view : list
        Camera position and angle
        [[3 x CameraPosition], [3 x CameraFocalPoint], [3 x CameraViewUp], 1 x CameraParallelScale]
    viewsize : nparray [1 x 2]
        Set size of exported image in pixel [width x height] will be extra scaled by parameter png_resolution
    vlabels : list of str
        Labels of vector datasets to plot (other present datasets are ignored)
    vscales : list of float
        Scale parameters of vector groups to plot
    vscale_mode : list of str [N_vecs x 1]
        List containing the type of vector scaling:

        - 'off': all vectors are normalized
        - 'vector': vectors are scaled according to their magnitudeeee
    """

    if plotfunction_type not in ['surface_vector_plot', 'surface_vector_plot_vtu', 'volume_plot', 'volume_plot_vtu']:
        raise Exception('plotfunction_type not set correctly, specify either [\'surface_vector_plot\', \
                            \'surface_vector_plot_vtu\', \'volume_plot\', \'volume_plot_vtu\']')

    ps = dict()
    ps['info'] = []
    ps['plot_function'] = plotfunction_type
    ps['fname_png'] = []
    ps['png_resolution'] = 1
    ps['quantity'] = None
    ps['datarange'] = None
    ps['colorbar_label'] = ''
    ps['colorbar_position'] = []
    ps['colorbar_orientation'] = 'Vertical'
    ps['colorbar_aspectratio'] = 20
    ps['colorbar_titlefontsize'] = 7
    ps['colorbar_labelfontsize'] = 7
    ps['colorbar_labelformat'] = '%-#6.3g'
    ps['colorbar_numberoflabels'] = 5
    ps['colorbar_labelcolor'] = [0, 0, 0]
    ps['colorbar_font'] = 'Arial'
    ps['view'] = 0
    ps['interpolate'] = False
    ps['edges'] = False
    ps['axes'] = True
    ps['colormap'] = "jet"
    ps['colormap_categories'] = False
    ps['opacitymap'] = None
    ps['background_color'] = [1, 1, 1]
    ps['viewsize'] = [800, 800]
    ps['NanColor'] = [1, 1, 1]
    ps["surface_smoothing"] = True
    ps["calculator"] = None

    # filename of input files
    if plotfunction_type in ['surface_vector_plot', 'surface_vector_plot_vtu', 'volume_plot']:
        ps['fname_in'] = []

    elif plotfunction_type in ['volume_plot_vtu']:
        ps['fname_vtu_volume'] = []
        ps['fname_vtu_surface'] = []
        ps['fname_vtu_coil'] = []

    # new features in .xdmf plot functions
    if plotfunction_type in ['surface_vector_plot', 'volume_plot', 'volume_plot_vtu']:
        ps['domain_label'] = 'tissue_type'
        ps['domain_IDs'] = 0
        ps['show_coil'] = True
        ps['coil_dipole_scaling'] = ['uniform', 1]
        ps['coil_dipole_color'] = 'jet'
        ps['coil_axes'] = True

    # surface specific properties
    if plotfunction_type in ['surface_vector_plot', 'surface_vector_plot_vtu']:
        ps['vlabels'] = ''
        ps['vscales'] = np.array([1])
        ps['vscale_mode'] = 'vector'
        ps['vector_mode'] = {'All Points': 0}
        ps['vcolor'] = np.array([1.0, 0.0, 0.0])

    # volume specific properties
    if plotfunction_type in ['volume_plot', 'volume_plot_vtu']:
        ps['clip_coords'] = np.array([])
        ps['clip_normals'] = np.array([])
        ps['clip_type'] = []
        ps['surface_color'] = [1, 1, 1]

    return ps


def surface_vector_plot(ps):
    """
    Generate plot with Paraview from data in .hdf5 file(s).

    Parameters
    ----------
    ps : dict
        Plot settings dict initialized with create_plot_settings_dict(plotfunction_type='surface_vector_plot')

    Returns
    -------
    <File> : .png file
        Generated plot
    """

    if type(ps['quantity']) is list:
        quantity = ps['quantity'][0]
    else:
        quantity = ps['quantity']

    # add whitespace if colorbar label is not given (empty colorbar labels are plotted wrong)
    if ps['colorbar_label'] is None or ps['colorbar_label']=='':
        ps['colorbar_label'] = ' '

    if type(ps['fname_in']) is str:
        ps['fname_in'] = [ps['fname_in']]

    _, ext = os.path.splitext(ps['fname_in'][0])

    # make .xdmf file if .hdf5 file is provided
    if ext == '.hdf5':
        mode = 'hdf5'
        fname_load = os.path.join(os.path.splitext(ps['fname_in'][0]), '.xdmf')

        if len(ps['fname_in']) == 1:
            write_xdmf(hdf5_fn = ps['fname_in'][0], hdf5_geo_fn=None, overwrite_xdmf=True)
        elif len(ps['fname_in']) == 2:
            write_xdmf(hdf5_fn = ps['fname_in'][0], hdf5_geo_fn = ps['fname_in'][1], overwrite_xdmf=True)
        else:
            raise Exception('Please specify either one .hdf5 file containing data and geometry or two .hdf5 files,'
                            'whereas the first contains the data and the second the geometry!')
    elif ext == '.xdmf':
        mode = 'xdmf'
        fname_load = ps['fname_in']

    else:
        raise Exception('Please check file type and extension!')

    # crop data to datarange and temporarily save it to to avoid graphics bug
    ps['fname_in'] = fname_load

    fn_data_hdf5 = crop_data_hdf5_to_datarange(ps)
    data_cropped = True

    # set target for interpolation
    if ps['interpolate']:
        target = 'POINTS'
    else:
        target = 'CELLS'

    # create a new 'Xdmf3ReaderT' for data
    p = paraview.simple.Xdmf3ReaderT(FileName=[fname_load[0]])
    renderView = GetActiveViewOrCreate('RenderView')

    label_datasets = p.CellArrays
    N_datasets = len(label_datasets)

    if len(ps['datarange']) == 1 and ps['datarange'][0] == None:
        datarange = [None, None]

    # set surface smoothing
    if ps["surface_smoothing"]:
        # create a new 'Extract Surface'
        p = paraview.simple.ExtractSurface(Input=p)

        # create a new 'Generate Surface Normals'
        p = paraview.simple.GenerateSurfaceNormals(Input=p)

        # Properties modified on generateSurfaceNormals1
        p.FeatureAngle = 50.0

    # set calculator
    # if ps["calculator"] is not None:
    #     # create a new 'Calculator'
    #     ps["calculator"] = ps["calculator"].replace("{}", ps["quantity"])
    #     Hide(p, renderView)
    #     p = paraview.simple.Calculator(Input=p)
    #     p.AttributeType = 'Cell Data'
    #     exec('p.Function = "' + ps["calculator"] + '"')
    #     ps["quantity"] = "Result"
    #     quantity = "Result"

    # get data ranges of included datasets
    if None in ps['datarange']:
        datarange_temp = servermanager.Fetch(p).GetBlock(0).GetCellData().GetArray(quantity).GetRange(0)

        if ps['datarange'][0] is None:
            ps['datarange'][0] = datarange_temp[0]

        if ps['datarange'][1] is None:
            ps['datarange'][1] = datarange_temp[1]

    # check if curvature data exists
    if np.any([True for label in ['curve', 'curv', 'curvature'] if label in label_datasets]):
        curve_exists = True
        curve_label = [label for label in ['curve', 'curv'] if label in ['curv', 'test']]
    else:
        curve_exists = False
        curve_label = ['']

    renderView = GetActiveViewOrCreate('RenderView')

    pLUT = GetColorTransferFunction(quantity)
    # pLUT.LockDataRange = 0  # not in v5.8 anymore
    pLUT.InterpretValuesAsCategories = 0
    pLUT.ShowCategoricalColorsinDataRangeOnly = 0
    pLUT.RescaleOnVisibilityChange = 0
    pLUT.EnableOpacityMapping = 0
    #pLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 0.50000500005, 0.865003, 0.865003, 0.865003,
    #                           1.0000100001, 0.705882, 0.0156863, 0.14902]
    pLUT.UseLogScale = 0
    pLUT.ColorSpace = 'Diverging'
    pLUT.UseBelowRangeColor = 0
    pLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    pLUT.UseAboveRangeColor = 0
    pLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    pLUT.NanColor = ps['NanColor']
    pLUT.Discretize = 1
    pLUT.NumberOfTableValues = 256
    pLUT.ScalarRangeInitialized = 1.0
    pLUT.HSVWrap = 0
    pLUT.VectorComponent = 0
    pLUT.VectorMode = 'Magnitude'
    pLUT.AllowDuplicateScalars = 1
    pLUT.Annotations = []
    pLUT.ActiveAnnotatedValues = []
    pLUT.IndexedColors = []

    # show data in view
    pDisplay = Show(p, renderView)

    # trace defaults for the display properties.
    pDisplay.Representation = 'Surface'
    pDisplay.AmbientColor = [1.0, 1.0, 1.0]
    pDisplay.ColorArrayName = ['POINTS', ps['domain_label']]
    pDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.LookupTable = pLUT
    pDisplay.MapScalars = 1
    pDisplay.InterpolateScalarsBeforeMapping = 1
    pDisplay.Opacity = 1.0
    pDisplay.PointSize = 2.0
    pDisplay.LineWidth = 1.0
    pDisplay.Interpolation = 'Gouraud'
    pDisplay.Specular = 0.0
    pDisplay.SpecularColor = [1.0, 1.0, 1.0]
    pDisplay.SpecularPower = 100.0
    pDisplay.Ambient = 0.0
    pDisplay.Diffuse = 1.0
    pDisplay.EdgeColor = [0.0, 0.0, 0.5]
    pDisplay.BackfaceRepresentation = 'Follow Frontface'
    pDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceOpacity = 1.0
    pDisplay.Position = [0.0, 0.0, 0.0]
    pDisplay.Scale = [1.0, 1.0, 1.0]
    pDisplay.Orientation = [0.0, 0.0, 0.0]
    pDisplay.Origin = [0.0, 0.0, 0.0]
    pDisplay.Pickable = 1
    pDisplay.Texture = None
    pDisplay.Triangulate = 0
    pDisplay.NonlinearSubdivisionLevel = 1
    pDisplay.OSPRayUseScaleArray = 0
    pDisplay.OSPRayScaleArray = ps["quantity"]
    pDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    pDisplay.GlyphType = 'Arrow'
    pDisplay.SelectionCellLabelBold = 0
    pDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    pDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionCellLabelFontSize = 18
    pDisplay.SelectionCellLabelItalic = 0
    pDisplay.SelectionCellLabelJustification = 'Left'
    pDisplay.SelectionCellLabelOpacity = 1.0
    pDisplay.SelectionCellLabelShadow = 0
    pDisplay.SelectionPointLabelBold = 0
    pDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    pDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionPointLabelFontSize = 18
    pDisplay.SelectionPointLabelItalic = 0
    pDisplay.SelectionPointLabelJustification = 'Left'
    pDisplay.SelectionPointLabelOpacity = 1.0
    pDisplay.SelectionPointLabelShadow = 0
    # pDisplay.ScalarOpacityUnitDistance = 4.008392218456473  # surface_smoothing
    # pDisplay.SelectMapper = 'Projected tetra'  # surface_smoothing
    pDisplay.GaussianRadius = 0.0
    pDisplay.ShaderPreset = 'Sphere'
    pDisplay.Emissive = 0
    pDisplay.ScaleByArray = 0
    pDisplay.SetScaleArray = ['POINTS', ps["quantity"]]
    pDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    pDisplay.OpacityByArray = 0
    pDisplay.OpacityArray = ['POINTS', ps["quantity"]]
    pDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    pDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    pDisplay.GlyphType.TipResolution = 6
    pDisplay.GlyphType.TipRadius = 0.1
    pDisplay.GlyphType.TipLength = 0.35
    pDisplay.GlyphType.ShaftResolution = 6
    pDisplay.GlyphType.ShaftRadius = 0.03
    pDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    pDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    pDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView.ResetCamera()

    # show color bar/color legend
    pDisplay.SetScalarBarVisibility(renderView, False)

    # get opacity transfer function/opacity map for 'tissuetype'
    pPWF = GetOpacityTransferFunction('tissuetype')
    pPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.0000100001, 1.0, 0.5, 0.0]
    pPWF.AllowDuplicateScalars = 1
    pPWF.ScalarRangeInitialized = 1

    # =============================================================================
    # threshold data to choose surface to plot data on
    # =============================================================================
    # create a new 'Threshold'

    t1 = paraview.simple.Threshold(Input=p)
    t1.Scalars = ['POINTS', ps['domain_label']]
    t1.ThresholdRange = [ps['domain_IDs'], ps['domain_IDs']]
    t1.AllScalars = 1
    t1.UseContinuousCellRange = 0

    if ps['interpolate']:
        t1i = paraview.simple.CellDatatoPointData(Input=t1)
        t1i.PassCellData = 0
        t1i.PieceInvariant = 0
        # show data in view
        t1Display = Show(t1i, renderView)
    else:
        # show data in view
        t1Display = Show(t1, renderView)

    # trace defaults for the display properties.
    t1Display.Representation = 'Surface'
    t1Display.AmbientColor = [1.0, 1.0, 1.0]
    t1Display.ColorArrayName = ['POINTS', ps['domain_label']]
    t1Display.DiffuseColor = [1.0, 1.0, 1.0]
    t1Display.LookupTable = pLUT
    t1Display.MapScalars = 1
    t1Display.InterpolateScalarsBeforeMapping = 1
    t1Display.Opacity = 1.0
    t1Display.PointSize = 2.0
    t1Display.LineWidth = 1.0
    t1Display.Interpolation = 'Gouraud'
    t1Display.Specular = 0.0
    t1Display.SpecularColor = [1.0, 1.0, 1.0]
    t1Display.SpecularPower = 100.0
    t1Display.Ambient = 0.0
    t1Display.Diffuse = 1.0
    t1Display.EdgeColor = [0.0, 0.0, 0.5]
    t1Display.BackfaceRepresentation = 'Follow Frontface'
    t1Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    t1Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    t1Display.BackfaceOpacity = 1.0
    t1Display.Position = [0.0, 0.0, 0.0]
    t1Display.Scale = [1.0, 1.0, 1.0]
    t1Display.Orientation = [0.0, 0.0, 0.0]
    t1Display.Origin = [0.0, 0.0, 0.0]
    t1Display.Pickable = 1
    t1Display.Texture = None
    t1Display.Triangulate = 0
    t1Display.NonlinearSubdivisionLevel = 1
    t1Display.OSPRayUseScaleArray = 0
    t1Display.OSPRayScaleArray = ps['domain_label']
    t1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    t1Display.GlyphType = 'Arrow'
    t1Display.SelectionCellLabelBold = 0
    t1Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    t1Display.SelectionCellLabelFontFamily = 'Arial'
    t1Display.SelectionCellLabelFontSize = 18
    t1Display.SelectionCellLabelItalic = 0
    t1Display.SelectionCellLabelJustification = 'Left'
    t1Display.SelectionCellLabelOpacity = 1.0
    t1Display.SelectionCellLabelShadow = 0
    t1Display.SelectionPointLabelBold = 0
    t1Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    t1Display.SelectionPointLabelFontFamily = 'Arial'
    t1Display.SelectionPointLabelFontSize = 18
    t1Display.SelectionPointLabelItalic = 0
    t1Display.SelectionPointLabelJustification = 'Left'
    t1Display.SelectionPointLabelOpacity = 1.0
    t1Display.SelectionPointLabelShadow = 0
    t1Display.ScalarOpacityUnitDistance = 4.903157073141748
    t1Display.SelectMapper = 'Projected tetra'
    t1Display.GaussianRadius = 0.0
    t1Display.ShaderPreset = 'Sphere'
    t1Display.Emissive = 0
    t1Display.ScaleByArray = 0
    t1Display.SetScaleArray = ['POINTS', ps["quantity"]]
    t1Display.ScaleTransferFunction = 'PiecewiseFunction'
    t1Display.OpacityByArray = 0
    t1Display.OpacityArray = ['POINTS', ps["quantity"]]
    t1Display.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    t1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    t1Display.GlyphType.TipResolution = 6
    t1Display.GlyphType.TipRadius = 0.1
    t1Display.GlyphType.TipLength = 0.35
    t1Display.GlyphType.ShaftResolution = 6
    t1Display.GlyphType.ShaftRadius = 0.03
    t1Display.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    t1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    t1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(p, renderView)

    # set scalar coloring
    if curve_exists:
        ColorBy(t1Display, (target, curve_label[0]))
    else:
        ColorBy(t1Display, None)

    # rescale color and/or opacity maps used to include current data range
    t1Display.RescaleTransferFunctionToDataRange(True)

    # show color bar/color legend
    # t1Display.SetScalarBarVisibility(renderView, False)

    # get color transfer function/color map for 'curv'
    curvLUT = GetColorTransferFunction(curve_label[0])
    # curvLUT.LockDataRange = 0  # not in v5.8 anymore
    curvLUT.InterpretValuesAsCategories = 0
    curvLUT.ShowCategoricalColorsinDataRangeOnly = 0
    curvLUT.RescaleOnVisibilityChange = 0
    curvLUT.EnableOpacityMapping = 0
    #curvLUT.RGBPoints = [-3.1706008911132812, 1.0, 1.0, 1.0, 1.9234193563461304, 0.0, 0.0, 0.0]
    curvLUT.UseLogScale = 0
    curvLUT.ColorSpace = 'RGB'
    curvLUT.UseBelowRangeColor = 0
    curvLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    curvLUT.UseAboveRangeColor = 0
    curvLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    curvLUT.NanColor = ps['NanColor']
    curvLUT.Discretize = 1
    curvLUT.NumberOfTableValues = 256
    curvLUT.ScalarRangeInitialized = 1.0
    curvLUT.HSVWrap = 0
    curvLUT.VectorComponent = 0
    curvLUT.VectorMode = 'Magnitude'
    curvLUT.AllowDuplicateScalars = 1
    curvLUT.Annotations = []
    curvLUT.ActiveAnnotatedValues = []
    curvLUT.IndexedColors = []

    # get opacity transfer function/opacity map for 'curv'
    curvPWF = GetOpacityTransferFunction(curve_label[0])
    #curvPWF.Points = [-3.1706008911132812, 0.0, 0.5, 0.0, 1.9234193563461304, 1.0, 0.5, 0.0]
    curvPWF.AllowDuplicateScalars = 1
    curvPWF.ScalarRangeInitialized = 1

    # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
    curvLUT.ApplyPreset('Grayscale', True)

    # =============================================================================
    # threshold data to choose data to plot on surface
    # =============================================================================

    # create a new 'Threshold'
    t2 = paraview.simple.Threshold(Input=t1)
    t2.Scalars = ['CELLS', quantity]

    if ps['datarange']:
        t2.ThresholdRange = [float(ps['datarange'][0]), ps['datarange'][1]]

    t2.AllScalars = 1
    t2.UseContinuousCellRange = 0

    if ps['interpolate']:
        # create a new 'Cell Data to Point Data'
        t2i = paraview.simple.CellDatatoPointData(Input=t2)
        t2i.PassCellData = 0
        t2i.PieceInvariant = 0
        # show data in view
        t2Display = Show(t2i, renderView)
    else:
        # show data in view
        t2Display = Show(t2, renderView)


    # trace defaults for the display properties.
    t2Display.Representation = 'Surface'
    t2Display.AmbientColor = [1.0, 1.0, 1.0]
    t2Display.ColorArrayName = ['POINTS', quantity]
    t2Display.DiffuseColor = [1.0, 1.0, 1.0]
    t2Display.LookupTable = pLUT
    t2Display.MapScalars = 1
    t2Display.InterpolateScalarsBeforeMapping = 1
    t2Display.Opacity = 1.0
    t2Display.PointSize = 2.0
    t2Display.LineWidth = 1.0
    t2Display.Interpolation = 'Gouraud'
    t2Display.Specular = 0.0
    t2Display.SpecularColor = [1.0, 1.0, 1.0]
    t2Display.SpecularPower = 100.0
    t2Display.Ambient = 0.0
    t2Display.Diffuse = 1.0
    t2Display.EdgeColor = [0.0, 0.0, 0.5]
    t2Display.BackfaceRepresentation = 'Follow Frontface'
    t2Display.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    t2Display.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    t2Display.BackfaceOpacity = 1.0
    t2Display.Position = [0.0, 0.0, 0.0]
    t2Display.Scale = [1.0, 1.0, 1.0]
    t2Display.Orientation = [0.0, 0.0, 0.0]
    t2Display.Origin = [0.0, 0.0, 0.0]
    t2Display.Pickable = 1
    t2Display.Texture = None
    t2Display.Triangulate = 0
    t2Display.NonlinearSubdivisionLevel = 1
    t2Display.OSPRayUseScaleArray = 0
    t2Display.OSPRayScaleArray = quantity
    t2Display.OSPRayScaleFunction = 'PiecewiseFunction'
    t2Display.GlyphType = 'Arrow'
    t2Display.SelectionCellLabelBold = 0
    t2Display.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    t2Display.SelectionCellLabelFontFamily = 'Arial'
    t2Display.SelectionCellLabelFontSize = 18
    t2Display.SelectionCellLabelItalic = 0
    t2Display.SelectionCellLabelJustification = 'Left'
    t2Display.SelectionCellLabelOpacity = 1.0
    t2Display.SelectionCellLabelShadow = 0
    t2Display.SelectionPointLabelBold = 0
    t2Display.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    t2Display.SelectionPointLabelFontFamily = 'Arial'
    t2Display.SelectionPointLabelFontSize = 18
    t2Display.SelectionPointLabelItalic = 0
    t2Display.SelectionPointLabelJustification = 'Left'
    t2Display.SelectionPointLabelOpacity = 1.0
    t2Display.SelectionPointLabelShadow = 0
    t2Display.ScalarOpacityUnitDistance = 3.974831691176322
    t2Display.SelectMapper = 'Projected tetra'
    t2Display.GaussianRadius = 0.0
    t2Display.ShaderPreset = 'Sphere'
    t2Display.Emissive = 0
    t2Display.ScaleByArray = 0
    t2Display.SetScaleArray = ['POINTS', quantity]
    t2Display.ScaleTransferFunction = 'PiecewiseFunction'
    t2Display.OpacityByArray = 0
    t2Display.OpacityArray = ['POINTS', quantity]
    t2Display.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    t2Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    t2Display.GlyphType.TipResolution = 6
    t2Display.GlyphType.TipRadius = 0.1
    t2Display.GlyphType.TipLength = 0.35
    t2Display.GlyphType.ShaftResolution = 6
    t2Display.GlyphType.ShaftRadius = 0.03
    t2Display.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    t2Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    t2Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # set scalar coloring
    ColorBy(t2Display, (target, quantity))

    # show color bar/color legend
    t2Display.SetScalarBarVisibility(renderView, True)

    # get color transfer function/color map for 'mic'
    t2LUT = GetColorTransferFunction(quantity)
    # t2LUT.LockDataRange = 0  # not in v5.8 anymore
    t2LUT.InterpretValuesAsCategories = 0
    t2LUT.ShowCategoricalColorsinDataRangeOnly = 0
    t2LUT.RescaleOnVisibilityChange = 0
    #t2LUT.RGBPoints = [0.0006630485877394676, 0.231373, 0.298039, 0.752941, 0.42029112903401256, 0.865003, 0.865003,
    #                    0.865003, 0.8399192094802856, 0.705882, 0.0156863, 0.14902]
    t2LUT.UseLogScale = 0
    t2LUT.ColorSpace = 'Diverging'
    t2LUT.UseBelowRangeColor = 0
    t2LUT.BelowRangeColor = [0.0, 0.0, 0.0]
    t2LUT.UseAboveRangeColor = 0
    t2LUT.AboveRangeColor = [1.0, 1.0, 1.0]
    t2LUT.NanColor = ps['NanColor']
    t2LUT.Discretize = 1
    t2LUT.NumberOfTableValues = 256
    t2LUT.ScalarRangeInitialized = 1.0
    t2LUT.HSVWrap = 0
    t2LUT.VectorComponent = 0
    t2LUT.VectorMode = 'Magnitude'
    t2LUT.AllowDuplicateScalars = 1
    t2LUT.Annotations = []
    t2LUT.ActiveAnnotatedValues = []
    t2LUT.IndexedColors = []

    t2PWF = GetOpacityTransferFunction(quantity)
    if ps['opacitymap']:
        t2LUT.EnableOpacityMapping = 1
        t2PWF.Points = ps['opacitymap']

    # get opacity transfer function/opacity map for 'mic'
    t2PWF.AllowDuplicateScalars = 1
    t2PWF.ScalarRangeInitialized = 1

    # camera placement for renderView
    if len(ps['view']) == 4:
        renderView.CameraPosition = ps['view'][0]
        renderView.CameraFocalPoint = ps['view'][1]
        renderView.CameraViewUp = ps['view'][2]
        renderView.CameraParallelScale = ps['view'][3][0]
    else:
        renderView.ResetCamera()

    if ps['interpolate']:
        t2LUT.ColorSpace = 'RGB'
    else:
        t2LUT.ColorSpace = 'RGB' #'Diverging'

    # =============================================================================
    # set colormap for magnitude plot
    # =============================================================================
    if type(ps['colormap']) is str:
        colormap_presets = {'Cool to Warm',
                            'Cool to Warm (Extended)',
                            'Blue to Red Rainbow',
                            'X Ray',
                            'Grayscale',
                            'jet',
                            'hsv',
                            'erdc_iceFire_L',
                            'Plasma (matplotlib)',
                            'Viridis (matplotlib)',
                            'gray_Matlab',
                            'Spectral_lowBlue',
                            'BuRd',
                            'Rainbow Blended White',
                            'b2rcw'}

        # set colorbar to 'jet' if not specified in presets
        if not (ps['colormap'] in colormap_presets):
            print((
                'Changing colormap to \'jet\' since user specified colormap \'{}\' is not part of the included presets ...').format(
                ps['colormap']))
            colormap = 'jet'

        if ps['colormap'] == 'b2rcw':
            rgb_values = b2rcw(ps['datarange'][0], ps['datarange'][1])
            rgb_data = np.linspace(ps['datarange'][0], ps['datarange'][1], rgb_values.shape[0])[:, np.newaxis]
            t2LUT.RGBPoints = np.hstack((rgb_data, rgb_values)).flatten()
        else:
            t2LUT.ApplyPreset(ps['colormap'], True)
    else:
        if ps['colormap_categories']:

            n_categories = int(len(ps['colormap']) / 4)

            # Properties modified on hotspotsLUT
            t2LUT.InterpretValuesAsCategories = 1
            t2LUT.AnnotationsInitialized = 1

            # Properties modified on hotspotsLUT
            t2LUT.Annotations = list(np.array([[str(i), str(i)] for i in range(n_categories)]).flatten())
            t2LUT.IndexedOpacities = [1.0] * n_categories

            # here now we need only the RGB values
            t2LUT.IndexedColors = np.reshape(ps['colormap'], (n_categories, 4))[:, 1:].flatten()
        else:

            t2LUT.RGBPoints = ps['colormap']

    # change representation type
    if ps['edges']:
        t2Display.SetRepresentationType('Surface With Edges')

    # get color legend/bar for eLUT in view renderView
    t2LUTColorBar = paraview.simple.GetScalarBar(pLUT, renderView)
    t2LUTColorBar.WindowLocation = 'LowerCenter'
    t2LUTColorBar.Orientation = ps['colorbar_orientation']

    # setting the position does not work anymore for some reason (Paraview 5.8)
    if ps['colorbar_position']:
        t2LUTColorBar.Position = ps['colorbar_position']
    else:
        t2LUTColorBar.Position = [0.847321428571429, 0.292476354256234]

    t2LUTColorBar.AutoOrient = 1
    t2LUTColorBar.Title = ps['colorbar_label']
    t2LUTColorBar.ComponentTitle = ''
    t2LUTColorBar.TitleJustification = 'Centered'
    t2LUTColorBar.TitleColor = ps['colorbar_labelcolor']
    t2LUTColorBar.TitleOpacity = 1.0
    t2LUTColorBar.TitleFontFamily = ps['colorbar_font']
    t2LUTColorBar.TitleBold = 0
    t2LUTColorBar.TitleItalic = 0
    t2LUTColorBar.TitleShadow = 0
    t2LUTColorBar.TitleFontSize = ps['colorbar_titlefontsize']
    t2LUTColorBar.LabelColor = ps['colorbar_labelcolor']
    t2LUTColorBar.LabelOpacity = 1.0
    t2LUTColorBar.LabelFontFamily = ps['colorbar_font']
    t2LUTColorBar.LabelBold = 0
    t2LUTColorBar.LabelItalic = 0
    t2LUTColorBar.LabelShadow = 0
    t2LUTColorBar.LabelFontSize = ps['colorbar_labelfontsize']
    t2LUTColorBar.AutomaticLabelFormat = 0
    t2LUTColorBar.LabelFormat = ps['colorbar_labelformat']
    # t2LUTColorBar.NumberOfLabels = ps['colorbar_numberoflabels']  # not in v5.8 anymore
    t2LUTColorBar.DrawTickMarks = 1
    # t2LUTColorBar.DrawSubTickMarks = 1  # not in v5.8 anymore
    t2LUTColorBar.DrawTickLabels = 1
    t2LUTColorBar.AddRangeLabels = 1
    t2LUTColorBar.RangeLabelFormat = ps['colorbar_labelformat']
    t2LUTColorBar.DrawAnnotations = 1
    t2LUTColorBar.AddRangeAnnotations = 0
    t2LUTColorBar.AutomaticAnnotations = 0
    t2LUTColorBar.DrawNanAnnotation = 0
    t2LUTColorBar.NanAnnotation = 'NaN'
    t2LUTColorBar.TextPosition = 'Ticks right/top, annotations left/bottom'
    # t2LUTColorBar.AspectRatio = ps['colorbar_aspectratio']  # paraview.NotSupportedException: 'AspectRatio' is obsolete as of ParaView 5.4. Use the 'ScalarBarThickness' property to set the width instead.

    # Rescale colorbar transfer function
    if ps['datarange']:
        t2LUT.RescaleTransferFunction(float(ps['datarange'][0]), ps['datarange'][1])
        t2PWF.RescaleTransferFunction(float(ps['datarange'][0]), ps['datarange'][1])
    else:
        t2Display.RescaleTransferFunctionToDataRange(False, True)

    # t2Display.RescaleTransferFunctionToDataRange(True)

    # turn off orientation axes
    if not(ps['axes']):
        renderView.OrientationAxesVisibility = 0

    # =============================================================================
    # create and set up vector plots
    # =============================================================================
    if ps['vlabels']:
        vec = [0] * len(ps['vlabels'])
        vecDisplay = [0] * len(ps['vlabels'])

        if ps['vcolor'].ndim == 1:
            ps['vcolor'] = ps['vcolor'][np.newaxis, :]

        N_vecs = len(ps['vlabels'])

        # copy vector colors if only one color is specified
        if len(ps['vlabels']) < ps['vcolor'].shape[0]:
            vcolor = np.tile(ps['vcolor'], (N_vecs, 1))

        # copy vector scale mode if only one scale mode is specified
        if len(ps['vscale_mode']) < ps['vcolor'].shape[0]:
            vscale_mode = [ps['vscale_mode'] for i in range(N_vecs)]

        # copy vector scale mode if only one scale mode is specified
        vscales = np.array(ps['vscales'])

        if ps['vscales'].size < ps['vcolor'].shape[0]:
            vscales = np.tile(ps['vscales'], (N_vecs, 1))

        # create a new 'Glyph' (vector plot)
        for i in range(N_vecs):
            vec[i] = paraview.simple.Glyph(Input=t2, GlyphType='Arrow')
            vec[i].Scalars = ['POINTS', 'None']
            vec[i].Vectors = ['CELLS', ps['vlabels'][i]]
            vec[i].Orient = 1
            vec[i].ScaleMode = ps['vscale_mode'][i]  # 'off', 'vector', 'vector_components'
            vec[i].ScaleFactor = ps['vscales'][i]
            vec[i].GlyphMode = list(ps['vector_mode'].keys())[0]
            if list(ps['vector_mode'].keys())[0] == 'Every Nth Point':
                vec[i].Stride = ps['vector_mode'][list(ps['vector_mode'].keys())[0]]
            vec[i].MaximumNumberOfSamplePoints = 5000
            vec[i].Seed = 10339
            vec[i].GlyphTransform = 'Transform2'

            # init the 'Arrow' selected for 'GlyphType'
            vec[i].GlyphType.TipResolution = 6
            vec[i].GlyphType.TipRadius = 0.1
            vec[i].GlyphType.TipLength = 0.35
            vec[i].GlyphType.ShaftResolution = 6
            vec[i].GlyphType.ShaftRadius = 0.03
            vec[i].GlyphType.Invert = 0

            # init the 'Transform2' selected for 'GlyphTransform'
            vec[i].GlyphTransform.Translate = [0.0, 0.0, 0.0]
            vec[i].GlyphTransform.Rotate = [0.0, 0.0, 0.0]
            vec[i].GlyphTransform.Scale = [1.0, 1.0, 1.0]

            # show data in view
            vecDisplay[i] = paraview.simple.Show(vec[i], renderView)

            # trace defaults for the display properties.
            vecDisplay[i].Representation = 'Surface'
            vecDisplay[i].AmbientColor = [1.0, 1.0, 1.0]
            vecDisplay[i].ColorArrayName = [None, '']
            vecDisplay[i].DiffuseColor = [1.0, 1.0, 1.0]
            vecDisplay[i].LookupTable = None
            vecDisplay[i].MapScalars = 1
            vecDisplay[i].InterpolateScalarsBeforeMapping = 1
            vecDisplay[i].Opacity = 1.0
            vecDisplay[i].PointSize = 2.0
            vecDisplay[i].LineWidth = 1.0
            vecDisplay[i].Interpolation = 'Gouraud'
            vecDisplay[i].Specular = 0.0
            vecDisplay[i].SpecularColor = [1.0, 1.0, 1.0]
            vecDisplay[i].SpecularPower = 100.0
            vecDisplay[i].Ambient = 0.0
            vecDisplay[i].Diffuse = 1.0
            vecDisplay[i].EdgeColor = [0.0, 0.0, 0.5]
            vecDisplay[i].BackfaceRepresentation = 'Follow Frontface'
            vecDisplay[i].BackfaceAmbientColor = [1.0, 1.0, 1.0]
            vecDisplay[i].BackfaceDiffuseColor = [1.0, 1.0, 1.0]
            vecDisplay[i].BackfaceOpacity = 1.0
            vecDisplay[i].Position = [0.0, 0.0, 0.0]
            vecDisplay[i].Scale = [1.0, 1.0, 1.0]
            vecDisplay[i].Orientation = [0.0, 0.0, 0.0]
            vecDisplay[i].Origin = [0.0, 0.0, 0.0]
            vecDisplay[i].Pickable = 1
            vecDisplay[i].Texture = None
            vecDisplay[i].Triangulate = 0
            vecDisplay[i].NonlinearSubdivisionLevel = 1
            vecDisplay[i].OSPRayUseScaleArray = 0
            vecDisplay[i].OSPRayScaleArray = quantity
            vecDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
            vecDisplay[i].GlyphType = 'Arrow'
            vecDisplay[i].SelectionCellLabelBold = 0
            vecDisplay[i].SelectionCellLabelColor = [0.0, 1.0, 0.0]
            vecDisplay[i].SelectionCellLabelFontFamily = 'Arial'
            vecDisplay[i].SelectionCellLabelFontSize = 18
            vecDisplay[i].SelectionCellLabelItalic = 0
            vecDisplay[i].SelectionCellLabelJustification = 'Left'
            vecDisplay[i].SelectionCellLabelOpacity = 1.0
            vecDisplay[i].SelectionCellLabelShadow = 0
            vecDisplay[i].SelectionPointLabelBold = 0
            vecDisplay[i].SelectionPointLabelColor = [1.0, 1.0, 0.0]
            vecDisplay[i].SelectionPointLabelFontFamily = 'Arial'
            vecDisplay[i].SelectionPointLabelFontSize = 18
            vecDisplay[i].SelectionPointLabelItalic = 0
            vecDisplay[i].SelectionPointLabelJustification = 'Left'
            vecDisplay[i].SelectionPointLabelOpacity = 1.0
            vecDisplay[i].SelectionPointLabelShadow = 0
            vecDisplay[i].GaussianRadius = 0.0
            vecDisplay[i].ShaderPreset = 'Sphere'
            vecDisplay[i].Emissive = 0
            vecDisplay[i].ScaleByArray = 0
            vecDisplay[i].SetScaleArray = [None, '']
            vecDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
            vecDisplay[i].OpacityByArray = 0
            vecDisplay[i].OpacityArray = [None, '']
            vecDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'

            # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
            vecDisplay[i].OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'Arrow' selected for 'GlyphType'
            vecDisplay[i].GlyphType.TipResolution = 6
            vecDisplay[i].GlyphType.TipRadius = 0.1
            vecDisplay[i].GlyphType.TipLength = 0.35
            vecDisplay[i].GlyphType.ShaftResolution = 6
            vecDisplay[i].GlyphType.ShaftRadius = 0.03
            vecDisplay[i].GlyphType.Invert = 0

            # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
            vecDisplay[i].ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
            vecDisplay[i].OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # change solid color using normalized EGB code (0...1)
            vecDisplay[i].DiffuseColor = ps['vcolor'][i, :]

    # =============================================================================
    # coil
    # =============================================================================
    source = GetActiveSource()
    source.UpdatePipeline()
    cdi = source.GetDataInformation().GetCompositeDataInformation()
    n_blocks = cdi.GetNumberOfChildren()
    block_names = [cdi.GetName(i) for i in range(n_blocks)]

    if 'coil' in block_names and ps['show_coil']:
        plot_coil = True
    else:
        plot_coil = False

    if plot_coil:

        # create a new 'Threshold'
        coilthreshold = paraview.simple.Threshold(Input=p)
        coilthreshold.Scalars = ['CELLS', 'dipole_mag']
        # threshold1.ThresholdRange = [1.1648167371749878, 8.777523040771484]
        coilthreshold.AllScalars = 1
        coilthreshold.UseContinuousCellRange = 0

        # show data in view
        coilthresholdDisplay = Show(coilthreshold, renderView)
        # trace defaults for the display properties.
        coilthresholdDisplay.Representation = 'Surface'
        coilthresholdDisplay.AmbientColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.ColorArrayName = ['CELLS', 'dipole_mag']
        coilthresholdDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        # coilthresholdDisplay.LookupTable = dipolemagLUT
        coilthresholdDisplay.MapScalars = 1
        coilthresholdDisplay.InterpolateScalarsBeforeMapping = 1
        coilthresholdDisplay.Opacity = 1.0
        coilthresholdDisplay.PointSize = 2.0
        coilthresholdDisplay.LineWidth = 1.0
        coilthresholdDisplay.Interpolation = 'Gouraud'
        coilthresholdDisplay.Specular = 0.0
        coilthresholdDisplay.SpecularColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.SpecularPower = 100.0
        coilthresholdDisplay.Ambient = 0.0
        coilthresholdDisplay.Diffuse = 1.0
        coilthresholdDisplay.EdgeColor = [0.0, 0.0, 0.5]
        coilthresholdDisplay.BackfaceRepresentation = 'Follow Frontface'
        coilthresholdDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.BackfaceOpacity = 1.0
        coilthresholdDisplay.Position = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Scale = [1.0, 1.0, 1.0]
        coilthresholdDisplay.Orientation = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Origin = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Pickable = 1
        coilthresholdDisplay.Texture = None
        coilthresholdDisplay.Triangulate = 0
        coilthresholdDisplay.NonlinearSubdivisionLevel = 1
        coilthresholdDisplay.OSPRayUseScaleArray = 0
        coilthresholdDisplay.OSPRayScaleArray = 'dipole_mag'
        coilthresholdDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilthresholdDisplay.GlyphType = 'Arrow'
        coilthresholdDisplay.SelectionCellLabelBold = 0
        coilthresholdDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        coilthresholdDisplay.SelectionCellLabelFontFamily = 'Arial'
        coilthresholdDisplay.SelectionCellLabelFontSize = 18
        coilthresholdDisplay.SelectionCellLabelItalic = 0
        coilthresholdDisplay.SelectionCellLabelJustification = 'Left'
        coilthresholdDisplay.SelectionCellLabelOpacity = 1.0
        coilthresholdDisplay.SelectionCellLabelShadow = 0
        coilthresholdDisplay.SelectionPointLabelBold = 0
        coilthresholdDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        coilthresholdDisplay.SelectionPointLabelFontFamily = 'Arial'
        coilthresholdDisplay.SelectionPointLabelFontSize = 18
        coilthresholdDisplay.SelectionPointLabelItalic = 0
        coilthresholdDisplay.SelectionPointLabelJustification = 'Left'
        coilthresholdDisplay.SelectionPointLabelOpacity = 1.0
        coilthresholdDisplay.SelectionPointLabelShadow = 0
        coilthresholdDisplay.ScalarOpacityUnitDistance = 10.18430143021554
        coilthresholdDisplay.SelectMapper = 'Projected tetra'
        coilthresholdDisplay.GaussianRadius = 0.0
        coilthresholdDisplay.ShaderPreset = 'Sphere'
        coilthresholdDisplay.Emissive = 0
        coilthresholdDisplay.ScaleByArray = 0
        coilthresholdDisplay.SetScaleArray = [None, '']
        coilthresholdDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilthresholdDisplay.OpacityByArray = 0
        coilthresholdDisplay.OpacityArray = [None, '']
        coilthresholdDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        coilthresholdDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        coilthresholdDisplay.GlyphType.TipResolution = 6
        coilthresholdDisplay.GlyphType.TipRadius = 0.1
        coilthresholdDisplay.GlyphType.TipLength = 0.35
        coilthresholdDisplay.GlyphType.ShaftResolution = 6
        coilthresholdDisplay.GlyphType.ShaftRadius = 0.03
        coilthresholdDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        coilthresholdDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        coilthresholdDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # show color bar/color legend
        coilthresholdDisplay.SetScalarBarVisibility(renderView, False)

        # create a new 'Glyph'
        coilGlyph = paraview.simple.Glyph(Input=coilthreshold, GlyphType='Arrow')
        coilGlyph.Scalars = ['CELLS', 'dipole_mag']
        coilGlyph.Vectors = ['POINTS', 'None']
        coilGlyph.Orient = 1
        coilGlyph.GlyphMode = 'All Points'
        coilGlyph.MaximumNumberOfSamplePoints = 5000
        coilGlyph.Seed = 10339
        coilGlyph.Stride = 1
        coilGlyph.GlyphTransform = 'Transform2'
        coilGlyph.GlyphType = 'Sphere'

        # set dipole scaling and size
        if ps['coil_dipole_scaling'][0] == 'scaled':
            coilGlyph.Scalars = ['POINTS', 'magnitude']
            coilGlyph.ScaleMode = 'scalar'
        else:
            coilGlyph.ScaleMode = 'off'

        coilGlyph.ScaleFactor = ps['coil_dipole_scaling'][1]

        # init the 'Transform2' selected for 'GlyphTransform'
        coilGlyph.GlyphTransform.Translate = [0.0, 0.0, 0.0]
        coilGlyph.GlyphTransform.Rotate = [0.0, 0.0, 0.0]
        coilGlyph.GlyphTransform.Scale = [1.0, 1.0, 1.0]

        # get color transfer function/color map for 'dipolemag'
        dipolemagLUT = GetColorTransferFunction('dipolemag')
        dipolemagLUT.LockDataRange = 0
        dipolemagLUT.InterpretValuesAsCategories = 0
        dipolemagLUT.ShowCategoricalColorsinDataRangeOnly = 0
        dipolemagLUT.RescaleOnVisibilityChange = 0
        dipolemagLUT.EnableOpacityMapping = 0
        dipolemagLUT.UseLogScale = 0
        dipolemagLUT.ColorSpace = 'Lab'
        dipolemagLUT.UseBelowRangeColor = 0
        dipolemagLUT.BelowRangeColor = [0.0, 0.0, 0.0]
        dipolemagLUT.UseAboveRangeColor = 0
        dipolemagLUT.AboveRangeColor = [1.0, 1.0, 1.0]
        dipolemagLUT.NanColor = ps['NanColor']
        dipolemagLUT.Discretize = 1
        dipolemagLUT.NumberOfTableValues = 256
        dipolemagLUT.ScalarRangeInitialized = 1.0
        dipolemagLUT.HSVWrap = 0
        dipolemagLUT.VectorComponent = 0
        dipolemagLUT.VectorMode = 'Magnitude'
        dipolemagLUT.AllowDuplicateScalars = 1
        dipolemagLUT.Annotations = []
        dipolemagLUT.ActiveAnnotatedValues = []
        dipolemagLUT.IndexedColors = []

        # show data in view
        coilGlyphDisplay = Show(coilGlyph, renderView)

        # trace defaults for the display properties.
        coilGlyphDisplay.Representation = 'Surface'
        coilGlyphDisplay.AmbientColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.ColorArrayName = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.LookupTable = dipolemagLUT
        coilGlyphDisplay.MapScalars = 1
        coilGlyphDisplay.InterpolateScalarsBeforeMapping = 1
        coilGlyphDisplay.Opacity = 1.0
        coilGlyphDisplay.PointSize = 2.0
        coilGlyphDisplay.LineWidth = 1.0
        coilGlyphDisplay.Interpolation = 'Gouraud'
        coilGlyphDisplay.Specular = 0.0
        coilGlyphDisplay.SpecularColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.SpecularPower = 100.0
        coilGlyphDisplay.Ambient = 0.0
        coilGlyphDisplay.Diffuse = 1.0
        coilGlyphDisplay.EdgeColor = [0.0, 0.0, 0.5]
        coilGlyphDisplay.BackfaceRepresentation = 'Follow Frontface'
        coilGlyphDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.BackfaceOpacity = 1.0
        coilGlyphDisplay.Position = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Scale = [1.0, 1.0, 1.0]
        coilGlyphDisplay.Orientation = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Origin = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Pickable = 1
        coilGlyphDisplay.Texture = None
        coilGlyphDisplay.Triangulate = 0
        coilGlyphDisplay.NonlinearSubdivisionLevel = 1
        coilGlyphDisplay.OSPRayUseScaleArray = 0
        coilGlyphDisplay.OSPRayScaleArray = 'dipole_mag'
        coilGlyphDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilGlyphDisplay.GlyphType = 'Arrow'
        coilGlyphDisplay.SelectionCellLabelBold = 0
        coilGlyphDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        coilGlyphDisplay.SelectionCellLabelFontFamily = 'Arial'
        coilGlyphDisplay.SelectionCellLabelFontSize = 18
        coilGlyphDisplay.SelectionCellLabelItalic = 0
        coilGlyphDisplay.SelectionCellLabelJustification = 'Left'
        coilGlyphDisplay.SelectionCellLabelOpacity = 1.0
        coilGlyphDisplay.SelectionCellLabelShadow = 0
        coilGlyphDisplay.SelectionPointLabelBold = 0
        coilGlyphDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        coilGlyphDisplay.SelectionPointLabelFontFamily = 'Arial'
        coilGlyphDisplay.SelectionPointLabelFontSize = 18
        coilGlyphDisplay.SelectionPointLabelItalic = 0
        coilGlyphDisplay.SelectionPointLabelJustification = 'Left'
        coilGlyphDisplay.SelectionPointLabelOpacity = 1.0
        coilGlyphDisplay.SelectionPointLabelShadow = 0
        coilGlyphDisplay.GaussianRadius = 0.0
        coilGlyphDisplay.ShaderPreset = 'Sphere'
        coilGlyphDisplay.Emissive = 0
        coilGlyphDisplay.ScaleByArray = 0
        coilGlyphDisplay.SetScaleArray = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilGlyphDisplay.OpacityByArray = 0
        coilGlyphDisplay.OpacityArray = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        coilGlyphDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        coilGlyphDisplay.GlyphType.TipResolution = 6
        coilGlyphDisplay.GlyphType.TipRadius = 0.1
        coilGlyphDisplay.GlyphType.TipLength = 0.35
        coilGlyphDisplay.GlyphType.ShaftResolution = 6
        coilGlyphDisplay.GlyphType.ShaftRadius = 0.03
        coilGlyphDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        coilGlyphDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        coilGlyphDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # show color bar/color legend
        coilGlyphDisplay.SetScalarBarVisibility(renderView, False)

        # set dipole color
        if isinstance(ps['coil_dipole_color'], (str,)):
            # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
            dipolemagLUT.ApplyPreset(ps['coil_dipole_color'], True)

        else:
            # change solid color
            coilGlyphDisplay.DiffuseColor = ps['coil_dipole_color']

        # =============================================================
        # set coil axes direction
        # =============================================================
        if ps['coil_axes']:
            import vtk.numpy_interface.dataset_adapter as dsa

            # read points out of dataset
            coilthreshold.UpdatePipeline()
            rawData = servermanager.Fetch(coilthreshold)
            data = dsa.WrapDataObject(rawData)
            points = np.array(data.Points.Arrays[2])

            # determine coil center
            coil_center = np.average(points, axis=0)

            # shift coil to center for SVD
            points = points - coil_center

            line = [0] * 3
            lineDisplay = [0] * 3
            line_color = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            U, s, V = np.linalg.svd(points, full_matrices=True)
            points_transform = np.dot(points, V.transpose())
            coil_dim = np.max(points_transform, axis=0) - np.min(points_transform, axis=0)

            for i in range(3):
                # create a new 'Line'
                line[i] = paraview.simple.Line()
                # Properties modified on line1
                line[i].Point1 = coil_center
                if ((i == 0) or (i == 1)):
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[i] / 2
                if i == 2:
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[0] / 2
                line[i].Resolution = 1000
                # set active source
                SetActiveSource(line[i])
                # show data in view
                lineDisplay[i] = Show(line[i], renderView)
                # trace defaults for the display properties.
                lineDisplay[i].ColorArrayName = [None, '']
                lineDisplay[i].OSPRayScaleArray = 'Texture Coordinates'
                lineDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
                lineDisplay[i].GlyphType = 'Sphere'
                lineDisplay[i].SetScaleArray = [None, '']
                lineDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].OpacityArray = [None, '']
                lineDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].ShaderPreset = 'Gaussian Blur (Default)'
                lineDisplay[i].DiffuseColor = line_color[i]
                lineDisplay[i].SetRepresentationType('3D Glyphs')
                lineDisplay[i].GlyphType.Radius = 1.0

    # set the background color
    renderView.Background = ps['background_color']

    # set image size
    renderView.ViewSize = ps['viewsize']  # [width, height]

    # save scene
    paraview.simple.SaveScreenshot(ps['fname_png'], magnification=ps['png_resolution'], quality=100, view=renderView)

    # crop surrounding of image
    crop_image(ps['fname_png'], ps['fname_png'])

    # delete temporary cropped .hdf5 data file and restore original file
    if data_cropped:
        shutil.move(os.path.splitext(fn_data_hdf5)[0] + '_backup.hdf5', fn_data_hdf5)

    # Reset Paraview session
    ResetSession()


def surface_vector_plot_vtu(ps):
    """ Generate plot with Paraview from data in .vtu file.

    Parameters
    ----------
    ps : dict
        Plot settings dict initialized with create_plot_settings_dict(plotfunction_type='surface_vector_plot_vtu')

    Returns
    -------
    <File> : .png file
        Generated plot
    """

    if ps['interpolate']:
        target = 'POINTS'
    else:
        target = 'CELLS'

    # add whitespace if colorbar label is not given (empty colorbar labels are plotted wrong)
    if ps['colorbar_label'] is None or ps['colorbar_label']=='':
        ps['colorbar_label'] = ' '

    # create a new 'XML Unstructured Grid Reader'
    p = paraview.simple.XMLUnstructuredGridReader(FileName=[ps['fname_in']])

    label_datasets = p.CellArrayStatus
    N_datasets = len(label_datasets)

    p.PointArrayStatus = []

    if len(ps['datarange']) == 1 and ps['datarange'][0] == None:
        datarange = [None, None]

    # get data ranges of included datasets
    if None in ps['datarange']:
        datarange_temp = servermanager.Fetch(p).GetCellData().GetArray(ps['quantity']).GetRange()
        if ps['datarange'][0] == None:
            ps['datarange'][0] = datarange_temp[0]
        if ps['datarange'][1] == None:
            ps['datarange'][1] = datarange_temp[1]

    # get active view
    renderView = GetActiveViewOrCreate('RenderView')

    # =============================================================================
    # plot curvature data as 'underlay' (if present)
    # =============================================================================
    if 'underlay' in label_datasets:
        # reload dataset to plot underlay data
        # create a new 'XML Unstructured Grid Reader'
        u = paraview.simple.XMLUnstructuredGridReader(FileName=[ps['fname_in']])
        u.PointArrayStatus = []
        renderView = GetActiveViewOrCreate('RenderView')

        # show data in view
        uDisplay = Show(u, renderView)
        # trace defaults for the display properties.
        uDisplay.Representation = 'Surface'
        uDisplay.AmbientColor = [1.0, 1.0, 1.0]
        uDisplay.ColorArrayName = [None, '']
        uDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        uDisplay.LookupTable = None
        uDisplay.MapScalars = 1
        uDisplay.InterpolateScalarsBeforeMapping = 1
        uDisplay.Opacity = 1.0
        uDisplay.PointSize = 2.0
        uDisplay.LineWidth = 1.0
        uDisplay.Interpolation = 'Gouraud'
        uDisplay.Specular = 0.0
        uDisplay.SpecularColor = [1.0, 1.0, 1.0]
        uDisplay.SpecularPower = 100.0
        uDisplay.Ambient = 0.0
        uDisplay.Diffuse = 1.0
        uDisplay.EdgeColor = [0.0, 0.0, 0.5]
        uDisplay.BackfaceRepresentation = 'Follow Frontface'
        uDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        uDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        uDisplay.BackfaceOpacity = 1.0
        uDisplay.Position = [0.0, 0.0, 0.0]
        uDisplay.Scale = [1.0, 1.0, 1.0]
        uDisplay.Orientation = [0.0, 0.0, 0.0]
        uDisplay.Origin = [0.0, 0.0, 0.0]
        uDisplay.Pickable = 1
        uDisplay.Texture = None
        uDisplay.Triangulate = 0
        uDisplay.NonlinearSubdivisionLevel = 1
        uDisplay.OSPRayUseScaleArray = 0
        uDisplay.OSPRayScaleArray = 'underlay'
        uDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        uDisplay.GlyphType = 'Arrow'
        uDisplay.SelectionCellLabelBold = 0
        uDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        uDisplay.SelectionCellLabelFontFamily = 'Arial'
        uDisplay.SelectionCellLabelFontSize = 18
        uDisplay.SelectionCellLabelItalic = 0
        uDisplay.SelectionCellLabelJustification = 'Left'
        uDisplay.SelectionCellLabelOpacity = 1.0
        uDisplay.SelectionCellLabelShadow = 0
        uDisplay.SelectionPointLabelBold = 0
        uDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        uDisplay.SelectionPointLabelFontFamily = 'Arial'
        uDisplay.SelectionPointLabelFontSize = 18
        uDisplay.SelectionPointLabelItalic = 0
        uDisplay.SelectionPointLabelJustification = 'Left'
        uDisplay.SelectionPointLabelOpacity = 1.0
        uDisplay.SelectionPointLabelShadow = 0
        uDisplay.ScalarOpacityUnitDistance = 5.089405629151854
        uDisplay.SelectMapper = 'Projected tetra'
        uDisplay.GaussianRadius = 0.0
        uDisplay.ShaderPreset = 'Sphere'
        uDisplay.Emissive = 0
        uDisplay.ScaleByArray = 0
        uDisplay.SetScaleArray = [None, '']
        uDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        uDisplay.OpacityByArray = 0
        uDisplay.OpacityArray = [None, '']
        uDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        uDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        uDisplay.GlyphType.TipResolution = 6
        uDisplay.GlyphType.TipRadius = 0.1
        uDisplay.GlyphType.TipLength = 0.35
        uDisplay.GlyphType.ShaftResolution = 6
        uDisplay.GlyphType.ShaftRadius = 0.03
        uDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        uDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        uDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # reset view to fit data
        renderView.ResetCamera()

        # set scalar coloring
        ColorBy(uDisplay, ('CELLS', 'underlay'))

        # rescale color and/or opacity maps used to include current data range
        uDisplay.RescaleTransferFunctionToDataRange(True)

        # show color bar/color legend
        uDisplay.SetScalarBarVisibility(renderView, True)

        # get color transfer function/color map for 'underlay'
        uLUT = GetColorTransferFunction('underlay')
        uLUT.ApplyPreset('X Ray', True)
        # uLUT.LockDataRange = 0  # not in v5.8 anymore
        uLUT.InterpretValuesAsCategories = 0
        uLUT.ShowCategoricalColorsinDataRangeOnly = 0
        uLUT.RescaleOnVisibilityChange = 0
        uLUT.EnableOpacityMapping = 0
        uLUT.UseLogScale = 0
        uLUT.ColorSpace = 'RGB'
        uLUT.UseBelowRangeColor = 0
        uLUT.BelowRangeColor = [0.0, 0.0, 0.0]
        uLUT.UseAboveRangeColor = 0
        uLUT.AboveRangeColor = [1.0, 1.0, 1.0]
        uLUT.NanColor = ps['NanColor']
        uLUT.Discretize = 1
        uLUT.NumberOfTableValues = 256
        uLUT.ScalarRangeInitialized = 1.0
        uLUT.HSVWrap = 0
        uLUT.VectorComponent = 0
        uLUT.VectorMode = 'Magnitude'
        uLUT.AllowDuplicateScalars = 1
        uLUT.Annotations = []
        uLUT.ActiveAnnotatedValues = []
        uLUT.IndexedColors = []

        # get opacity transfer function/opacity map for 'curv'
        uPWF = GetOpacityTransferFunction('underlay')
        uPWF.AllowDuplicateScalars = 1
        uPWF.ScalarRangeInitialized = 1

        # hide color bar/color legend
        uDisplay.SetScalarBarVisibility(renderView, False)

    # =============================================================================
    # plot main results
    # =============================================================================
    # create a new 'Cell Data to Point Data' if interpolate is selected or an underlay is present in order to enable
    # an opacity transfer function of the overlay (main) data
    if ps['interpolate'] or ('underlay' in label_datasets):
        Hide(p, renderView)
        p1 = paraview.simple.CellDatatoPointData(Input=p)
        p1.PassCellData = 0
        p1.PieceInvariant = 0
        pDisplay = Show(p1, renderView)
    else:
        pDisplay = Show(p, renderView)

    # trace defaults for the display properties.
    pDisplay.Representation = 'Surface'
    pDisplay.AmbientColor = [1.0, 1.0, 1.0]
    pDisplay.ColorArrayName = [None, '']
    pDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.LookupTable = None
    pDisplay.MapScalars = 1
    pDisplay.InterpolateScalarsBeforeMapping = 1
    pDisplay.Opacity = 1.0
    pDisplay.PointSize = 2.0
    pDisplay.LineWidth = 1.0
    pDisplay.Interpolation = 'Gouraud'
    pDisplay.Specular = 0.0
    pDisplay.SpecularColor = [1.0, 1.0, 1.0]
    pDisplay.SpecularPower = 100.0
    pDisplay.Ambient = 0.0
    pDisplay.Diffuse = 1.0
    pDisplay.EdgeColor = [0.0, 0.0, 0.5]
    pDisplay.BackfaceRepresentation = 'Follow Frontface'
    pDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceOpacity = 1.0
    pDisplay.Position = [0.0, 0.0, 0.0]
    pDisplay.Scale = [1.0, 1.0, 1.0]
    pDisplay.Orientation = [0.0, 0.0, 0.0]
    pDisplay.Origin = [0.0, 0.0, 0.0]
    pDisplay.Pickable = 1
    pDisplay.Texture = None
    pDisplay.Triangulate = 0
    pDisplay.NonlinearSubdivisionLevel = 1
    pDisplay.OSPRayUseScaleArray = 0
    pDisplay.OSPRayScaleArray = ps['quantity']
    pDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    pDisplay.GlyphType = 'Arrow'
    pDisplay.SelectionCellLabelBold = 0
    pDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    pDisplay.SelectionCellLabelFontFamily = 'Arial'
    pDisplay.SelectionCellLabelFontSize = 18
    pDisplay.SelectionCellLabelItalic = 0
    pDisplay.SelectionCellLabelJustification = 'Left'
    pDisplay.SelectionCellLabelOpacity = 1.0
    pDisplay.SelectionCellLabelShadow = 0
    pDisplay.SelectionPointLabelBold = 0
    pDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    pDisplay.SelectionPointLabelFontFamily = 'Arial'
    pDisplay.SelectionPointLabelFontSize = 18
    pDisplay.SelectionPointLabelItalic = 0
    pDisplay.SelectionPointLabelJustification = 'Left'
    pDisplay.SelectionPointLabelOpacity = 1.0
    pDisplay.SelectionPointLabelShadow = 0
    pDisplay.ScalarOpacityUnitDistance = 1.7832435554535888
    pDisplay.SelectMapper = 'Projected tetra'
    pDisplay.GaussianRadius = 0.0
    pDisplay.ShaderPreset = 'Sphere'
    pDisplay.Emissive = 0
    pDisplay.ScaleByArray = 0
    pDisplay.SetScaleArray = [None, '']
    pDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    pDisplay.OpacityByArray = 0
    pDisplay.OpacityArray = [None, '']  # ???
    pDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    pDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    pDisplay.GlyphType.TipResolution = 6
    pDisplay.GlyphType.TipRadius = 0.1
    pDisplay.GlyphType.TipLength = 0.35
    pDisplay.GlyphType.ShaftResolution = 6
    pDisplay.GlyphType.ShaftRadius = 0.03
    pDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    pDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    pDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView.ResetCamera()

    # camera placement for renderView
    if len(ps['view']) == 4:
        renderView.CameraPosition = ps['view'][0]
        renderView.CameraFocalPoint = ps['view'][1]
        renderView.CameraViewUp = ps['view'][2]
        renderView.CameraParallelScale = ps['view'][3][0]
    else:
        renderView.ResetCamera()

    # set coloring of surface
    ColorBy(pDisplay, (target, ps['quantity']))

    # rescale color and/or opacity maps used to include current data range
    pDisplay.RescaleTransferFunctionToDataRange(False)

    # show color bar/color legend
    pDisplay.SetScalarBarVisibility(renderView, True)

    # get color transfer function/color map for 'quantity'
    eLUT = GetColorTransferFunction(ps['quantity'])
    # eLUT.LockDataRange = 0  # not in v5.8 anymore
    eLUT.InterpretValuesAsCategories = 0
    eLUT.ShowCategoricalColorsinDataRangeOnly = 0
    eLUT.RescaleOnVisibilityChange = 0
    # if 'underlay' in label_datasets:
    #     eLUT.EnableOpacityMapping = 1
    # else:
    #     eLUT.EnableOpacityMapping = 0
    eLUT.UseLogScale = 0
    if ps['interpolate']:
        eLUT.ColorSpace = 'RGB'
    else:
        eLUT.ColorSpace = 'RGB' #'Diverging'
    eLUT.UseBelowRangeColor = 0
    eLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    eLUT.UseAboveRangeColor = 0
    eLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    eLUT.NanColor = ps['NanColor']
    eLUT.Discretize = 1
    eLUT.NumberOfTableValues = 256
    eLUT.ScalarRangeInitialized = 1.0
    eLUT.HSVWrap = 0
    eLUT.VectorComponent = 0
    eLUT.VectorMode = 'Magnitude'
    eLUT.AllowDuplicateScalars = 1
    eLUT.Annotations = []
    eLUT.ActiveAnnotatedValues = []
    eLUT.IndexedColors = []

    # set opacity transfer function/opacity map 'quantity'
    ePWF = GetOpacityTransferFunction(ps['quantity'])
    if not (ps['opacitymap'] == []):
        eLUT.EnableOpacityMapping = 1
        ePWF.Points = ps['opacitymap']
    ePWF.AllowDuplicateScalars = 1
    ePWF.ScalarRangeInitialized = 1

    # =============================================================================
    # set colormap for magnitude plot
    # =============================================================================
    if type(ps['colormap']) is str:
        colormap_presets = {'Cool to Warm',
                            'Cool to Warm (Extended)',
                            'Blue to Red Rainbow',
                            'X Ray',
                            'Grayscale',
                            'jet',
                            'hsv',
                            'erdc_iceFire_L',
                            'Plasma (matplotlib)',
                            'Viridis (matplotlib)',
                            'gray_Matlab',
                            'Spectral_lowBlue',
                            'BuRd',
                            'Rainbow Blended White',
                            'b2rcw'}

        # set colorbar to 'jet' if not specified in presets
        if not (ps['colormap'] in colormap_presets):
            print((
                'Changing colormap to \'jet\' since user specified colormap \'{}\' is not part of the included presets ...').format(
                ps['colormap']))
            colormap = 'jet'

        if ps['colormap'] == 'b2rcw':
            rgb_values = b2rcw(ps['datarange'][0],ps['datarange'][1])
            rgb_data = np.linspace(ps['datarange'][0],ps['datarange'][1], rgb_values.shape[0])[:,np.newaxis]
            eLUT.RGBPoints = np.hstack((rgb_data,rgb_values)).flatten()
        else:
            eLUT.ApplyPreset(ps['colormap'], True)
    else:
        eLUT.RGBPoints = ps['colormap']

    # change representation type
    if ps['edges']:
        pDisplay.SetRepresentationType('Surface With Edges')

    # get color legend/bar for eLUT in view renderView
    eLUTColorBar = paraview.simple.GetScalarBar(eLUT, renderView)
    if ps['colorbar_position']:
        eLUTColorBar.Position = ps['colorbar_position']
    else:
        eLUTColorBar.Position = [0.847321428571429, 0.292476354256234]
    # eLUTColorBar.Position2 = [0.12, 0.43]  #'Position2' is obsolete as of ParaView 5.4. Use the 'ScalarBarLength' property to set the length instead.
    eLUTColorBar.AutoOrient = 1
    eLUTColorBar.Orientation = ps['colorbar_orientation']
    eLUTColorBar.Title = ps['colorbar_label']
    eLUTColorBar.ComponentTitle = ''
    eLUTColorBar.TitleJustification = 'Centered'
    eLUTColorBar.TitleColor = ps['colorbar_labelcolor']
    eLUTColorBar.TitleOpacity = 1.0
    eLUTColorBar.TitleFontFamily = ps['colorbar_font']
    eLUTColorBar.TitleBold = 0
    eLUTColorBar.TitleItalic = 0
    eLUTColorBar.TitleShadow = 0
    eLUTColorBar.TitleFontSize = ps['colorbar_titlefontsize']
    eLUTColorBar.LabelColor = ps['colorbar_labelcolor']
    eLUTColorBar.LabelOpacity = 1.0
    eLUTColorBar.LabelFontFamily = ps['colorbar_font']
    eLUTColorBar.LabelBold = 0
    eLUTColorBar.LabelItalic = 0
    eLUTColorBar.LabelShadow = 0
    eLUTColorBar.LabelFontSize = ps['colorbar_labelfontsize']
    eLUTColorBar.AutomaticLabelFormat = 0
    eLUTColorBar.LabelFormat = ps['colorbar_labelformat']
    # eLUTColorBar.NumberOfLabels = ps['colorbar_numberoflabels']  # not in v5.8 anymore
    eLUTColorBar.DrawTickMarks = 1
    # eLUTColorBar.DrawSubTickMarks = 1  # not in v5.8 anymore
    eLUTColorBar.DrawTickLabels = 1
    eLUTColorBar.AddRangeLabels = 1
    eLUTColorBar.RangeLabelFormat = ps['colorbar_labelformat']
    eLUTColorBar.DrawAnnotations = 1
    eLUTColorBar.AddRangeAnnotations = 0
    eLUTColorBar.AutomaticAnnotations = 0
    eLUTColorBar.DrawNanAnnotation = 0
    eLUTColorBar.NanAnnotation = 'NaN'
    eLUTColorBar.TextPosition = 'Ticks right/top, annotations left/bottom'
    # eLUTColorBar.AspectRatio = ps['colorbar_aspectratio']  # paraview.NotSupportedException: 'AspectRatio' is obsolete as of ParaView 5.4. Use the 'ScalarBarThickness' property to set the width instead.

    # Rescale colorbar transfer function
    if ps['datarange']:
        eLUT.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])
        ePWF.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])
    else:
        pDisplay.RescaleTransferFunctionToDataRange(False)

    # turn off orientation axes
    if not (ps['axes']):
        renderView.OrientationAxesVisibility = 0
    # =============================================================================
    # create and set up vector plots
    # =============================================================================
    vec = [0] * len(ps['vlabels'])
    vecDisplay = [0] * len(ps['vlabels'])

    if ps['vcolor'].ndim == 1:
        ps['vcolor'] = ps['vcolor'][np.newaxis, :]

    N_vecs = len(ps['vlabels'])

    # copy vector colors if only one color is specified
    if len(ps['vlabels']) < ps['vcolor'].shape[0]:
        vcolor = np.tile(ps['vcolor'], (N_vecs, 1))

    # copy vector scale mode if only one scale mode is specified
    if len(ps['vscale_mode']) < ps['vcolor'].shape[0]:
        vscale_mode = [ps['vscale_mode'] for i in range(N_vecs)]

    # copy vector scale mode if only one scale mode is specified
    vscales = np.array(ps['vscales'])

    if ps['vscales'].size < ps['vcolor'].shape[0]:
        vscales = np.tile(ps['vscales'], (N_vecs, 1))

    # create a new 'Glyph' (vector plot)
    for i in range(N_vecs):
        vec[i] = paraview.simple.Glyph(Input=p, GlyphType='Arrow')
        vec[i].Scalars = ['POINTS', 'None']
        vec[i].Vectors = ['POINTS', 'None']
        vec[i].Orient = 1
        vec[i].ScaleMode = ps['vscale_mode'][i]  # 'off', 'vector', 'vector_components'
        vec[i].ScaleFactor = ps['vscales'][i]
        vec[i].GlyphMode = list(ps['vector_mode'].keys())[0]
        if list(ps['vector_mode'].keys())[0] == 'Every Nth Point':
            vec[i].Stride = ps['vector_mode'][list(ps['vector_mode'].keys())[0]]
        vec[i].MaximumNumberOfSamplePoints = 5000
        vec[i].Seed = 10339
        vec[i].GlyphTransform = 'Transform2'

        # init the 'Arrow' selected for 'GlyphType'
        vec[i].GlyphType.TipResolution = 6
        vec[i].GlyphType.TipRadius = 0.1
        vec[i].GlyphType.TipLength = 0.35
        vec[i].GlyphType.ShaftResolution = 6
        vec[i].GlyphType.ShaftRadius = 0.03
        vec[i].GlyphType.Invert = 0

        # init the 'Transform2' selected for 'GlyphTransform'
        vec[i].GlyphTransform.Translate = [0.0, 0.0, 0.0]
        vec[i].GlyphTransform.Rotate = [0.0, 0.0, 0.0]
        vec[i].GlyphTransform.Scale = [1.0, 1.0, 1.0]

        # Properties modified on vec1
        vec[i].Vectors = ['CELLS', ps['vlabels'][i]]

        # show data in view
        vecDisplay[i] = paraview.simple.Show(vec[i], renderView)

        # trace defaults for the display properties.
        vecDisplay[i].Representation = 'Surface'
        vecDisplay[i].AmbientColor = [1.0, 1.0, 1.0]
        vecDisplay[i].ColorArrayName = [None, '']
        vecDisplay[i].DiffuseColor = [1.0, 1.0, 1.0]
        vecDisplay[i].LookupTable = None
        vecDisplay[i].MapScalars = 1
        vecDisplay[i].InterpolateScalarsBeforeMapping = 1
        vecDisplay[i].Opacity = 1.0
        vecDisplay[i].PointSize = 2.0
        vecDisplay[i].LineWidth = 1.0
        vecDisplay[i].Interpolation = 'Gouraud'
        vecDisplay[i].Specular = 0.0
        vecDisplay[i].SpecularColor = [1.0, 1.0, 1.0]
        vecDisplay[i].SpecularPower = 100.0
        vecDisplay[i].Ambient = 0.0
        vecDisplay[i].Diffuse = 1.0
        vecDisplay[i].EdgeColor = [0.0, 0.0, 0.5]
        vecDisplay[i].BackfaceRepresentation = 'Follow Frontface'
        vecDisplay[i].BackfaceAmbientColor = [1.0, 1.0, 1.0]
        vecDisplay[i].BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        vecDisplay[i].BackfaceOpacity = 1.0
        vecDisplay[i].Position = [0.0, 0.0, 0.0]
        vecDisplay[i].Scale = [1.0, 1.0, 1.0]
        vecDisplay[i].Orientation = [0.0, 0.0, 0.0]
        vecDisplay[i].Origin = [0.0, 0.0, 0.0]
        vecDisplay[i].Pickable = 1
        vecDisplay[i].Texture = None
        vecDisplay[i].Triangulate = 0
        vecDisplay[i].NonlinearSubdivisionLevel = 1
        vecDisplay[i].OSPRayUseScaleArray = 0
        vecDisplay[i].OSPRayScaleArray = ps['quantity']
        vecDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
        vecDisplay[i].GlyphType = 'Arrow'
        vecDisplay[i].SelectionCellLabelBold = 0
        vecDisplay[i].SelectionCellLabelColor = [0.0, 1.0, 0.0]
        vecDisplay[i].SelectionCellLabelFontFamily = ps['colorbar_font']
        vecDisplay[i].SelectionCellLabelFontSize = 18
        vecDisplay[i].SelectionCellLabelItalic = 0
        vecDisplay[i].SelectionCellLabelJustification = 'Left'
        vecDisplay[i].SelectionCellLabelOpacity = 1.0
        vecDisplay[i].SelectionCellLabelShadow = 0
        vecDisplay[i].SelectionPointLabelBold = 0
        vecDisplay[i].SelectionPointLabelColor = [1.0, 1.0, 0.0]
        vecDisplay[i].SelectionPointLabelFontFamily = ps['colorbar_font']
        vecDisplay[i].SelectionPointLabelFontSize = 18
        vecDisplay[i].SelectionPointLabelItalic = 0
        vecDisplay[i].SelectionPointLabelJustification = 'Left'
        vecDisplay[i].SelectionPointLabelOpacity = 1.0
        vecDisplay[i].SelectionPointLabelShadow = 0
        vecDisplay[i].GaussianRadius = 0.0
        vecDisplay[i].ShaderPreset = 'Sphere'
        vecDisplay[i].Emissive = 0
        vecDisplay[i].ScaleByArray = 0
        vecDisplay[i].SetScaleArray = [None, '']
        vecDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
        vecDisplay[i].OpacityByArray = 0
        vecDisplay[i].OpacityArray = [None, '']
        vecDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        vecDisplay[i].OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        vecDisplay[i].GlyphType.TipResolution = 6
        vecDisplay[i].GlyphType.TipRadius = 0.1
        vecDisplay[i].GlyphType.TipLength = 0.35
        vecDisplay[i].GlyphType.ShaftResolution = 6
        vecDisplay[i].GlyphType.ShaftRadius = 0.03
        vecDisplay[i].GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        vecDisplay[i].ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        vecDisplay[i].OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # change solid color using normalized EGB code (0...1)
        vecDisplay[i].DiffuseColor = ps['vcolor'][i, :]

    # set the background color
    renderView.Background = ps['background_color']

    # set image size
    renderView.ViewSize = ps['viewsize']  # [width, height]

    # save scene
    paraview.simple.SaveScreenshot(ps['fname_png'], magnification=ps['png_resolution'], quality=100, view=renderView,
                                   TransparentBackground=True,
                                   CompressionLevel=0)

    # crop surrounding of image
    crop_image(ps['fname_png'], ps['fname_png'])

    # Reset Paraview session
    ResetSession()


def volume_plot(ps):
    """
    Generate plot with Paraview from data in .hdf5 file.

    Parameters
    ----------
    ps : dict
        Plot settings dict initialized with create_plot_settings_dict(plotfunction_type=''volume_plot'')

    Returns
    -------
    <File> : .png file
        Generated plot
    """

    # add whitespace if colorbar label is not given (empty colorbar labels are plotted wrong)
    if ps['colorbar_label'] is None or ps['colorbar_label']=='':
        ps['colorbar_label'] = ' '

    if type(ps['fname_in']) is str:
        ps['fname_in'] = [ps['fname_in']]

    _, ext = os.path.splitext(ps['fname_in'][0])

    # make .xdmf file if .hdf5 file is provided
    if ext == '.hdf5':
        mode = 'hdf5'
        fname_load = os.path.join(os.path.splitext(ps['fname_in'][0]), '.xdmf')

        if len(ps['fname_in']) == 1:
            write_xdmf(hdf5_fn = ps['fname_in'][0], hdf5_geo_fn=None, overwrite_xdmf=True)
        elif len(ps['fname_in']) == 2:
            write_xdmf(hdf5_fn = ps['fname_in'][0], hdf5_geo_fn = ps['fname_in'][1], overwrite_xdmf=True)
        else:
            raise Exception('Please specify either one .hdf5 file containing data and geometry or two .hdf5 files,'
                                'whereas the first contains the data and the second the geometry!')
    elif ext == '.xdmf':
        mode = 'xdmf'
        fname_load = ps['fname_in']

    else:
        raise Exception('Please check file type and extension!')

    thresholding = not(ps['domain_IDs'] == [])
    if ps['interpolate']:
        target = 'POINTS'
    else:
        target = 'CELLS'

    # =============================================================================
    # Load data
    # =============================================================================

    # create a new 'Xdmf3ReaderT' for data
    p = paraview.simple.Xdmf3ReaderT(FileName=[fname_load[0]])
    p.PointArrays = []
    p.CellArrays = [ps['quantity'], 'dipole_mag', 'tissue_type']
    p.Sets = []

    # get active view
    renderView = GetActiveViewOrCreate('RenderView')

    # show data in view
    pDisplay = Show(p, renderView)
    # trace defaults for the display properties.
    pDisplay.Representation = 'Surface'
    pDisplay.AmbientColor = [1.0, 1.0, 1.0]
    pDisplay.ColorArrayName = [None, '']
    pDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.LookupTable = None
    pDisplay.MapScalars = 1
    pDisplay.InterpolateScalarsBeforeMapping = 1
    pDisplay.Opacity = 1.0
    pDisplay.PointSize = 2.0
    pDisplay.LineWidth = 1.0
    pDisplay.Interpolation = 'Gouraud'
    pDisplay.Specular = 0.0
    pDisplay.SpecularColor = [1.0, 1.0, 1.0]
    pDisplay.SpecularPower = 100.0
    pDisplay.Ambient = 0.0
    pDisplay.Diffuse = 1.0
    pDisplay.EdgeColor = [0.0, 0.0, 0.5]
    pDisplay.BackfaceRepresentation = 'Follow Frontface'
    pDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceOpacity = 1.0
    pDisplay.Position = [0.0, 0.0, 0.0]
    pDisplay.Scale = [1.0, 1.0, 1.0]
    pDisplay.Orientation = [0.0, 0.0, 0.0]
    pDisplay.Origin = [0.0, 0.0, 0.0]
    pDisplay.Pickable = 1
    pDisplay.Texture = None
    pDisplay.Triangulate = 0
    pDisplay.NonlinearSubdivisionLevel = 1
    pDisplay.OSPRayUseScaleArray = 0
    pDisplay.OSPRayScaleArray = 'tissue_type'
    pDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    pDisplay.GlyphType = 'Arrow'
    pDisplay.SelectionCellLabelBold = 0
    pDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    pDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionCellLabelFontSize = 18
    pDisplay.SelectionCellLabelItalic = 0
    pDisplay.SelectionCellLabelJustification = 'Left'
    pDisplay.SelectionCellLabelOpacity = 1.0
    pDisplay.SelectionCellLabelShadow = 0
    pDisplay.SelectionPointLabelBold = 0
    pDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    pDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionPointLabelFontSize = 18
    pDisplay.SelectionPointLabelItalic = 0
    pDisplay.SelectionPointLabelJustification = 'Left'
    pDisplay.SelectionPointLabelOpacity = 1.0
    pDisplay.SelectionPointLabelShadow = 0
    pDisplay.ScalarOpacityUnitDistance = 1.5164840226522087
    pDisplay.SelectMapper = 'Projected tetra'
    pDisplay.GaussianRadius = 0.0
    pDisplay.ShaderPreset = 'Sphere'
    pDisplay.Emissive = 0
    pDisplay.ScaleByArray = 0
    pDisplay.SetScaleArray = [None, '']
    pDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    pDisplay.OpacityByArray = 0
    pDisplay.OpacityArray = [None, '']
    pDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    pDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    pDisplay.GlyphType.TipResolution = 6
    pDisplay.GlyphType.TipRadius = 0.1
    pDisplay.GlyphType.TipLength = 0.35
    pDisplay.GlyphType.ShaftResolution = 6
    pDisplay.GlyphType.ShaftRadius = 0.03
    pDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    pDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    pDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView.ResetCamera()

    # set scalar coloring
    ColorBy(pDisplay, ('FIELD', 'vtkBlockColors'))

    # show color bar/color legend
    pDisplay.SetScalarBarVisibility(renderView, False)

    # get color transfer function/color map for 'vtkBlockColors'
    vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')
    # vtkBlockColorsLUT.LockDataRange = 0  # not in v5.8 anymore
    vtkBlockColorsLUT.InterpretValuesAsCategories = 1
    vtkBlockColorsLUT.ShowCategoricalColorsinDataRangeOnly = 0
    vtkBlockColorsLUT.RescaleOnVisibilityChange = 0
    vtkBlockColorsLUT.EnableOpacityMapping = 0
    vtkBlockColorsLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 0.5, 0.865003, 0.865003, 0.865003, 1.0, 0.705882,
                                   0.0156863, 0.14902]
    vtkBlockColorsLUT.UseLogScale = 0
    vtkBlockColorsLUT.ColorSpace = 'Diverging'
    vtkBlockColorsLUT.UseBelowRangeColor = 0
    vtkBlockColorsLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    vtkBlockColorsLUT.UseAboveRangeColor = 0
    vtkBlockColorsLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    vtkBlockColorsLUT.NanColor = ps['NanColor']
    vtkBlockColorsLUT.Discretize = 1
    vtkBlockColorsLUT.NumberOfTableValues = 256
    vtkBlockColorsLUT.ScalarRangeInitialized = 0.0
    vtkBlockColorsLUT.HSVWrap = 0
    vtkBlockColorsLUT.VectorComponent = 0
    vtkBlockColorsLUT.VectorMode = 'Magnitude'
    vtkBlockColorsLUT.AllowDuplicateScalars = 1
    vtkBlockColorsLUT.Annotations = ['0', '0', '1', '1', '2', '2', '3', '3', '4', '4', '5', '5', '6', '6', '7', '7',
                                     '8', '8', '9', '9', '10', '10', '11', '11']
    vtkBlockColorsLUT.ActiveAnnotatedValues = ['0', '1', '2']
    vtkBlockColorsLUT.IndexedColors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0,
                                       0.0, 1.0, 0.0, 1.0, 1.0, 0.63, 0.63, 1.0, 0.67, 0.5, 0.33, 1.0, 0.5, 0.75, 0.53,
                                       0.35, 0.7, 1.0, 0.75, 0.5]

    # get opacity transfer function/opacity map for 'vtkBlockColors'
    vtkBlockColorsPWF = GetOpacityTransferFunction('vtkBlockColors')
    vtkBlockColorsPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
    vtkBlockColorsPWF.AllowDuplicateScalars = 1
    vtkBlockColorsPWF.ScalarRangeInitialized = 0

    # hide original dataset
    Hide(p, renderView)

    # =============================================================================
    # Process surface data (make threshold w.r.t. tissue_type > 1000)
    # =============================================================================
    s = paraview.simple.Threshold(Input=p)
    s.Scalars = ['CELLS', 'tissue_type']
    s.ThresholdRange = [np.min(ps['domain_IDs']).astype(float) + 1000, np.max(ps['domain_IDs']).astype(float) + 1000]
    s.AllScalars = 1
    s.UseContinuousCellRange = 0

    # get color transfer function/color map for 'tissuetype'
    tissuetypeLUT = GetColorTransferFunction('tissuetype')
    # tissuetypeLUT.LockDataRange = 0  # not in v5.8 anymore
    tissuetypeLUT.InterpretValuesAsCategories = 0
    tissuetypeLUT.ShowCategoricalColorsinDataRangeOnly = 0
    tissuetypeLUT.RescaleOnVisibilityChange = 0
    tissuetypeLUT.EnableOpacityMapping = 0
    #tissuetypeLUT.RGBPoints = [1002.0, 0.231373, 0.298039, 0.752941, 1002.0050100501, 0.865003, 0.865003, 0.865003,
    #                           1002.0100201002, 0.705882, 0.0156863, 0.14902]
    tissuetypeLUT.UseLogScale = 0
    tissuetypeLUT.ColorSpace = 'Diverging'
    tissuetypeLUT.UseBelowRangeColor = 0
    tissuetypeLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    tissuetypeLUT.UseAboveRangeColor = 0
    tissuetypeLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    tissuetypeLUT.NanColor = ps['NanColor']
    tissuetypeLUT.Discretize = 1
    tissuetypeLUT.NumberOfTableValues = 256
    tissuetypeLUT.ScalarRangeInitialized = 1.0
    tissuetypeLUT.HSVWrap = 0
    tissuetypeLUT.VectorComponent = 0
    tissuetypeLUT.VectorMode = 'Magnitude'
    tissuetypeLUT.AllowDuplicateScalars = 1
    tissuetypeLUT.Annotations = []
    tissuetypeLUT.ActiveAnnotatedValues = []
    tissuetypeLUT.IndexedColors = []

    # show data in view
    sDisplay = Show(s, renderView)
    # trace defaults for the display properties.
    sDisplay.Representation = 'Surface'
    sDisplay.AmbientColor = [1.0, 1.0, 1.0]
    sDisplay.ColorArrayName = ['CELLS', 'tissue_type']
    sDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    sDisplay.LookupTable = tissuetypeLUT
    sDisplay.MapScalars = 1
    sDisplay.InterpolateScalarsBeforeMapping = 1
    sDisplay.Opacity = 1.0
    sDisplay.PointSize = 2.0
    sDisplay.LineWidth = 1.0
    sDisplay.Interpolation = 'Gouraud'
    sDisplay.Specular = 0.0
    sDisplay.SpecularColor = [1.0, 1.0, 1.0]
    sDisplay.SpecularPower = 100.0
    sDisplay.Ambient = 0.0
    sDisplay.Diffuse = 1.0
    sDisplay.EdgeColor = [0.0, 0.0, 0.5]
    sDisplay.BackfaceRepresentation = 'Follow Frontface'
    sDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    sDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    sDisplay.BackfaceOpacity = 1.0
    sDisplay.Position = [0.0, 0.0, 0.0]
    sDisplay.Scale = [1.0, 1.0, 1.0]
    sDisplay.Orientation = [0.0, 0.0, 0.0]
    sDisplay.Origin = [0.0, 0.0, 0.0]
    sDisplay.Pickable = 1
    sDisplay.Texture = None
    sDisplay.Triangulate = 0
    sDisplay.NonlinearSubdivisionLevel = 1
    sDisplay.OSPRayUseScaleArray = 0
    sDisplay.OSPRayScaleArray = 'tissue_type'
    sDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    sDisplay.GlyphType = 'Arrow'
    sDisplay.SelectionCellLabelBold = 0
    sDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    sDisplay.SelectionCellLabelFontFamily =ps['colorbar_font']
    sDisplay.SelectionCellLabelFontSize = 18
    sDisplay.SelectionCellLabelItalic = 0
    sDisplay.SelectionCellLabelJustification = 'Left'
    sDisplay.SelectionCellLabelOpacity = 1.0
    sDisplay.SelectionCellLabelShadow = 0
    sDisplay.SelectionPointLabelBold = 0
    sDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    sDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    sDisplay.SelectionPointLabelFontSize = 18
    sDisplay.SelectionPointLabelItalic = 0
    sDisplay.SelectionPointLabelJustification = 'Left'
    sDisplay.SelectionPointLabelOpacity = 1.0
    sDisplay.SelectionPointLabelShadow = 0
    sDisplay.ScalarOpacityUnitDistance = 3.2593175817027698
    sDisplay.SelectMapper = 'Projected tetra'
    sDisplay.GaussianRadius = 0.0
    sDisplay.ShaderPreset = 'Sphere'
    sDisplay.Emissive = 0
    sDisplay.ScaleByArray = 0
    sDisplay.SetScaleArray = [None, '']
    sDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    sDisplay.OpacityByArray = 0
    sDisplay.OpacityArray = [None, '']
    sDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    sDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    sDisplay.GlyphType.TipResolution = 6
    sDisplay.GlyphType.TipRadius = 0.1
    sDisplay.GlyphType.TipLength = 0.35
    sDisplay.GlyphType.ShaftResolution = 6
    sDisplay.GlyphType.ShaftRadius = 0.03
    sDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    sDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    sDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView.ResetCamera()

    # show color bar/color legend
    sDisplay.SetScalarBarVisibility(renderView, False)

    # get opacity transfer function/opacity map for 'tissuetype'
    tissuetypePWF = GetOpacityTransferFunction('tissuetype')
    #tissuetypePWF.Points = [1002.0, 0.0, 0.5, 0.0, 1002.0100201002, 1.0, 0.5, 0.0]
    tissuetypePWF.AllowDuplicateScalars = 1
    tissuetypePWF.ScalarRangeInitialized = 1

    # turn off scalar coloring
    ColorBy(sDisplay, None)

    # change solid color
    sDisplay.DiffuseColor = ps['surface_color']

    # =============================================================================
    # Process volume data
    # =============================================================================
    if thresholding:

        #for i in range(len(domain_IDs)):

        # create new threshold
        #if interpolate:
        #    t[i] = paraview.simple.Threshold(Input=p1)
        #else:
        t = paraview.simple.Threshold(Input=p)

        t.Scalars = ['CELLS', ps['domain_label']]
        t.ThresholdRange = [np.min(ps['domain_IDs']).astype(float), np.max(ps['domain_IDs']).astype(float)]
        t.AllScalars = 1
        t.UseContinuousCellRange = 0

        tDisplay = Show(t, renderView)

        ColorBy(tDisplay, (target, ps['quantity']))
        tDisplay.Representation = 'Surface'
        tDisplay.AmbientColor = [1.0, 1.0, 1.0]
        tDisplay.ColorArrayName = [None, '']
        tDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        tDisplay.LookupTable = None
        tDisplay.MapScalars = 1
        tDisplay.InterpolateScalarsBeforeMapping = 1
        tDisplay.Opacity = 1.0
        tDisplay.PointSize = 2.0
        tDisplay.LineWidth = 1.0
        tDisplay.Interpolation = 'Gouraud'
        tDisplay.Specular = 0.0
        tDisplay.SpecularColor = [1.0, 1.0, 1.0]
        tDisplay.SpecularPower = 100.0
        tDisplay.Ambient = 0.0
        tDisplay.Diffuse = 1.0
        tDisplay.EdgeColor = [0.0, 0.0, 0.5]
        tDisplay.BackfaceRepresentation = 'Follow Frontface'
        tDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        tDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        tDisplay.BackfaceOpacity = 1.0
        tDisplay.Position = [0.0, 0.0, 0.0]
        tDisplay.Scale = [1.0, 1.0, 1.0]
        tDisplay.Orientation = [0.0, 0.0, 0.0]
        tDisplay.Origin = [0.0, 0.0, 0.0]
        tDisplay.Pickable = 1
        tDisplay.Texture = None
        tDisplay.Triangulate = 0
        tDisplay.NonlinearSubdivisionLevel = 1
        tDisplay.OSPRayUseScaleArray = 0
        tDisplay.OSPRayScaleArray = ps['quantity']
        tDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        tDisplay.GlyphType = 'Arrow'
        tDisplay.SelectionCellLabelBold = 0
        tDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        tDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
        tDisplay.SelectionCellLabelFontSize = 18
        tDisplay.SelectionCellLabelItalic = 0
        tDisplay.SelectionCellLabelJustification = 'Left'
        tDisplay.SelectionCellLabelOpacity = 1.0
        tDisplay.SelectionCellLabelShadow = 0
        tDisplay.SelectionPointLabelBold = 0
        tDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        tDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
        tDisplay.SelectionPointLabelFontSize = 18
        tDisplay.SelectionPointLabelItalic = 0
        tDisplay.SelectionPointLabelJustification = 'Left'
        tDisplay.SelectionPointLabelOpacity = 1.0
        tDisplay.SelectionPointLabelShadow = 0
        tDisplay.ScalarOpacityUnitDistance = 1.8692603892074375
        tDisplay.SelectMapper = 'Projected tetra'
        tDisplay.GaussianRadius = 0.0
        tDisplay.ShaderPreset = 'Sphere'
        tDisplay.Emissive = 0
        tDisplay.ScaleByArray = 0
        tDisplay.SetScaleArray = [None, '']
        tDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        tDisplay.OpacityByArray = 0
        tDisplay.OpacityArray = [None, '']
        tDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        tDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        tDisplay.GlyphType.TipResolution = 6
        tDisplay.GlyphType.TipRadius = 0.1
        tDisplay.GlyphType.TipLength = 0.35
        tDisplay.GlyphType.ShaftResolution = 6
        tDisplay.GlyphType.ShaftRadius = 0.03
        tDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        tDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        tDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # create a new 'Cell Data to Point Data'
    # interpolate and no thresholding
    if ps['interpolate']:
        if thresholding:
            p1 = paraview.simple.CellDatatoPointData(Input=t)
        else:
            p1 = paraview.simple.CellDatatoPointData(Input=p)
        p1.PassCellData = 0
        p1.PieceInvariant = 0
        pDisplay = Show(p1, renderView)
    else:
        if thresholding:
            pDisplay = Show(t, renderView)
        else:
            pDisplay = Show(p, renderView)

    # trace defaults for the display properties.
    pDisplay.Representation = 'Surface'
    pDisplay.AmbientColor = [1.0, 1.0, 1.0]
    pDisplay.ColorArrayName = [None, '']
    pDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.LookupTable = None
    pDisplay.MapScalars = 1
    pDisplay.InterpolateScalarsBeforeMapping = 1
    pDisplay.Opacity = 1.0
    pDisplay.PointSize = 2.0
    pDisplay.LineWidth = 1.0
    pDisplay.Interpolation = 'Gouraud'
    pDisplay.Specular = 0.0
    pDisplay.SpecularColor = [1.0, 1.0, 1.0]
    pDisplay.SpecularPower = 100.0
    pDisplay.Ambient = 0.0
    pDisplay.Diffuse = 1.0
    pDisplay.EdgeColor = [0.0, 0.0, 0.5]
    pDisplay.BackfaceRepresentation = 'Follow Frontface'
    pDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceOpacity = 1.0
    pDisplay.Position = [0.0, 0.0, 0.0]
    pDisplay.Scale = [1.0, 1.0, 1.0]
    pDisplay.Orientation = [0.0, 0.0, 0.0]
    pDisplay.Origin = [0.0, 0.0, 0.0]
    pDisplay.Pickable = 1
    pDisplay.Texture = None
    pDisplay.Triangulate = 0
    pDisplay.NonlinearSubdivisionLevel = 1
    pDisplay.OSPRayUseScaleArray = 0
    pDisplay.OSPRayScaleArray = ''#quantity
    pDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    pDisplay.GlyphType = 'Arrow'
    pDisplay.SelectionCellLabelBold = 0
    pDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    pDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionCellLabelFontSize = 18
    pDisplay.SelectionCellLabelItalic = 0
    pDisplay.SelectionCellLabelJustification = 'Left'
    pDisplay.SelectionCellLabelOpacity = 1.0
    pDisplay.SelectionCellLabelShadow = 0
    pDisplay.SelectionPointLabelBold = 0
    pDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    pDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionPointLabelFontSize = 18
    pDisplay.SelectionPointLabelItalic = 0
    pDisplay.SelectionPointLabelJustification = 'Left'
    pDisplay.SelectionPointLabelOpacity = 1.0
    pDisplay.SelectionPointLabelShadow = 0
    pDisplay.ScalarOpacityUnitDistance = 1.6558923367892595
    pDisplay.SelectMapper = 'Projected tetra'
    pDisplay.GaussianRadius = 0.0
    pDisplay.ShaderPreset = 'Sphere'
    pDisplay.Emissive = 0
    pDisplay.ScaleByArray = 0
    pDisplay.SetScaleArray = [target, '']#quantity
    pDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    pDisplay.OpacityByArray = 0
    pDisplay.OpacityArray = [target, '']#quantity
    pDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    pDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    pDisplay.GlyphType.TipResolution = 6
    pDisplay.GlyphType.TipRadius = 0.1
    pDisplay.GlyphType.TipLength = 0.35
    pDisplay.GlyphType.ShaftResolution = 6
    pDisplay.GlyphType.ShaftRadius = 0.03
    pDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    pDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    pDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # change representation type
    if ps['edges']:
        pDisplay.SetRepresentationType('Surface With Edges')

    # =============================================================================
    # Make Clip or Slice
    # =============================================================================
    # create a new 'Clip'
    if ps['clip_coords'].any():
        # hide original surfaces (will be replaced by new slice objects)
        Hide(s,renderView)

        N_clips = ps['clip_coords'].shape[0]
        clip_coords_surface = copy.deepcopy(ps['clip_coords'])
        pcut = [0] * N_clips
        scut = [0] * N_clips
        pcutDisplay = [0] * N_clips
        scutDisplay = [0] * N_clips

        for i in range(N_clips):
            # shift clip coords of surface a bit to get visability
            for i_shift in range(3):
                if ps['clip_normals'][i, i_shift] > 0:
                    if ps['clip_type'][i] == 'clip':
                        clip_coords_surface[i, i_shift] = copy.deepcopy(ps['clip_coords'][i, i_shift]) - 0.1
                    if ps['clip_type'][i] == 'slice':
                        clip_coords_surface[i, i_shift] = copy.deepcopy(ps['clip_coords'][i, i_shift]) + 0.1

            # clip
            if ps['clip_type'][i] == 'clip':

                # Generate clip
                if ps['interpolate']:
                    if thresholding:
                        pcut[i] = paraview.simple.Clip(Input=p1)
                else:
                    if thresholding:
                        pcut[i] = paraview.simple.Clip(Input=t)
                    else:
                        pcut[i] = paraview.simple.Clip(Input=p)

                # init the 'Plane' selected for 'ClipType' (volume)
                pcut[i].ClipType = 'Plane'
                pcut[i].Scalars = [target, ps['quantity']]
                pcut[i].Value = 0.0
                pcut[i].InsideOut = 0
                pcut[i].Crinkleclip = 0
                pcut[i].ClipType.Origin = [ps['clip_coords'][i, 0], ps['clip_coords'][i, 1], ps['clip_coords'][i, 2]]
                pcut[i].ClipType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
                pcut[i].ClipType.Offset = 0.0

            # slice
            elif ps['clip_type'][i] == 'slice':

                # Generate slice
                if ps['interpolate']:
                    if thresholding:
                        pcut[i] = paraview.simple.Slice(Input=p1)
                else:
                    if thresholding:
                        pcut[i] = paraview.simple.Slice(Input=t)
                    else:
                        pcut[i] = paraview.simple.Slice(Input=p)



                # init the 'Plane' selected for 'ClipType' (volume)
                pcut[i].SliceType = 'Plane'
                pcut[i].Crinkleslice = 0
                pcut[i].Triangulatetheslice = 1
                pcut[i].SliceOffsetValues = [0.0]
                pcut[i].SliceType.Origin = [ps['clip_coords'][i, 0], ps['clip_coords'][i, 1], ps['clip_coords'][i, 2]]
                pcut[i].SliceType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
                pcut[i].SliceType.Offset = 0.0

            # Generate slice (surface)
            scut[i] = paraview.simple.Slice(Input=s)

            # init the 'Plane' selected for 'ClipType' (surface)
            scut[i].SliceType = 'Plane'
            scut[i].Crinkleslice = 0
            scut[i].Triangulatetheslice = 1
            scut[i].SliceOffsetValues = [0.0]
            scut[i].SliceType.Origin = [clip_coords_surface[i, 0], clip_coords_surface[i, 1], clip_coords_surface[i, 2]]
            scut[i].SliceType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
            scut[i].SliceType.Offset = 0.0

            # show data in view
            pcutDisplay[i] = Show(pcut[i], renderView)

            # map results to geometry
            #pcutDisplay[i].ColorArrayName = [target, quantity]
            paraview.simple.ColorBy(pcutDisplay[i], (target, ps['quantity']))

            # trace defaults for the display properties.
            pcutDisplay[i].Representation = 'Surface'
            pcutDisplay[i].AmbientColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].ColorArrayName = [None, '']
            pcutDisplay[i].DiffuseColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].LookupTable = None
            pcutDisplay[i].MapScalars = 1
            pcutDisplay[i].InterpolateScalarsBeforeMapping = 1
            pcutDisplay[i].Opacity = 1.0
            pcutDisplay[i].PointSize = 2.0
            pcutDisplay[i].LineWidth = 1.0
            pcutDisplay[i].Interpolation = 'Gouraud'
            pcutDisplay[i].Specular = 0.0
            pcutDisplay[i].SpecularColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].SpecularPower = 100.0
            pcutDisplay[i].Ambient = 0.0
            pcutDisplay[i].Diffuse = 1.0
            pcutDisplay[i].EdgeColor = [0.0, 0.0, 0.5]
            pcutDisplay[i].BackfaceRepresentation = 'Follow Frontface'
            pcutDisplay[i].BackfaceAmbientColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].BackfaceDiffuseColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].BackfaceOpacity = 1.0
            pcutDisplay[i].Position = [0.0, 0.0, 0.0]
            pcutDisplay[i].Scale = [1.0, 1.0, 1.0]
            pcutDisplay[i].Orientation = [0.0, 0.0, 0.0]
            pcutDisplay[i].Origin = [0.0, 0.0, 0.0]
            pcutDisplay[i].Pickable = 1
            pcutDisplay[i].Texture = None
            pcutDisplay[i].Triangulate = 0
            pcutDisplay[i].NonlinearSubdivisionLevel = 1
            pcutDisplay[i].OSPRayUseScaleArray = 0
            pcutDisplay[i].OSPRayScaleArray = ps['quantity']
            pcutDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
            pcutDisplay[i].GlyphType = 'Arrow'
            pcutDisplay[i].SelectionCellLabelBold = 0
            pcutDisplay[i].SelectionCellLabelColor = [0.0, 1.0, 0.0]
            pcutDisplay[i].SelectionCellLabelFontFamily = ps['colorbar_font']
            pcutDisplay[i].SelectionCellLabelFontSize = 18
            pcutDisplay[i].SelectionCellLabelItalic = 0
            pcutDisplay[i].SelectionCellLabelJustification = 'Left'
            pcutDisplay[i].SelectionCellLabelOpacity = 1.0
            pcutDisplay[i].SelectionCellLabelShadow = 0
            pcutDisplay[i].SelectionPointLabelBold = 0
            pcutDisplay[i].SelectionPointLabelColor = [1.0, 1.0, 0.0]
            pcutDisplay[i].SelectionPointLabelFontFamily = ps['colorbar_font']
            pcutDisplay[i].SelectionPointLabelFontSize = 18
            pcutDisplay[i].SelectionPointLabelItalic = 0
            pcutDisplay[i].SelectionPointLabelJustification = 'Left'
            pcutDisplay[i].SelectionPointLabelOpacity = 1.0
            pcutDisplay[i].SelectionPointLabelShadow = 0
            if ps['clip_type'][i] == 'clip':
                pcutDisplay[i].ScalarOpacityUnitDistance = 1.702063581347167
                pcutDisplay[i].SelectMapper = 'Projected tetra'
            pcutDisplay[i].GaussianRadius = 0.0
            pcutDisplay[i].ShaderPreset = 'Sphere'
            pcutDisplay[i].Emissive = 0
            pcutDisplay[i].ScaleByArray = 0
            if ps['interpolate']:
                pcutDisplay[i].SetScaleArray = [target, ps['quantity']]
                pcutDisplay[i].OpacityArray = [target, ps['quantity']]
            else:
                pcutDisplay[i].SetScaleArray = [None, '']
                pcutDisplay[i].OpacityArray = [None, '']
            pcutDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
            pcutDisplay[i].OpacityByArray = 0
            pcutDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'

            # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
            pcutDisplay[i].OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'Arrow' selected for 'GlyphType'
            pcutDisplay[i].GlyphType.TipResolution = 6
            pcutDisplay[i].GlyphType.TipRadius = 0.1
            pcutDisplay[i].GlyphType.TipLength = 0.35
            pcutDisplay[i].GlyphType.ShaftResolution = 6
            pcutDisplay[i].GlyphType.ShaftRadius = 0.03
            pcutDisplay[i].GlyphType.Invert = 0

            # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
            pcutDisplay[i].ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
            pcutDisplay[i].OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # change representation type
            if ps['edges']:
                pcutDisplay[i].SetRepresentationType('Surface With Edges')

            # Apply all settings from volume slices to surface slices
            #scutDisplay[i] = pcutDisplay[i]

            # set scalar coloring
            paraview.simple.ColorBy(pcutDisplay[i], (target, ps['quantity']))

            # rescale color and/or opacity maps used to include current data range
            pcutDisplay[i].RescaleTransferFunctionToDataRange(True)

            # show color bar/color legend
            pcutDisplay[i].SetScalarBarVisibility(renderView, True)

            # show data in view
            scutDisplay[i] = Show(scut[i], renderView)

            scutDisplay[i].Representation = 'Surface'
            scutDisplay[i].AmbientColor = [1.0, 1.0, 1.0]
            scutDisplay[i].ColorArrayName = ['CELLS', 'tissue_type']
            scutDisplay[i].DiffuseColor = [1.0, 1.0, 1.0]
            scutDisplay[i].LookupTable = tissuetypeLUT
            scutDisplay[i].MapScalars = 1
            scutDisplay[i].InterpolateScalarsBeforeMapping = 1
            scutDisplay[i].Opacity = 1.0
            scutDisplay[i].PointSize = 2.0
            scutDisplay[i].LineWidth = 1.0
            scutDisplay[i].Interpolation = 'Gouraud'
            scutDisplay[i].Specular = 0.0
            scutDisplay[i].SpecularColor = [1.0, 1.0, 1.0]
            scutDisplay[i].SpecularPower = 100.0
            scutDisplay[i].Ambient = 0.0
            scutDisplay[i].Diffuse = 1.0
            scutDisplay[i].EdgeColor = [0.0, 0.0, 0.5]
            scutDisplay[i].BackfaceRepresentation = 'Follow Frontface'
            scutDisplay[i].BackfaceAmbientColor = [1.0, 1.0, 1.0]
            scutDisplay[i].BackfaceDiffuseColor = [1.0, 1.0, 1.0]
            scutDisplay[i].BackfaceOpacity = 1.0
            scutDisplay[i].Position = [0.0, 0.0, 0.0]
            scutDisplay[i].Scale = [1.0, 1.0, 1.0]
            scutDisplay[i].Orientation = [0.0, 0.0, 0.0]
            scutDisplay[i].Origin = [0.0, 0.0, 0.0]
            scutDisplay[i].Pickable = 1
            scutDisplay[i].Texture = None
            scutDisplay[i].Triangulate = 0
            scutDisplay[i].NonlinearSubdivisionLevel = 1
            scutDisplay[i].OSPRayUseScaleArray = 0
            scutDisplay[i].OSPRayScaleArray = 'tissue_type'
            scutDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
            scutDisplay[i].GlyphType = 'Arrow'
            scutDisplay[i].SelectionCellLabelBold = 0
            scutDisplay[i].SelectionCellLabelColor = [0.0, 1.0, 0.0]
            scutDisplay[i].SelectionCellLabelFontFamily = ps['colorbar_font']
            scutDisplay[i].SelectionCellLabelFontSize = 18
            scutDisplay[i].SelectionCellLabelItalic = 0
            scutDisplay[i].SelectionCellLabelJustification = 'Left'
            scutDisplay[i].SelectionCellLabelOpacity = 1.0
            scutDisplay[i].SelectionCellLabelShadow = 0
            scutDisplay[i].SelectionPointLabelBold = 0
            scutDisplay[i].SelectionPointLabelColor = [1.0, 1.0, 0.0]
            scutDisplay[i].SelectionPointLabelFontFamily = ps['colorbar_font']
            scutDisplay[i].SelectionPointLabelFontSize = 18
            scutDisplay[i].SelectionPointLabelItalic = 0
            scutDisplay[i].SelectionPointLabelJustification = 'Left'
            scutDisplay[i].SelectionPointLabelOpacity = 1.0
            scutDisplay[i].SelectionPointLabelShadow = 0
            scutDisplay[i].GaussianRadius = 0.0
            scutDisplay[i].ShaderPreset = 'Sphere'
            scutDisplay[i].Emissive = 0
            scutDisplay[i].ScaleByArray = 0
            if ps['interpolate']:
                scutDisplay[i].SetScaleArray = [target, 'tissue_type']
                scutDisplay[i].OpacityArray = [target, 'tissue_type']
            else:
                scutDisplay[i].SetScaleArray = [None, '']
                scutDisplay[i].OpacityArray = [None, '']

            scutDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
            scutDisplay[i].OpacityByArray = 0
            scutDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'

            # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
            scutDisplay[i].OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'Arrow' selected for 'GlyphType'
            scutDisplay[i].GlyphType.TipResolution = 6
            scutDisplay[i].GlyphType.TipRadius = 0.1
            scutDisplay[i].GlyphType.TipLength = 0.35
            scutDisplay[i].GlyphType.ShaftResolution = 6
            scutDisplay[i].GlyphType.ShaftRadius = 0.03
            scutDisplay[i].GlyphType.Invert = 0

            # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
            scutDisplay[i].ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
            scutDisplay[i].OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # show color bar/color legend
            scutDisplay[i].SetScalarBarVisibility(renderView, False)

            # turn off scalar coloring
            ColorBy(scutDisplay[i], None)

            # change solid color
            scutDisplay[i].DiffuseColor = ps['surface_color']


    # =============================================================================
    # Disable selected elements for final view
    # =============================================================================
    if ps['interpolate']:
        if thresholding:
            Hide(t, renderView)
            Hide(p1, renderView)
        else:
            Hide(p, renderView)
    else:
        if thresholding:
            Hide(p, renderView)

    # turn off orientation axes
    if not (ps['axes']):
        renderView.OrientationAxesVisibility = 0

    # =============================================================================
    # Setup colormap and colorbar
    # =============================================================================
    # get color transfer function/color map for 'quantity'
    eLUT = GetColorTransferFunction(ps['quantity'])
    # eLUT.LockDataRange = 0  # not in v5.8 anymore
    eLUT.InterpretValuesAsCategories = 0
    eLUT.ShowCategoricalColorsinDataRangeOnly = 0
    eLUT.RescaleOnVisibilityChange = 0
    eLUT.EnableOpacityMapping = 0
    eLUT.UseLogScale = 0
    if ps['interpolate']:
        eLUT.ColorSpace = 'RGB'
    else:
        eLUT.ColorSpace = 'RGB' #'Diverging'
    eLUT.ColorSpace = 'Diverging'
    eLUT.UseBelowRangeColor = 0
    eLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    eLUT.UseAboveRangeColor = 0
    eLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    eLUT.NanColor = ps['NanColor']
    eLUT.Discretize = 1
    eLUT.NumberOfTableValues = 256
    eLUT.ScalarRangeInitialized = 1.0
    eLUT.HSVWrap = 0
    eLUT.VectorComponent = 0
    eLUT.VectorMode = 'Magnitude'
    eLUT.AllowDuplicateScalars = 1
    eLUT.Annotations = []
    eLUT.ActiveAnnotatedValues = []
    eLUT.IndexedColors = []

    # set opacity transfer function/opacity map for 'quantity'
    ePWF = GetOpacityTransferFunction(ps['quantity'])
    if not(ps['opacitymap']==[]):
        eLUT.EnableOpacityMapping = 1
        ePWF.Points = ps['opacitymap']
    ePWF.AllowDuplicateScalars = 1
    ePWF.ScalarRangeInitialized = 1

    colormap_presets = {'Cool to Warm',
                        'Cool to Warm (Extended)',
                        'Blue to Red Rainbow',
                        'X Ray',
                        'Grayscale',
                        'jet',
                        'hsv',
                        'erdc_iceFire_L',
                        'Plasma (matplotlib)',
                        'Viridis (matplotlib)',
                        'gray_Matlab',
                        'Spectral_lowBlue',
                        'Rainbow Blended White',
                        'BuRd'}

    if type(ps['colormap']) is str:
        # set colorbar to 'jet' if not specified in presets
        if not (ps['colormap'] in colormap_presets):
            print((
                'Changing colormap to \'jet\' since user specified colormap \'{}\' is not part of the included presets ...').format(
                ps['colormap']))
            colormap = 'jet'

        if ps['colormap'] == 'b2rcw':
            rgb_values = b2rcw(ps['datarange'][0], ps['datarange'][1])
            rgb_data = np.linspace(ps['datarange'][0], ps['datarange'][1], rgb_values.shape[0])
            eLUT.RGBPoints = np.hstack((rgb_data,rgb_values))
        else:
            # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
            eLUT.ApplyPreset(ps['colormap'], True)
    else:
        eLUT.RGBPoints = ps['colormap']

    # =============================================================================
    # colorbar
    # =============================================================================
    # get color legend/bar for eLUT in view renderView
    eLUTColorBar = GetScalarBar(eLUT, renderView)
    if ps['colorbar_position']:
        eLUTColorBar.Position = ps['colorbar_position']
    else:
        eLUTColorBar.Position = [0.85, 0.05]
    # eLUTColorBar.Position2 = [0.12, 0.43]  # 'Position2' is obsolete as of ParaView 5.4. Use the 'ScalarBarLength' property to set the length instead.
    eLUTColorBar.AutoOrient = 1
    eLUTColorBar.Orientation = ps['colorbar_orientation']
    eLUTColorBar.Title = ps['quantity']
    eLUTColorBar.ComponentTitle = 'Magnitude'
    eLUTColorBar.TitleJustification = 'Centered'
    eLUTColorBar.TitleColor = ps['colorbar_labelcolor']
    eLUTColorBar.TitleOpacity = 1.0
    eLUTColorBar.TitleFontFamily = ps['colorbar_font']
    eLUTColorBar.TitleBold = 0
    eLUTColorBar.TitleItalic = 0
    eLUTColorBar.TitleShadow = 0
    eLUTColorBar.LabelColor = ps['colorbar_labelcolor']
    eLUTColorBar.LabelOpacity = 1.0
    eLUTColorBar.LabelFontFamily = ps['colorbar_font']
    eLUTColorBar.LabelBold = 0
    eLUTColorBar.LabelItalic = 0
    eLUTColorBar.LabelShadow = 0
    eLUTColorBar.AutomaticLabelFormat = 0
    eLUTColorBar.LabelFormat = ps['colorbar_labelformat']
    # eLUTColorBar.NumberOfLabels = ps['colorbar_numberoflabels']  # not in v5.8 anymore
    eLUTColorBar.DrawTickMarks = 1
    # eLUTColorBar.DrawSubTickMarks = 1  # not in v5.8 anymore
    eLUTColorBar.DrawTickLabels = 1
    eLUTColorBar.AddRangeLabels = 1
    eLUTColorBar.RangeLabelFormat = ps['colorbar_labelformat']
    eLUTColorBar.DrawAnnotations = 1
    eLUTColorBar.AddRangeAnnotations = 0
    eLUTColorBar.AutomaticAnnotations = 0
    eLUTColorBar.DrawNanAnnotation = 0
    eLUTColorBar.NanAnnotation = 'NaN'
    eLUTColorBar.TextPosition = 'Ticks right/top, annotations left/bottom'
    # eLUTColorBar.AspectRatio = ps['colorbar_aspectratio']  # paraview.NotSupportedException: 'AspectRatio' is obsolete as of ParaView 5.4. Use the 'ScalarBarThickness' property to set the width instead.
    eLUTColorBar.Title = ps['colorbar_label']
    eLUTColorBar.ComponentTitle = ''
    eLUTColorBar.TitleFontSize = ps['colorbar_titlefontsize']
    eLUTColorBar.LabelFontSize = ps['colorbar_labelfontsize']

    # Rescale transfer function
    if ps['datarange']:
        eLUT.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])
        ePWF.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])

    # camera placement for renderView
    if len(ps['view']) == 4:
        renderView.CameraPosition = ps['view'][0]
        renderView.CameraFocalPoint = ps['view'][1]
        renderView.CameraViewUp = ps['view'][2]
        renderView.CameraParallelScale = ps['view'][3][0]
    else:
        renderView.ResetCamera()

    # =============================================================================
    # coil
    # =============================================================================
    source = GetActiveSource()
    source.UpdatePipeline()
    cdi = source.GetDataInformation().GetCompositeDataInformation()
    n_blocks = cdi.GetNumberOfChildren()
    block_names = [cdi.GetName(i) for i in range(n_blocks)]

    if 'coil' in block_names and ps['show_coil']:
        plot_coil = True
    else:
        plot_coil = False

    if plot_coil:

        # create a new 'Threshold'
        coilthreshold = paraview.simple.Threshold(Input=p)
        coilthreshold.Scalars = ['CELLS', 'dipole_mag']
        #threshold1.ThresholdRange = [1.1648167371749878, 8.777523040771484]
        coilthreshold.AllScalars = 1
        coilthreshold.UseContinuousCellRange = 0

        # show data in view
        coilthresholdDisplay = Show(coilthreshold, renderView)
        # trace defaults for the display properties.
        coilthresholdDisplay.Representation = 'Surface'
        coilthresholdDisplay.AmbientColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.ColorArrayName = ['CELLS', 'dipole_mag']
        coilthresholdDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        #coilthresholdDisplay.LookupTable = dipolemagLUT
        coilthresholdDisplay.MapScalars = 1
        coilthresholdDisplay.InterpolateScalarsBeforeMapping = 1
        coilthresholdDisplay.Opacity = 1.0
        coilthresholdDisplay.PointSize = 2.0
        coilthresholdDisplay.LineWidth = 1.0
        coilthresholdDisplay.Interpolation = 'Gouraud'
        coilthresholdDisplay.Specular = 0.0
        coilthresholdDisplay.SpecularColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.SpecularPower = 100.0
        coilthresholdDisplay.Ambient = 0.0
        coilthresholdDisplay.Diffuse = 1.0
        coilthresholdDisplay.EdgeColor = [0.0, 0.0, 0.5]
        coilthresholdDisplay.BackfaceRepresentation = 'Follow Frontface'
        coilthresholdDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        coilthresholdDisplay.BackfaceOpacity = 1.0
        coilthresholdDisplay.Position = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Scale = [1.0, 1.0, 1.0]
        coilthresholdDisplay.Orientation = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Origin = [0.0, 0.0, 0.0]
        coilthresholdDisplay.Pickable = 1
        coilthresholdDisplay.Texture = None
        coilthresholdDisplay.Triangulate = 0
        coilthresholdDisplay.NonlinearSubdivisionLevel = 1
        coilthresholdDisplay.OSPRayUseScaleArray = 0
        coilthresholdDisplay.OSPRayScaleArray = 'dipole_mag'
        coilthresholdDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilthresholdDisplay.GlyphType = 'Arrow'
        coilthresholdDisplay.SelectionCellLabelBold = 0
        coilthresholdDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        coilthresholdDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
        coilthresholdDisplay.SelectionCellLabelFontSize = 18
        coilthresholdDisplay.SelectionCellLabelItalic = 0
        coilthresholdDisplay.SelectionCellLabelJustification = 'Left'
        coilthresholdDisplay.SelectionCellLabelOpacity = 1.0
        coilthresholdDisplay.SelectionCellLabelShadow = 0
        coilthresholdDisplay.SelectionPointLabelBold = 0
        coilthresholdDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        coilthresholdDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
        coilthresholdDisplay.SelectionPointLabelFontSize = 18
        coilthresholdDisplay.SelectionPointLabelItalic = 0
        coilthresholdDisplay.SelectionPointLabelJustification = 'Left'
        coilthresholdDisplay.SelectionPointLabelOpacity = 1.0
        coilthresholdDisplay.SelectionPointLabelShadow = 0
        coilthresholdDisplay.ScalarOpacityUnitDistance = 10.18430143021554
        coilthresholdDisplay.SelectMapper = 'Projected tetra'
        coilthresholdDisplay.GaussianRadius = 0.0
        coilthresholdDisplay.ShaderPreset = 'Sphere'
        coilthresholdDisplay.Emissive = 0
        coilthresholdDisplay.ScaleByArray = 0
        coilthresholdDisplay.SetScaleArray = [None, '']
        coilthresholdDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilthresholdDisplay.OpacityByArray = 0
        coilthresholdDisplay.OpacityArray = [None, '']
        coilthresholdDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        coilthresholdDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        coilthresholdDisplay.GlyphType.TipResolution = 6
        coilthresholdDisplay.GlyphType.TipRadius = 0.1
        coilthresholdDisplay.GlyphType.TipLength = 0.35
        coilthresholdDisplay.GlyphType.ShaftResolution = 6
        coilthresholdDisplay.GlyphType.ShaftRadius = 0.03
        coilthresholdDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        coilthresholdDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        coilthresholdDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # show color bar/color legend
        coilthresholdDisplay.SetScalarBarVisibility(renderView, False)

        # create a new 'Glyph'
        coilGlyph = paraview.simple.Glyph(Input=coilthreshold, GlyphType='Arrow')
        coilGlyph.Scalars = ['CELLS', 'dipole_mag']
        coilGlyph.Vectors = ['POINTS', 'None']
        coilGlyph.Orient = 1
        coilGlyph.GlyphMode = 'All Points'
        coilGlyph.MaximumNumberOfSamplePoints = 5000
        coilGlyph.Seed = 10339
        coilGlyph.Stride = 1
        coilGlyph.GlyphTransform = 'Transform2'
        coilGlyph.GlyphType = 'Sphere'

        # set dipole scaling and size
        if ps['coil_dipole_scaling'][0] == 'scaled':
            coilGlyph.Scalars = ['POINTS', 'magnitude']
            coilGlyph.ScaleMode = 'scalar'
        else:
            coilGlyph.ScaleMode = 'off'

        coilGlyph.ScaleFactor = ps['coil_dipole_scaling'][1]

        # init the 'Transform2' selected for 'GlyphTransform'
        coilGlyph.GlyphTransform.Translate = [0.0, 0.0, 0.0]
        coilGlyph.GlyphTransform.Rotate = [0.0, 0.0, 0.0]
        coilGlyph.GlyphTransform.Scale = [1.0, 1.0, 1.0]

        # get color transfer function/color map for 'dipolemag'
        dipolemagLUT = GetColorTransferFunction('dipolemag')
        # dipolemagLUT.LockDataRange = 0  # not in v5.8 anymore
        dipolemagLUT.InterpretValuesAsCategories = 0
        dipolemagLUT.ShowCategoricalColorsinDataRangeOnly = 0
        dipolemagLUT.RescaleOnVisibilityChange = 0
        dipolemagLUT.EnableOpacityMapping = 0
        dipolemagLUT.UseLogScale = 0
        dipolemagLUT.ColorSpace = 'Lab'
        dipolemagLUT.UseBelowRangeColor = 0
        dipolemagLUT.BelowRangeColor = [0.0, 0.0, 0.0]
        dipolemagLUT.UseAboveRangeColor = 0
        dipolemagLUT.AboveRangeColor = [1.0, 1.0, 1.0]
        dipolemagLUT.NanColor = ps['NanColor']
        dipolemagLUT.Discretize = 1
        dipolemagLUT.NumberOfTableValues = 256
        dipolemagLUT.ScalarRangeInitialized = 1.0
        dipolemagLUT.HSVWrap = 0
        dipolemagLUT.VectorComponent = 0
        dipolemagLUT.VectorMode = 'Magnitude'
        dipolemagLUT.AllowDuplicateScalars = 1
        dipolemagLUT.Annotations = []
        dipolemagLUT.ActiveAnnotatedValues = []
        dipolemagLUT.IndexedColors = []

        # show data in view
        coilGlyphDisplay = Show(coilGlyph, renderView)

        # trace defaults for the display properties.
        coilGlyphDisplay.Representation = 'Surface'
        coilGlyphDisplay.AmbientColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.ColorArrayName = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.LookupTable = dipolemagLUT
        coilGlyphDisplay.MapScalars = 1
        coilGlyphDisplay.InterpolateScalarsBeforeMapping = 1
        coilGlyphDisplay.Opacity = 1.0
        coilGlyphDisplay.PointSize = 2.0
        coilGlyphDisplay.LineWidth = 1.0
        coilGlyphDisplay.Interpolation = 'Gouraud'
        coilGlyphDisplay.Specular = 0.0
        coilGlyphDisplay.SpecularColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.SpecularPower = 100.0
        coilGlyphDisplay.Ambient = 0.0
        coilGlyphDisplay.Diffuse = 1.0
        coilGlyphDisplay.EdgeColor = [0.0, 0.0, 0.5]
        coilGlyphDisplay.BackfaceRepresentation = 'Follow Frontface'
        coilGlyphDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        coilGlyphDisplay.BackfaceOpacity = 1.0
        coilGlyphDisplay.Position = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Scale = [1.0, 1.0, 1.0]
        coilGlyphDisplay.Orientation = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Origin = [0.0, 0.0, 0.0]
        coilGlyphDisplay.Pickable = 1
        coilGlyphDisplay.Texture = None
        coilGlyphDisplay.Triangulate = 0
        coilGlyphDisplay.NonlinearSubdivisionLevel = 1
        coilGlyphDisplay.OSPRayUseScaleArray = 0
        coilGlyphDisplay.OSPRayScaleArray = 'dipole_mag'
        coilGlyphDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilGlyphDisplay.GlyphType = 'Arrow'
        coilGlyphDisplay.SelectionCellLabelBold = 0
        coilGlyphDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        coilGlyphDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
        coilGlyphDisplay.SelectionCellLabelFontSize = 18
        coilGlyphDisplay.SelectionCellLabelItalic = 0
        coilGlyphDisplay.SelectionCellLabelJustification = 'Left'
        coilGlyphDisplay.SelectionCellLabelOpacity = 1.0
        coilGlyphDisplay.SelectionCellLabelShadow = 0
        coilGlyphDisplay.SelectionPointLabelBold = 0
        coilGlyphDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        coilGlyphDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
        coilGlyphDisplay.SelectionPointLabelFontSize = 18
        coilGlyphDisplay.SelectionPointLabelItalic = 0
        coilGlyphDisplay.SelectionPointLabelJustification = 'Left'
        coilGlyphDisplay.SelectionPointLabelOpacity = 1.0
        coilGlyphDisplay.SelectionPointLabelShadow = 0
        coilGlyphDisplay.GaussianRadius = 0.0
        coilGlyphDisplay.ShaderPreset = 'Sphere'
        coilGlyphDisplay.Emissive = 0
        coilGlyphDisplay.ScaleByArray = 0
        coilGlyphDisplay.SetScaleArray = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilGlyphDisplay.OpacityByArray = 0
        coilGlyphDisplay.OpacityArray = ['POINTS', 'dipole_mag']
        coilGlyphDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        coilGlyphDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        coilGlyphDisplay.GlyphType.TipResolution = 6
        coilGlyphDisplay.GlyphType.TipRadius = 0.1
        coilGlyphDisplay.GlyphType.TipLength = 0.35
        coilGlyphDisplay.GlyphType.ShaftResolution = 6
        coilGlyphDisplay.GlyphType.ShaftRadius = 0.03
        coilGlyphDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        coilGlyphDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        coilGlyphDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # show color bar/color legend
        coilGlyphDisplay.SetScalarBarVisibility(renderView, False)

        # set dipole color
        if isinstance(ps['coil_dipole_color'], (str,)):
            # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
            dipolemagLUT.ApplyPreset(ps['coil_dipole_color'], True)

        else:
            # change solid color
            coilGlyphDisplay.DiffuseColor = ps['coil_dipole_color']

        # =============================================================
        # set coil axes direction
        # =============================================================
        if ps['coil_axes']:
            import vtk.numpy_interface.dataset_adapter as dsa

            # read points out of dataset
            coilthreshold.UpdatePipeline()
            rawData = servermanager.Fetch(coilthreshold)
            data = dsa.WrapDataObject(rawData)
            points = np.array(data.Points.Arrays[2])

            # determine coil center
            coil_center = np.average(points, axis=0)

            # shift coil to center for SVD
            points = points - coil_center

            line = [0] * 3
            lineDisplay = [0] * 3
            line_color = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            U, s, V = np.linalg.svd(points, full_matrices=True)
            points_transform = np.dot(points, V.transpose())
            coil_dim = np.max(points_transform, axis=0) - np.min(points_transform, axis=0)

            for i in range(3):
                # create a new 'Line'
                line[i] = paraview.simple.Line()
                # Properties modified on line1
                line[i].Point1 = coil_center
                if ((i == 0) or (i == 1)):
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[i] / 2
                if i == 2:
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[0] / 2
                line[i].Resolution = 1000
                # set active source
                SetActiveSource(line[i])
                # show data in view
                lineDisplay[i] = Show(line[i], renderView)
                # trace defaults for the display properties.
                lineDisplay[i].ColorArrayName = [None, '']
                lineDisplay[i].OSPRayScaleArray = 'Texture Coordinates'
                lineDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
                lineDisplay[i].GlyphType = 'Sphere'
                lineDisplay[i].SetScaleArray = [None, '']
                lineDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].OpacityArray = [None, '']
                lineDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].ShaderPreset = 'Gaussian Blur (Default)'
                lineDisplay[i].DiffuseColor = line_color[i]
                lineDisplay[i].SetRepresentationType('3D Glyphs')
                lineDisplay[i].GlyphType.Radius = 1.0

    # =============================================================================
    # plot parameters
    # =============================================================================

    # set the background color
    renderView.Background = ps['background_color']

    # set image size
    renderView.ViewSize = ps['viewsize']  # [width, height]

    # save scene
    paraview.simple.SaveScreenshot(ps['fname_png'], magnification=ps['png_resolution'], quality=100, view=renderView)

    # crop surrounding of image
    crop_image(ps['fname_png'], ps['fname_png'])

    # Reset Paraview session
    ResetSession()


def volume_plot_vtu(ps):
    """
    Generate plot with Paraview from data in .vtu file.

    Parameters
    ----------
    ps : dict
        Plot settings dict initialized with create_plot_settings_dict(plotfunction_type=''volume_plot_vtu'')

    Returns
    -------
    <File> : .png file
        Generated plot
    """

    # add whitespace if colorbar label is not given (empty colorbar labels are plotted wrong)
    if ps['colorbar_label'] is None or ps['colorbar_label']=='':
        ps['colorbar_label'] = ' '

    thresholding = not(ps['domain_IDs'] == [])
    if ps['interpolate']:
        target = 'POINTS'
    else:
        target = 'CELLS'
    # =============================================================================
    # Load and process surface data
    # =============================================================================

    s = paraview.simple.XMLUnstructuredGridReader(FileName=[ps['fname_vtu_surface']])
    s.CellArrayStatus = ['quantity']
    s.PointArrayStatus = []

    # get active view
    renderView = GetActiveViewOrCreate('RenderView')
    # uncomment following to set a specific view size
    # renderView.ViewSize = [1031, 1164]

    # show data in view
    sDisplay = Show(s, renderView)
    # trace defaults for the display properties.
    sDisplay.Representation = 'Surface'
    sDisplay.AmbientColor = [1.0, 1.0, 1.0]
    sDisplay.ColorArrayName = [None, '']
    sDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    sDisplay.LookupTable = None
    sDisplay.MapScalars = 1
    sDisplay.InterpolateScalarsBeforeMapping = 1
    sDisplay.Opacity = 1.0
    sDisplay.PointSize = 2.0
    sDisplay.LineWidth = 1.0
    sDisplay.Interpolation = 'Gouraud'
    sDisplay.Specular = 0.0
    sDisplay.SpecularColor = [1.0, 1.0, 1.0]
    sDisplay.SpecularPower = 100.0
    sDisplay.Ambient = 0.0
    sDisplay.Diffuse = 1.0
    sDisplay.EdgeColor = [0.0, 0.0, 0.5]
    sDisplay.BackfaceRepresentation = 'Follow Frontface'
    sDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    sDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    sDisplay.BackfaceOpacity = 1.0
    sDisplay.Position = [0.0, 0.0, 0.0]
    sDisplay.Scale = [1.0, 1.0, 1.0]
    sDisplay.Orientation = [0.0, 0.0, 0.0]
    sDisplay.Origin = [0.0, 0.0, 0.0]
    sDisplay.Pickable = 1
    sDisplay.Texture = None
    sDisplay.Triangulate = 0
    sDisplay.NonlinearSubdivisionLevel = 1
    sDisplay.OSPRayUseScaleArray = 0
    sDisplay.OSPRayScaleArray = ps['quantity']
    sDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    sDisplay.GlyphType = 'Arrow'
    sDisplay.SelectionCellLabelBold = 0
    sDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    sDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
    sDisplay.SelectionCellLabelFontSize = 18
    sDisplay.SelectionCellLabelItalic = 0
    sDisplay.SelectionCellLabelJustification = 'Left'
    sDisplay.SelectionCellLabelOpacity = 1.0
    sDisplay.SelectionCellLabelShadow = 0
    sDisplay.SelectionPointLabelBold = 0
    sDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    sDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    sDisplay.SelectionPointLabelFontSize = 18
    sDisplay.SelectionPointLabelItalic = 0
    sDisplay.SelectionPointLabelJustification = 'Left'
    sDisplay.SelectionPointLabelOpacity = 1.0
    sDisplay.SelectionPointLabelShadow = 0
    sDisplay.ScalarOpacityUnitDistance = 2.7853016213990154
    sDisplay.SelectMapper = 'Projected tetra'
    sDisplay.GaussianRadius = 0.0
    sDisplay.ShaderPreset = 'Sphere'
    sDisplay.Emissive = 0
    sDisplay.ScaleByArray = 0
    sDisplay.SetScaleArray = [None, '']
    sDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    sDisplay.OpacityByArray = 0
    sDisplay.OpacityArray = [None, '']
    sDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    sDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    sDisplay.GlyphType.TipResolution = 6
    sDisplay.GlyphType.TipRadius = 0.1
    sDisplay.GlyphType.TipLength = 0.35
    sDisplay.GlyphType.ShaftResolution = 6
    sDisplay.GlyphType.ShaftRadius = 0.03
    sDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    sDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    sDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # change solid color
    sDisplay.DiffuseColor = ps['surface_color']

    # Hide outer surface
    Hide(s, renderView)

    # =============================================================================
    # Load and process volume data
    # =============================================================================

    # create a new 'XML Unstructured Grid Reader' for volume data
    p = paraview.simple.XMLUnstructuredGridReader(FileName=[ps['fname_vtu_volume']])
    p.PointArrayStatus = []

    # get data ranges of included datasets
    # if datarange == []:
    #    sm = servermanager.Fetch(p)
    #    datarange = sm.GetCellData().GetArray(0).GetRange(0)

    # select specific domains
    # =============================================================================

    # determine IDs of cells in domains of interest
    # ...

    # select cells/points of domains of interest
    # selection = paraview.simple.IDSelectionSource(ContainingCells=1, FieldType="CELL", IDs=[0, cellID0, 0, cellID1, 0, cellID2, ...])
    # selection.GetCellDataInformation()

    # extract selection
    # extracted = paraview.simple.ExtractSelection(selection)

    # =====================================================
    # Show only domains of interest (create 'Threshold')
    # =====================================================
    #t = [0]*len(domain_IDs)
    #tDisplay = [0]*len(domain_IDs)

    if thresholding:

        #for i in range(len(domain_IDs)):

        # create new threshold
        #if interpolate:
        #    t[i] = paraview.simple.Threshold(Input=p1)
        #else:
        t = paraview.simple.Threshold(Input=p)

        t.Scalars = ['CELLS', ps['domain_label']]
        t.ThresholdRange = [np.min(ps['domain_IDs']).astype(float), np.max(ps['domain_IDs']).astype(float)]
        t.AllScalars = 1
        t.UseContinuousCellRange = 0

        tDisplay = Show(t, renderView)

        ColorBy(tDisplay, (target, ps['quantity']))
        tDisplay.Representation = 'Surface'
        tDisplay.AmbientColor = [1.0, 1.0, 1.0]
        tDisplay.ColorArrayName = [None, '']
        tDisplay.DiffuseColor = [1.0, 1.0, 1.0]
        tDisplay.LookupTable = None
        tDisplay.MapScalars = 1
        tDisplay.InterpolateScalarsBeforeMapping = 1
        tDisplay.Opacity = 1.0
        tDisplay.PointSize = 2.0
        tDisplay.LineWidth = 1.0
        tDisplay.Interpolation = 'Gouraud'
        tDisplay.Specular = 0.0
        tDisplay.SpecularColor = [1.0, 1.0, 1.0]
        tDisplay.SpecularPower = 100.0
        tDisplay.Ambient = 0.0
        tDisplay.Diffuse = 1.0
        tDisplay.EdgeColor = [0.0, 0.0, 0.5]
        tDisplay.BackfaceRepresentation = 'Follow Frontface'
        tDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        tDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        tDisplay.BackfaceOpacity = 1.0
        tDisplay.Position = [0.0, 0.0, 0.0]
        tDisplay.Scale = [1.0, 1.0, 1.0]
        tDisplay.Orientation = [0.0, 0.0, 0.0]
        tDisplay.Origin = [0.0, 0.0, 0.0]
        tDisplay.Pickable = 1
        tDisplay.Texture = None
        tDisplay.Triangulate = 0
        tDisplay.NonlinearSubdivisionLevel = 1
        tDisplay.OSPRayUseScaleArray = 0
        tDisplay.OSPRayScaleArray = ps['quantity']
        tDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        tDisplay.GlyphType = 'Arrow'
        tDisplay.SelectionCellLabelBold = 0
        tDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        tDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
        tDisplay.SelectionCellLabelFontSize = 18
        tDisplay.SelectionCellLabelItalic = 0
        tDisplay.SelectionCellLabelJustification = 'Left'
        tDisplay.SelectionCellLabelOpacity = 1.0
        tDisplay.SelectionCellLabelShadow = 0
        tDisplay.SelectionPointLabelBold = 0
        tDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
        tDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
        tDisplay.SelectionPointLabelFontSize = 18
        tDisplay.SelectionPointLabelItalic = 0
        tDisplay.SelectionPointLabelJustification = 'Left'
        tDisplay.SelectionPointLabelOpacity = 1.0
        tDisplay.SelectionPointLabelShadow = 0
        tDisplay.ScalarOpacityUnitDistance = 1.8692603892074375
        tDisplay.SelectMapper = 'Projected tetra'
        tDisplay.GaussianRadius = 0.0
        tDisplay.ShaderPreset = 'Sphere'
        tDisplay.Emissive = 0
        tDisplay.ScaleByArray = 0
        tDisplay.SetScaleArray = [None, '']
        tDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        tDisplay.OpacityByArray = 0
        tDisplay.OpacityArray = [None, '']
        tDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
        tDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'Arrow' selected for 'GlyphType'
        tDisplay.GlyphType.TipResolution = 6
        tDisplay.GlyphType.TipRadius = 0.1
        tDisplay.GlyphType.TipLength = 0.35
        tDisplay.GlyphType.ShaftResolution = 6
        tDisplay.GlyphType.ShaftRadius = 0.03
        tDisplay.GlyphType.Invert = 0

        # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
        tDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

        # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
        tDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # create a new 'Cell Data to Point Data'
    # interpolate and no thresholding
    if ps['interpolate']:
        if thresholding:
            p1 = paraview.simple.CellDatatoPointData(Input=t)
        else:
            p1 = paraview.simple.CellDatatoPointData(Input=p)
        p1.PassCellData = 0
        p1.PieceInvariant = 0
        pDisplay = Show(p1, renderView)
    else:
        if thresholding:
            pDisplay = Show(t, renderView)
        else:
            pDisplay = Show(p, renderView)

    # trace defaults for the display properties.
    pDisplay.Representation = 'Surface'
    pDisplay.AmbientColor = [1.0, 1.0, 1.0]
    pDisplay.ColorArrayName = [None, '']
    pDisplay.DiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.LookupTable = None
    pDisplay.MapScalars = 1
    pDisplay.InterpolateScalarsBeforeMapping = 1
    pDisplay.Opacity = 1.0
    pDisplay.PointSize = 2.0
    pDisplay.LineWidth = 1.0
    pDisplay.Interpolation = 'Gouraud'
    pDisplay.Specular = 0.0
    pDisplay.SpecularColor = [1.0, 1.0, 1.0]
    pDisplay.SpecularPower = 100.0
    pDisplay.Ambient = 0.0
    pDisplay.Diffuse = 1.0
    pDisplay.EdgeColor = [0.0, 0.0, 0.5]
    pDisplay.BackfaceRepresentation = 'Follow Frontface'
    pDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
    pDisplay.BackfaceOpacity = 1.0
    pDisplay.Position = [0.0, 0.0, 0.0]
    pDisplay.Scale = [1.0, 1.0, 1.0]
    pDisplay.Orientation = [0.0, 0.0, 0.0]
    pDisplay.Origin = [0.0, 0.0, 0.0]
    pDisplay.Pickable = 1
    pDisplay.Texture = None
    pDisplay.Triangulate = 0
    pDisplay.NonlinearSubdivisionLevel = 1
    pDisplay.OSPRayUseScaleArray = 0
    pDisplay.OSPRayScaleArray = ''#quantity
    pDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    pDisplay.GlyphType = 'Arrow'
    pDisplay.SelectionCellLabelBold = 0
    pDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    pDisplay.SelectionCellLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionCellLabelFontSize = 18
    pDisplay.SelectionCellLabelItalic = 0
    pDisplay.SelectionCellLabelJustification = 'Left'
    pDisplay.SelectionCellLabelOpacity = 1.0
    pDisplay.SelectionCellLabelShadow = 0
    pDisplay.SelectionPointLabelBold = 0
    pDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    pDisplay.SelectionPointLabelFontFamily = ps['colorbar_font']
    pDisplay.SelectionPointLabelFontSize = 18
    pDisplay.SelectionPointLabelItalic = 0
    pDisplay.SelectionPointLabelJustification = 'Left'
    pDisplay.SelectionPointLabelOpacity = 1.0
    pDisplay.SelectionPointLabelShadow = 0
    pDisplay.ScalarOpacityUnitDistance = 1.6558923367892595
    pDisplay.SelectMapper = 'Projected tetra'
    pDisplay.GaussianRadius = 0.0
    pDisplay.ShaderPreset = 'Sphere'
    pDisplay.Emissive = 0
    pDisplay.ScaleByArray = 0
    pDisplay.SetScaleArray = [target, '']#quantity
    pDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    pDisplay.OpacityByArray = 0
    pDisplay.OpacityArray = [target, '']#quantity
    pDisplay.OpacityTransferFunction = 'PiecewiseFunction'

    # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
    pDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'Arrow' selected for 'GlyphType'
    pDisplay.GlyphType.TipResolution = 6
    pDisplay.GlyphType.TipRadius = 0.1
    pDisplay.GlyphType.TipLength = 0.35
    pDisplay.GlyphType.ShaftResolution = 6
    pDisplay.GlyphType.ShaftRadius = 0.03
    pDisplay.GlyphType.Invert = 0

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    pDisplay.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    pDisplay.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

    # change representation type
    if ps['edges']:
        pDisplay.SetRepresentationType('Surface With Edges')

    # =============================================================================
    # Make Clip or Slice
    # =============================================================================
    # create a new 'Clip'
    if ps['clip_coords'].any():

        N_clips = ps['clip_coords'].shape[0]
        clip_coords_surface = copy.deepcopy(ps['clip_coords'])
        pcut = [0] * N_clips
        scut = [0] * N_clips
        pcutDisplay = [0] * N_clips
        scutDisplay = [0] * N_clips

        for i in range(N_clips):
            # shift clip coords of surface a bit to get visability
            for i_shift in range(3):
                if ps['clip_normals'][i, i_shift] > 0:
                    if ps['clip_type'][i] == 'clip':
                        clip_coords_surface[i, i_shift] = copy.deepcopy(ps['clip_coords'][i, i_shift]) - 0.1
                    if ps['clip_type'][i] == 'slice':
                        clip_coords_surface[i, i_shift] = copy.deepcopy(ps['clip_coords'][i, i_shift]) + 0.1

            # clip
            if clip_type[i] == 'clip':

                # Generate clip
                if ps['interpolate']:
                    if thresholding:
                        pcut[i] = paraview.simple.Clip(Input=p1)
                else:
                    if thresholding:
                        pcut[i] = paraview.simple.Clip(Input=t)
                    else:
                        pcut[i] = paraview.simple.Clip(Input=p)

                # init the 'Plane' selected for 'ClipType' (volume)
                pcut[i].ClipType = 'Plane'
                pcut[i].Scalars = [target, ps['quantity']]
                pcut[i].Value = 0.0
                pcut[i].InsideOut = 0
                pcut[i].Crinkleclip = 0
                pcut[i].ClipType.Origin = [ps['clip_coords'][i, 0], ps['clip_coords'][i, 1], ps['clip_coords'][i, 2]]
                pcut[i].ClipType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
                pcut[i].ClipType.Offset = 0.0

            # slice
            elif ps['clip_type'][i] == 'slice':

                # Generate slice
                if ps['interpolate']:
                    if thresholding:
                        pcut[i] = paraview.simple.Slice(Input=p1)
                else:
                    if thresholding:
                        pcut[i] = paraview.simple.Slice(Input=t)
                    else:
                        pcut[i] = paraview.simple.Slice(Input=p)



                # init the 'Plane' selected for 'ClipType' (volume)
                pcut[i].SliceType = 'Plane'
                pcut[i].Crinkleslice = 0
                pcut[i].Triangulatetheslice = 1
                pcut[i].SliceOffsetValues = [0.0]
                pcut[i].SliceType.Origin = [ps['clip_coords'][i, 0], ps['clip_coords'][i, 1], ps['clip_coords'][i, 2]]
                pcut[i].SliceType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
                pcut[i].SliceType.Offset = 0.0

            # Generate slice (surface)
            scut[i] = paraview.simple.Slice(Input=s)

            # init the 'Plane' selected for 'ClipType' (surface)
            scut[i].SliceType = 'Plane'
            scut[i].Crinkleslice = 0
            scut[i].Triangulatetheslice = 1
            scut[i].SliceOffsetValues = [0.0]
            scut[i].SliceType.Origin = [clip_coords_surface[i, 0], clip_coords_surface[i, 1], clip_coords_surface[i, 2]]
            scut[i].SliceType.Normal = [ps['clip_normals'][i, 0], ps['clip_normals'][i, 1], ps['clip_normals'][i, 2]]
            scut[i].SliceType.Offset = 0.0

            # show data in view
            pcutDisplay[i] = Show(pcut[i], renderView)
            scutDisplay[i] = Show(scut[i], renderView)

            # map results to geometry
            #pcutDisplay[i].ColorArrayName = [target, quantity]
            paraview.simple.ColorBy(pcutDisplay[i], (target, ps['quantity']))

            # trace defaults for the display properties.
            pcutDisplay[i].Representation = 'Surface'
            pcutDisplay[i].AmbientColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].ColorArrayName = [None, '']
            pcutDisplay[i].DiffuseColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].LookupTable = None
            pcutDisplay[i].MapScalars = 1
            pcutDisplay[i].InterpolateScalarsBeforeMapping = 1
            pcutDisplay[i].Opacity = 1.0
            pcutDisplay[i].PointSize = 2.0
            pcutDisplay[i].LineWidth = 1.0
            pcutDisplay[i].Interpolation = 'Gouraud'
            pcutDisplay[i].Specular = 0.0
            pcutDisplay[i].SpecularColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].SpecularPower = 100.0
            pcutDisplay[i].Ambient = 0.0
            pcutDisplay[i].Diffuse = 1.0
            pcutDisplay[i].EdgeColor = [0.0, 0.0, 0.5]
            pcutDisplay[i].BackfaceRepresentation = 'Follow Frontface'
            pcutDisplay[i].BackfaceAmbientColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].BackfaceDiffuseColor = [1.0, 1.0, 1.0]
            pcutDisplay[i].BackfaceOpacity = 1.0
            pcutDisplay[i].Position = [0.0, 0.0, 0.0]
            pcutDisplay[i].Scale = [1.0, 1.0, 1.0]
            pcutDisplay[i].Orientation = [0.0, 0.0, 0.0]
            pcutDisplay[i].Origin = [0.0, 0.0, 0.0]
            pcutDisplay[i].Pickable = 1
            pcutDisplay[i].Texture = None
            pcutDisplay[i].Triangulate = 0
            pcutDisplay[i].NonlinearSubdivisionLevel = 1
            pcutDisplay[i].OSPRayUseScaleArray = 0
            pcutDisplay[i].OSPRayScaleArray = ps['quantity']
            pcutDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
            pcutDisplay[i].GlyphType = 'Arrow'
            pcutDisplay[i].SelectionCellLabelBold = 0
            pcutDisplay[i].SelectionCellLabelColor = [0.0, 1.0, 0.0]
            pcutDisplay[i].SelectionCellLabelFontFamily = ps['colorbar_font']
            pcutDisplay[i].SelectionCellLabelFontSize = 18
            pcutDisplay[i].SelectionCellLabelItalic = 0
            pcutDisplay[i].SelectionCellLabelJustification = 'Left'
            pcutDisplay[i].SelectionCellLabelOpacity = 1.0
            pcutDisplay[i].SelectionCellLabelShadow = 0
            pcutDisplay[i].SelectionPointLabelBold = 0
            pcutDisplay[i].SelectionPointLabelColor = [1.0, 1.0, 0.0]
            pcutDisplay[i].SelectionPointLabelFontFamily = ps['colorbar_font']
            pcutDisplay[i].SelectionPointLabelFontSize = 18
            pcutDisplay[i].SelectionPointLabelItalic = 0
            pcutDisplay[i].SelectionPointLabelJustification = 'Left'
            pcutDisplay[i].SelectionPointLabelOpacity = 1.0
            pcutDisplay[i].SelectionPointLabelShadow = 0
            if ps['clip_type'][i] == 'clip':
                pcutDisplay[i].ScalarOpacityUnitDistance = 1.702063581347167
                pcutDisplay[i].SelectMapper = 'Projected tetra'
            pcutDisplay[i].GaussianRadius = 0.0
            pcutDisplay[i].ShaderPreset = 'Sphere'
            pcutDisplay[i].Emissive = 0
            pcutDisplay[i].ScaleByArray = 0
            if ps['interpolate']:
                pcutDisplay[i].SetScaleArray = [target, ps['quantity']]
                pcutDisplay[i].OpacityArray = [target, ps['quantity']]
            else:
                pcutDisplay[i].SetScaleArray = [None, '']
                pcutDisplay[i].OpacityArray = [None, '']
            pcutDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
            pcutDisplay[i].OpacityByArray = 0
            pcutDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'

            # init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
            pcutDisplay[i].OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'Arrow' selected for 'GlyphType'
            pcutDisplay[i].GlyphType.TipResolution = 6
            pcutDisplay[i].GlyphType.TipRadius = 0.1
            pcutDisplay[i].GlyphType.TipLength = 0.35
            pcutDisplay[i].GlyphType.ShaftResolution = 6
            pcutDisplay[i].GlyphType.ShaftRadius = 0.03
            pcutDisplay[i].GlyphType.Invert = 0

            # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
            pcutDisplay[i].ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
            pcutDisplay[i].OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

            # change representation type
            if ps['edges']:
                pcutDisplay[i].SetRepresentationType('Surface With Edges')

            # Apply all settings from volume slices to surface slices
            scutDisplay[i] = pcutDisplay[i]

            # set scalar coloring
            paraview.simple.ColorBy(pcutDisplay[i], (target, ps['quantity']))

            # rescale color and/or opacity maps used to include current data range
            pcutDisplay[i].RescaleTransferFunctionToDataRange(True)

            # show color bar/color legend
            pcutDisplay[i].SetScalarBarVisibility(renderView, True)

    # =============================================================================
    # Disable selected elements for final view
    # =============================================================================
    if ps['interpolate']:
        if thresholding:
            Hide(t, renderView)
            Hide(p1, renderView)
        else:
            Hide(p, renderView)
    else:
        if thresholding:
            Hide(p, renderView)

    # turn off orientation axes
    if not (ps['axes']):
        renderView.OrientationAxesVisibility = 0

    # =============================================================================
    # Setup colormap and colorbar
    # =============================================================================
    # get color transfer function/color map for 'quantity'
    eLUT = GetColorTransferFunction(ps['quantity'])
    # eLUT.LockDataRange = 0  # not in v5.8 anymore
    eLUT.InterpretValuesAsCategories = 0
    eLUT.ShowCategoricalColorsinDataRangeOnly = 0
    eLUT.RescaleOnVisibilityChange = 0
    eLUT.EnableOpacityMapping = 0
    eLUT.UseLogScale = 0
    if ps['interpolate']:
        eLUT.ColorSpace = 'RGB'
    else:
        eLUT.ColorSpace = 'RGB' #'Diverging'
    eLUT.ColorSpace = 'Diverging'
    eLUT.UseBelowRangeColor = 0
    eLUT.BelowRangeColor = [0.0, 0.0, 0.0]
    eLUT.UseAboveRangeColor = 0
    eLUT.AboveRangeColor = [1.0, 1.0, 1.0]
    eLUT.NanColor = ps['NanColor']
    eLUT.Discretize = 1
    eLUT.NumberOfTableValues = 256
    eLUT.ScalarRangeInitialized = 1.0
    eLUT.HSVWrap = 0
    eLUT.VectorComponent = 0
    eLUT.VectorMode = 'Magnitude'
    eLUT.AllowDuplicateScalars = 1
    eLUT.Annotations = []
    eLUT.ActiveAnnotatedValues = []
    eLUT.IndexedColors = []

    # set opacity transfer function/opacity map for 'quantity'
    ePWF = GetOpacityTransferFunction(ps['quantity'])
    if not(ps['opacitymap']==[]):
        eLUT.EnableOpacityMapping = 1
        ePWF.Points = ps['opacitymap']
    ePWF.AllowDuplicateScalars = 1
    ePWF.ScalarRangeInitialized = 1

    colormap_presets = {'Cool to Warm',
                        'Cool to Warm (Extended)',
                        'Blue to Red Rainbow',
                        'X Ray',
                        'Grayscale',
                        'jet',
                        'hsv',
                        'erdc_iceFire_L',
                        'Plasma (matplotlib)',
                        'Viridis (matplotlib)',
                        'gray_Matlab',
                        'Spectral_lowBlue',
                        'Rainbow Blended White'
                        'BuRd'}

    if type(ps['colormap']) is str:
        # set colorbar to 'jet' if not specified in presets
        if not (ps['colormap'] in colormap_presets):
            print((
                'Changing colormap to \'jet\' since user specified colormap \'{}\' is not part of the included presets ...').format(
            ps['colormap']))
            colormap = 'jet'

        if ps['colormap'] == 'b2rcw':
            rgb_values = b2rcw(ps['datarange'][0], ps['datarange'][1])
            rgb_data = np.linspace(ps['datarange'][0], ps['datarange'][1], rgb_values.shape[0])
            eLUT.RGBPoints = np.hstack((rgb_data,rgb_values))
        else:
            # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
            eLUT.ApplyPreset(ps['colormap'], True)
    else:
        eLUT.RGBPoints = ps['colormap']

    # =============================================================================
    # colorbar
    # =============================================================================
    # get color legend/bar for eLUT in view renderView
    eLUTColorBar = GetScalarBar(eLUT, renderView)
    if ps['colorbar_position']:
        eLUTColorBar.Position = ps['colorbar_position']
    else:
        eLUTColorBar.Position = [0.85, 0.05]
    # eLUTColorBar.Position2 = [0.12, 0.43]  #'Position2' is obsolete as of ParaView 5.4. Use the 'ScalarBarLength' property to set the length instead.
    eLUTColorBar.AutoOrient = 1
    eLUTColorBar.Orientation = ps['colorbar_orientation']
    eLUTColorBar.Title = ps['quantity']
    eLUTColorBar.ComponentTitle = 'Magnitude'
    eLUTColorBar.TitleJustification = 'Centered'
    eLUTColorBar.TitleColor = ps['colorbar_labelcolor']
    eLUTColorBar.TitleOpacity = 1.0
    eLUTColorBar.TitleFontFamily = ps['colorbar_font']
    eLUTColorBar.TitleBold = 0
    eLUTColorBar.TitleItalic = 0
    eLUTColorBar.TitleShadow = 0
    eLUTColorBar.LabelColor = ps['colorbar_labelcolor']
    eLUTColorBar.LabelOpacity = 1.0
    eLUTColorBar.LabelFontFamily = ps['colorbar_font']
    eLUTColorBar.LabelBold = 0
    eLUTColorBar.LabelItalic = 0
    eLUTColorBar.LabelShadow = 0
    eLUTColorBar.AutomaticLabelFormat = 0
    eLUTColorBar.LabelFormat = ps['colorbar_labelformat']
    # eLUTColorBar.NumberOfLabels = ps['colorbar_numberoflabels']  # not in v5.8 anymore
    eLUTColorBar.DrawTickMarks = 1
    # eLUTColorBar.DrawSubTickMarks = 1  # not in v5.8 anymore
    eLUTColorBar.DrawTickLabels = 1
    eLUTColorBar.AddRangeLabels = 1
    eLUTColorBar.RangeLabelFormat = ps['colorbar_labelformat']
    eLUTColorBar.DrawAnnotations = 1
    eLUTColorBar.AddRangeAnnotations = 0
    eLUTColorBar.AutomaticAnnotations = 0
    eLUTColorBar.DrawNanAnnotation = 0
    eLUTColorBar.NanAnnotation = 'NaN'
    eLUTColorBar.TextPosition = 'Ticks right/top, annotations left/bottom'
    # eLUTColorBar.AspectRatio = ps['colorbar_aspectratio']  # paraview.NotSupportedException: 'AspectRatio' is obsolete as of ParaView 5.4. Use the 'ScalarBarThickness' property to set the width instead.
    eLUTColorBar.Title = ps['colorbar_label']
    eLUTColorBar.ComponentTitle = ''
    eLUTColorBar.TitleFontSize = ps['colorbar_titlefontsize']
    eLUTColorBar.LabelFontSize = ps['colorbar_labelfontsize']


    # Rescale transfer function
    if ps['datarange']:
        eLUT.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])
        ePWF.RescaleTransferFunction(ps['datarange'][0], ps['datarange'][1])

    # camera placement for renderView
    if len(ps['view']) == 4:
        renderView.CameraPosition = ps['view'][0]
        renderView.CameraFocalPoint = ps['view'][1]
        renderView.CameraViewUp = ps['view'][2]
        renderView.CameraParallelScale = ps['view'][3][0]
    else:
        renderView.ResetCamera()

    # =============================================================================
    # coil
    # =============================================================================
    if ps['fname_vtu_coil'] and ps['show_coil']:
        # load coil .vtu file and create a new 'XML Unstructured Grid Reader'
        coil = paraview.simple.XMLUnstructuredGridReader(FileName=[ps['fname_vtu_coil']])
        coil.PointArrayStatus = ['magnitude']

        # show data in view
        coilDisplay = paraview.simple.Show(coil, renderView)

        # trace defaults for the display properties.
        coilDisplay.ColorArrayName = [None, '']
        coilDisplay.OSPRayScaleArray = 'magnitude'
        coilDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilDisplay.ScalarOpacityUnitDistance = 170.51694871976824
        coilDisplay.SetScaleArray = ['POINTS', 'magnitude']
        coilDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilDisplay.OpacityArray = ['POINTS', 'magnitude']
        coilDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # create a new 'Glyph'
        coilGlyph = paraview.simple.Glyph(Input=coil, GlyphType='Arrow')
        coilGlyph.Scalars = ['POINTS', 'None']
        coilGlyph.Vectors = ['POINTS', 'None']
        coilGlyph.ScaleFactor = 14.657378544
        coilGlyph.GlyphTransform = 'Transform2'
        coilGlyph.GlyphMode = 'All Points'

        # set active source
        paraview.simple.SetActiveSource(coilGlyph)

        # set dipole scaling and size
        if ps['coil_dipole_scaling'][0] == 'scaled':
            coilGlyph.Scalars = ['POINTS', 'magnitude']
            coilGlyph.ScaleMode = 'scalar'
        else:
            coilGlyph.ScaleMode = 'off'

        coilGlyph.ScaleFactor = ps['coil_dipole_scaling'][1]

        # show data in view
        coilGlyphDisplay = paraview.simple.Show(coilGlyph, renderView)

        # trace defaults for the display properties.
        coilGlyphDisplay.ColorArrayName = [None, '']
        coilGlyphDisplay.OSPRayScaleArray = 'magnitude'
        coilGlyphDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
        coilGlyphDisplay.GlyphType = 'Sphere'
        coilGlyphDisplay.SetScaleArray = ['POINTS', 'magnitude']
        coilGlyphDisplay.ScaleTransferFunction = 'PiecewiseFunction'
        coilGlyphDisplay.OpacityArray = ['POINTS', 'magnitude']
        coilGlyphDisplay.OpacityTransferFunction = 'PiecewiseFunction'

        # set dipole color
        if isinstance(ps['coil_dipole_color'], (str,)):
            # set scalar coloring
            paraview.simple.ColorBy(coilGlyphDisplay, ('POINTS', 'magnitude'))

            # rescale color and/or opacity maps used to include current data range
            coilGlyphDisplay.RescaleTransferFunctionToDataRange(True)

            # show color bar/color legend
            coilGlyphDisplay.SetScalarBarVisibility(renderView, True)

            # get color transfer function/color map for 'magnitude'
            magnitudeLUT = paraview.simple.GetColorTransferFunction('magnitude')
            magnitudeLUT.ColorSpace = 'HSV'
            magnitudeLUT.ScalarRangeInitialized = 1.0
            # magnitudeLUT.RGBPoints = [1.16477014, 0.0, 0.0, 1.0, 8.77717169, 1.0, 0.0, 0.0]
            magnitudeLUT.NanColor = ps['NanColor']

            # get opacity transfer function/opacity map for 'magnitude'
            magnitudePWF = paraview.simple.GetOpacityTransferFunction('magnitude')
            magnitudePWF.ScalarRangeInitialized = 1
            # magnitudePWF.Points = [1.16477014, 0.0, 0.5, 0.0, 8.77717169, 1.0, 0.5, 0.0]

            # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
            magnitudeLUT.ApplyPreset(ps['coil_dipole_color'], True)
        else:
            coilGlyphDisplay.DiffuseColor = ps['coil_dipole_color']

        # hide data in view
        paraview.simple.Hide(coil, renderView)

        # show data in view
        coilGlyphDisplay = paraview.simple.Show(coilGlyph, renderView)

        # hide color bar/color legend
        coilGlyphDisplay.SetScalarBarVisibility(renderView, False)

        # =============================================================
        # set coil axes direction
        # =============================================================
        if ps['coil_axes']:
            # Get number of dipoles
            N_dip = coil.GetClientSideObject().GetOutput().GetNumberOfElements(0)

            # Extract points coordinates
            points = [coil.GetClientSideObject().GetOutput().GetPoint(i) for i in range(N_dip)]
            points_array = np.asarray(points)

            # determine coil center
            coil_center = np.average(points_array, axis=0)

            # shift coil to center for SVD
            points_array = points_array - coil_center

            line = [0] * 3
            lineDisplay = [0] * 3
            line_color = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            U, s, V = np.linalg.svd(points_array, full_matrices=True)
            points_transform = np.dot(points_array, V.transpose())
            coil_dim = np.max(points_transform, axis=0) - np.min(points_transform, axis=0)

            for i in range(3):
                # create a new 'Line'
                line[i] = paraview.simple.Line()
                # Properties modified on line1
                line[i].Point1 = coil_center
                if ((i == 0) or (i == 1)):
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[i] / 2
                if i == 2:
                    line[i].Point2 = coil_center + V[i, :] / np.linalg.norm(V[i, :]) * coil_dim[0] / 2
                line[i].Resolution = 1000
                # set active source
                SetActiveSource(line[i])
                # show data in view
                lineDisplay[i] = Show(line[i], renderView)
                # trace defaults for the display properties.
                lineDisplay[i].ColorArrayName = [None, '']
                lineDisplay[i].OSPRayScaleArray = 'Texture Coordinates'
                lineDisplay[i].OSPRayScaleFunction = 'PiecewiseFunction'
                lineDisplay[i].GlyphType = 'Sphere'
                lineDisplay[i].SetScaleArray = [None, '']
                lineDisplay[i].ScaleTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].OpacityArray = [None, '']
                lineDisplay[i].OpacityTransferFunction = 'PiecewiseFunction'
                lineDisplay[i].ShaderPreset = 'Gaussian Blur (Default)'
                lineDisplay[i].DiffuseColor = line_color[i]
                lineDisplay[i].SetRepresentationType('3D Glyphs')
                lineDisplay[i].GlyphType.Radius = 1.0

    # =============================================================================
    # plot parameters
    # =============================================================================

    # set the background color
    renderView.Background = ps['background_color']

    # set image size
    renderView.ViewSize = ps['viewsize']  # [width, height]

    # save scene
    paraview.simple.SaveScreenshot(ps['fname_png'], magnification=ps['png_resolution'], quality=100, view=renderView)

    # crop surrounding of image
    crop_image(ps['fname_png'], ps['fname_png'])

    # Reset Paraview session
    ResetSession()


def write_vtu_mult(fname, data_labels, points, triangles, tetrahedras, idx_start, *data):
    """
    Writes data in triangles and tetrahedra centers into .vtu file, which can be loaded with Paraview.

    Parameters
    ----------
    fname : str
        Name of .vtu file (incl. path)
    data_labels : list of str [N_data]
        Label of each dataset
    points : nparray of float [N_points x 3]
        Coordinates of vertices
    triangles : nparray of int [N_tri x 3]
        Connectivity of points forming triangles
    tetrahedras : nparray of int [N_tri x 4]
        Connectivity of points forming tetrahedra
        idx_start: int
        smallest index in connectivity matrix, defines offset w.r.t python
        indexing, which starts at '0'
    *data : nparray(s) [N_tet x N_comp(N_data)]
        Arrays containing data in tetrahedra center
        multiple components per dataset possible e.g. [Ex, Ey, Ez]

    Returns
    -------
    <File> : .vtu file
        Geometry and data information
    """

    # this saves triangles and tetrahedras in one vtu file.
    # data-vectors have to have the same length as len(triangles) + len(tetrahedres)
    # first: triangles, second: tetrahedras.

    N_points = points.shape[0]
    N_ele = triangles.shape[0] + tetrahedras.shape[0]
    triangles_type = 5
    tetrahedra_type = 10

    # determine number of components in data arguments
    N_data = len(data)
    # print(len(data))
    N_comp = np.zeros(len(data)).astype(int)

    for i in range(len(data)):
        if hasattr(data[i], 'ndim'):
            N_comp[i] = data[i].shape[1] if data[i].ndim > 1 else 1
        else:
            N_comp[i] = 1

    # open output file
    f = open(fname, 'w')

    # write .vtu header
    f.write(
        '<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')

    # specify grid-type
    f.write('<UnstructuredGrid>\n')
    f.write(
        '<Piece NumberOfPoints="{:d}" NumberOfCells="{:d}">\n'.format(N_points, N_ele))

    # write point data (not used here)
    f.write('<PointData>\n')
    f.write('</PointData>\n')

    # write cell data (data)
    # =============================================================================
    f.write('<CellData Scalars="scalars">\n')
    for i_data in range(N_data):
        f.write('<DataArray type="Float64" Name="{}" NumberOfComponents="{:d}" format="ascii">\n'.format(
            data_labels[i_data], N_comp[i_data]))
        np.savetxt(f, data[i_data], '%1.8f')  # data
        f.write('</DataArray>\n')
    f.write('</CellData>\n')

    # write point coordinates of vertices
    # =============================================================================
    f.write('<Points>\n')
    f.write(
        '<DataArray type="Float64" Name="Points" NumberOfComponents="3" format="ascii">\n')
    np.savetxt(f, points, '%1.8f')  # points
    f.write('</DataArray>\n')
    f.write('</Points>\n')

    # write cell information
    # =============================================================================
    f.write('<Cells>\n')

    # tetrahedras and triangles
    f.write('<DataArray type="Int64" Name="connectivity" format="ascii">\n')
    # tetrahedra (has to start with 0)
    np.savetxt(f, triangles - idx_start, '%d')
    # tetrahedra (has to start with 0)
    np.savetxt(f, tetrahedras - idx_start, '%d')
    f.write('</DataArray>\n')

    # offset
    f.write('<DataArray type="Int64" Name="offsets" format="ascii">\n')
    # offset (3,6,9,...) for triangles or (4,8,12,...) for tetrahedra
    np.savetxt(f, triangles.shape[
        1] * np.linspace(1, triangles.shape[0], triangles.shape[0]), '%d')
    np.savetxt(f, triangles.shape[0] * 3 + tetrahedras.shape[1] * np.linspace(
        1, tetrahedras.shape[0], tetrahedras.shape[0]), '%d')  # add last triangles offset to all tets
    f.write('</DataArray>\n')

    # type of cells
    f.write('<DataArray type="UInt8" Name="types" format="ascii">\n')
    # type 5 (triangles) or 10 (tetrahedra)
    np.savetxt(f, triangles_type * np.ones((triangles.shape[0], 1)), '%d')
    # type 5 (triangles) or 10 (tetrahedra)
    np.savetxt(f, tetrahedra_type * np.ones((tetrahedras.shape[0], 1)), '%d')
    f.write('</DataArray>\n')

    f.write('</Cells>\n')

    # end of file
    # =============================================================================
    f.write('</Piece>\n')
    f.write('</UnstructuredGrid>\n')
    f.write('</VTKFile>')
    f.close()


def write_vtu(fname, data_labels, points, connectivity, idx_start, data):
    """
    Writes data in tetrahedra centers into .vtu file, which can be loaded with Paraview.

    Parameters
    ----------
    fname : str
        Name of .vtu file (incl. path)
    data_labels : list with N_data str
        Label of each dataset
    points : array of float [N_points x 3]
        Coordinates of vertices
    connectivity : array of int [N_tet x 4]
        Connectivity of points forming tetrahedra
    idx_start : int
        Smallest index in connectivity matrix, defines offset w.r.t Python indexing, which starts at '0'
    *data : array(s) [N_tet x N_comp(N_data)]
        Arrays containing data in tetrahedra center multiple components per dataset possible e.g. [Ex, Ey, Ez]

    Returns
    -------
    <File> : .vtu file
        Geometry and data information
    """

    N_points = points.shape[0]
    N_ele = connectivity.shape[0]
    if connectivity.shape[1] == 3:
        ele_type = 5  # triangles
    elif connectivity.shape[1] == 4:
        ele_type = 10  # tetrahedra
    else:
        raise RuntimeError('Error in connectivity matrix!')

    # determine number of components in data arguments
    N_data = len(data)
    N_comp = np.zeros(len(data)).astype(int)

    for i in range(len(data)):
        N_comp[i] = data[i].shape[1] if data[i].ndim > 1 else 1

    # open output file
    f = open(fname, 'w')

    # write .vtu header
    f.write('<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')

    # specify grid-type
    f.write('<UnstructuredGrid>\n')
    f.write('<Piece NumberOfPoints="{:d}" NumberOfCells="{:d}">\n'.format(N_points, N_ele))

    # write point data (not used here)
    f.write('<PointData>\n')
    f.write('</PointData>\n')

    # write cell data (data)
    # =============================================================================
    f.write('<CellData Scalars="scalars">\n')
    for i_data in range(N_data):
        f.write('<DataArray type="Float64" Name="{}" NumberOfComponents="{:d}" format="ascii">\n'.format(
            data_labels[i_data], N_comp[i_data]))
        np.savetxt(f, data[i_data], '%1.8f')  # data
        f.write('</DataArray>\n')
    f.write('</CellData>\n')

    # write point coordinates of vertices
    # =============================================================================
    f.write('<Points>\n')
    f.write(
        '<DataArray type="Float64" Name="Points" NumberOfComponents="3" format="ascii">\n')
    np.savetxt(f, points, '%1.8f')  # points
    f.write('</DataArray>\n')
    f.write('</Points>\n')

    # write cell information
    # =============================================================================
    f.write('<Cells>\n')

    # tetrahedra
    f.write('<DataArray type="Int64" Name="connectivity" format="ascii">\n')
    # tetrahedra (has to start with 0)
    np.savetxt(f, connectivity - idx_start, '%d')
    f.write('</DataArray>\n')

    # offset
    f.write('<DataArray type="Int64" Name="offsets" format="ascii">\n')
    # offset (3,6,9,...) for triangles or (4,8,12,...) for tetrahedra
    np.savetxt(f, connectivity.shape[1] * np.linspace(1, N_ele, N_ele), '%d')
    f.write('</DataArray>\n')

    # type of cells
    f.write('<DataArray type="UInt8" Name="types" format="ascii">\n')
    # type 5 (triangles) or 10 (tetrahedra)
    np.savetxt(f, ele_type * np.ones((N_ele, 1)), '%d')
    f.write('</DataArray>\n')

    f.write('</Cells>\n')

    # end of file
    # =============================================================================
    f.write('</Piece>\n')
    f.write('</UnstructuredGrid>\n')
    f.write('</VTKFile>')
    f.close()


def write_vtu_coilpos(fname_geo, fname_vtu):
    """
    Read dipole data of coil (position and magnitude of each dipole) from geo file and store it as vtu file.

    Parameters
    ----------
    fname_geo : str
        .geo file from SimNIBS.
    fname_vtu : str
        .vtu output file. Nodes and nodedata.

    Returns
    -------
    <File> : .vtu file
        Magnetic dipoles of the TMS coil
    """

    # regex magic: get all floats from line, discard other stuff
    regexp = '.*?([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'
    dipoles = np.fromregex(fname_geo,
                           regexp,
                           [('x', np.float_),
                            ('y', np.float_),
                            ('z', np.float_),
                            ('mag', np.float_)])
    dipoles.astype(np.float_)
    points = []
    mag = []

    # this is ugly, but it's monday
    for i in range(len(dipoles)):
        points.append([dipoles[i][0], dipoles[i][1], dipoles[i][2]])
        mag.append(dipoles[i][3])

    # some variables for the vtu file
    N_points = len(points)
    N_ele = 1
    f = open(fname_vtu, 'w')

    f.write(
        '<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n'
    )

    # specify grid-type
    f.write('<UnstructuredGrid>\n')
    f.write(
        '<Piece NumberOfPoints="{:d}" NumberOfCells="{:d}">\n'.format(N_points, N_ele)
    )

    # write point data
    f.write('<PointData>\n')
    f.write('<DataArray type="Float64" Name="magnitude" NumberOfComponents="1" format="ascii">\n')
    np.savetxt(f, mag, '%1.8f')  # data
    f.write('</DataArray>\n')
    f.write('</PointData>\n')

    f.write('<CellData Scalars="scalars">\n')
    # not used here
    f.write('</CellData>\n')

    f.write('<Points>\n')
    f.write(
        '<DataArray type="Float64" Name="Points" NumberOfComponents="3" format="ascii">\n')
    np.savetxt(f, points, '%1.8f')  # points
    f.write('</DataArray>\n')
    f.write('</Points>\n')

    # write cell information
    # we define one cell which consist of every point, as vtu needs cells to access points.
    f.write('<Cells>\n')
    f.write('<DataArray type="Int64" Name="connectivity" format="ascii">')
    np.savetxt(f, list(range(N_points)), fmt='%d', delimiter=' ')  # 1 2 3 4 ... N_Points
    f.write('</DataArray>\n')
    f.write('<DataArray type="Int64" Name="offsets" format="ascii">\n')
    f.write(str(N_points))
    f.write('</DataArray>\n')
    f.write('<DataArray type="UInt8" Name="types" format="ascii">\n')
    f.write('2\n')  # element type 2: no lines, just points
    f.write('</DataArray>\n')
    f.write('</Cells>\n')

    # end of file
    #######################################################################
    f.write('</Piece>\n')
    f.write('</UnstructuredGrid>\n')
    f.write('</VTKFile>')
    f.close()
