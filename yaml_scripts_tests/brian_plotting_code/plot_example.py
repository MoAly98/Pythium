import logging
from utils.plotting import BasicPlot, RatioPlot
from utils.file     import walkFile
from utils.log      import setupLogger
from rootpy         import asrootpy
from random         import gauss
from utils.colours  import *

if __name__ == "__main__":
    hist_store, files = {}, {}
    for isotope in ['Pb212', 'Pb214', 'Bi210', 'Bi212', 'Bi214', 'K40']:#, 'Ac228']:
        hist_store[isotope], files[isotope] = walkFile('/coepp/cephfs/share/sabre/forFederico/Lumirror_%s.root' % isotope)

    logger = setupLogger('plotting', __name__, logging.DEBUG)

    plot_style = {'fillstyle': 'solid', 'drawstyle': 'HIST', 'legendstyle': 'F', 'stacked': 'Background'}

    example = BasicPlot('test1')
    example.__initPlot__()
    example.addObject(hist_store['Bi210']['CrystalSignal']['phi'], title = 'Bi 210', fillcolor=9016, **plot_style)
    example.addObject(hist_store['Pb212']['CrystalSignal']['phi'], title = 'Pb 212', fillcolor=9001, **plot_style)
    example.addObject(hist_store['Pb214']['CrystalSignal']['phi'], title = 'Pb 214', fillcolor=9002, **plot_style)
    example.addObject(hist_store['Bi212']['CrystalSignal']['phi'], title = 'Bi 212', fillcolor=9005, **plot_style)
    example.addObject(hist_store['Bi214']['CrystalSignal']['phi'], title = 'Bi 214', fillcolor=9008, **plot_style)
    example.addObject(hist_store['K40']  ['CrystalSignal']['phi'], title = 'K40',    fillcolor=9010, fillstyle='/', drawstyle='HIST', legendstyle='F')
    example.makeStackUnc('Background', fillstyle='\\', fillcolor='black', drawstyle='E2')
    example.draw('test1.eps', xtitle='#varphi', ytitle='Events', logy=True)
    del example

    logger.info(red("##############################################################################"))
    example = BasicPlot('test2')
    example.__initPlot__()
    example.addObject(hist_store['Pb212']['CrystalSignal']['theta_vs_phi_var_xbin'], title = 'Pb 212', linecolor=9001,  drawstyle='CONT2', legendstyle='L')
    example.addObject(hist_store['Pb214']['CrystalSignal']['theta_vs_phi_var_xbin'], title = 'Pb 214', linecolor='red', drawstyle='CONT2', legendstyle='L')
    example.addObject(asrootpy(hist_store['Pb212']['CrystalSignal']['theta_vs_phi_var_xbin'].ProfileX()), title = 'Profile X', linecolor='forestgreen', legendstyle='L')
    example.draw('test2.eps', xtitle='#varphi', ytitle='#theta')#, logy=True)
    del example

    logger.info(red("##############################################################################"))
    example = RatioPlot('test3')
    example.__initPlot__()
    example.addObject(hist_store['Bi210']['CrystalSignal']['phi'], title = 'Bi 210', fillcolor=9016, plotOn='upper', **plot_style)
    example.addObject(hist_store['Pb212']['CrystalSignal']['phi'], title = 'Pb 212', fillcolor=9001, plotOn='upper', **plot_style)
    example.addObject(hist_store['Pb214']['CrystalSignal']['phi'], title = 'Pb 214', fillcolor=9002, plotOn='upper', **plot_style)
    example.addObject(hist_store['Bi212']['CrystalSignal']['phi'], title = 'Bi 212', fillcolor=9005, plotOn='upper', **plot_style)
    example.addObject(hist_store['Bi214']['CrystalSignal']['phi'], title = 'Bi 214', fillcolor=9008, plotOn='upper', **plot_style)
    example.addObject(hist_store['K40']  ['CrystalSignal']['phi'], title = 'K40',    fillcolor=9010, plotOn='upper', **plot_style)
    example.makeStackUnc('Background', fillstyle='\\', fillcolor='black', drawstyle='E2', plotOn='upper', setDenominator=True)
    # Dummy data
    for i in example.upper.uncs['Background'].bins_range():
        example.upper.uncs['Background'].SetBinError(i, example.upper.uncs['Background'].GetBinError(i)*10)
    data = example.upper.uncs['Background'].Clone()
    for i in data.bins_range():
        data.SetBinContent(i, data.GetBinContent(i)*gauss(1,0.2))
    data.SetName('data')

    example.addObject(data, title='Data', drawstyle='E0', linecolor='black', linestyle='solid', legendstyle='LEP', setNumerator=True, plotOn='upper')
    example.makeRatio(with_uncs=True)
    example.draw('test3.eps', xtitle='#varphi', ytitle='Events', logy=True)
    del example
