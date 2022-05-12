from plot_classes import *
from datafiles_and_parsers.textfile_data import txt_parser
from datafiles_and_parsers.yamlscript_corrmatrix import corrmatrix_parser
from matplotlib import transforms
from math import ceil



"""
Hist1D
"""
dict1 = {
    'font.size': 10,
    'lines.marker': '.'
}

plot1 = Hist1D(
    samples=['gauss1', 'gauss2', 'gauss3'],
    # data='gauss2',
    # stack=True,
    # errors='hist'
)
plot1.figure_options(figsize=(5,5), mastertitle="Master Title")
plot1.plot_options(rcp_kw=dict1, gridstring='y:', markersize=6)
plot1.fontsize_options(25, 13, 15)
# plot1.color_options(colormap='plasma', reverse=True)
plot1.set_axislabels(12, ymain="Events", xmain=plot.names[0])
plot1.create()
# plot1.saveimage("Hist1D_demo_plasma", 1000)


"""
RatioPlot
"""
plot2 = RatioPlot(
    samples=['gauss1', 'gauss2'], 
    reference='gauss1',
    data='gauss2',
    # stack=True,
    errors='all'
)
# plot2.color_options(['black', 'black'])
plot2.figure_options(spacing=0.02, figsize=(7,6))
plot2.ratio_options([0.5,1.5], 0.5)
# plot2.plot_options(shape='hollow', gridstring='y:')
plot2.set_axislabels(10, ymain="Events", xbot=rplot.names[0])
plot2.create()
# plot2.saveimage("RatioPlot_demo", 1000)


"""
PullPlot
"""
data = txt_parser('tHbb_v31_v3.txt')
numeric_data = data.astype(float)
data0      = numeric_data[numeric_data[1] == 0]
data1      = numeric_data[(numeric_data[1] == 1) & (numeric_data.index != 'gamma_stat_SR_bin_9')]
data_gamma = numeric_data[numeric_data.index == 'gamma_stat_SR_bin_9']

dict3 = {
    'axes.titlesize': 15
}

plot3 = PullPlot(data0.iloc[0:20])
plot3.plot_options(rcp_kw=dict3)
plot3.figure_options(labelside='right')
# plot3.color_options('blue', 'red', 'orange')
# plot3.set_rangex([-6, 11])
plot3.set_axislabels(12, xmain=r'$(\hat{\theta}-\theta)/\Delta\theta$')
plot3.create()
# plot3.saveimage("PullPlot_demo", 1000)


"""
ProjectionPlot
"""
# create boost histogram
v1 = np.random.normal(size=(2, 100_000), scale=0.35)
hist = bh.Histogram(
    bh.axis.Regular(20, -1, 1, metadata='x'),
    bh.axis.Regular(20, -1, 1, metadata='y')
)
hist.fill(*v1)

dict4 = {
    'axes.titlesize': 20,
    'xaxis.labellocation': 'right',
    'yaxis.labellocation': 'top',
}

plot4 = ProjectionPlot(hist)
plot4.figure_options(figsize=(6,6), spacing=0.07)
plot4.plot_options('both:', rcp_kw=dict4)
plot4.set_axislabels(15, ymain=r'$p_y$ [MeV]', xmain=r'$p_x$ [MeV]', xright='righttitle', ytop='toptitle')
plot4.color_options(colormap='binary')
plot4.create()
plot4.saveimage("ProjectionPlot_demo_binary", 1000)


"""
CMatrixPlot
"""
cmdata = corrmatrix_parser('CorrelationMatrix.yaml')

plot5 = CMatrixPlot(cmdata, 0.001)
plot5.fontsize_options(20, 8, 15)
plot5.figure_options(figsize=(9,9))
plot5.create()
plot5.saveimage("CMatrix_demo", 1000)