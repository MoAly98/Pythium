import rootpy, uuid, ROOT, logging
from copy import copy
from rootpy.plotting       import Hist, Hist2D, Hist3D, \
                                  HistStack, F1, F2, F3,\
                                  Canvas, Pad, set_style, Legend
from rootpy.plotting.utils import draw, get_limits
from rootpy.plotting.hist  import  _Hist
from rootpy.plotting.hist  import  HistStack as HS
from rootpy                import ROOTError, asrootpy
from math                  import log, exp, pow
from utils.colours         import *
from utils.file            import walkFile
from utils.draw            import applyDrawOptions
from utils.log             import setupLogger

class BasicPlot(object):
    logger = logging.getLogger( __name__ + '.BasicPlot' )
    def __init__(self, name, title=False, verbose=logging.INFO, **kwargs):
        """Base class for plot objects
        Initialise with BasicPlot(name)
        Params:
        @ name   : Name of the object
        @ title  : Title for the plot
        @ verbose: Verbosity level for logger
        @ kwargs : keyword arguments which override existing options

        Objects can be added by the addObject function and this will automatically
        place the object in a relevant store until the draw phase.

        To generate a plot, the draw function will draw and save your relevant plot.
        This draw function will call upon some internal functions:
        __initPlot__   : which initates the canvas and pad required
        __drawObjects__: which iteratively plots all objects in objects stores
        __drawText__   : which draws text objects including legends
        __finalise__   : which rearranges the sizes of objects
        __save__       : which saves the canvas to file
        """
        # Basic properties
        self.name   = name
        self.title  = title if title else name
        self.logger.setLevel(verbose)
        self.logger.info('Setting up %s named %s', green('BasicPlot'), blue(self.name))

        # Stores containing plottables
        self.canvas     = False
        self.pad        = False
        self.legend     = False
        # Final plottables (requires a list)
        self.objects    = []
        self.objects_2d = []
        self.objects_3d = []
        # Intermediates (internal functions will flush to objects lists)
        self.stacked    = {}
        self.stacked_2d = {}
        self.uncs       = {}

        # Internal canvas properties
        self.width = 600
        self.height = 600
        self.upperFraction = 0.4

        # Legend attributes
        self.drawLegend = True
        self.legend_header = '#it{SABRE-PoP}'
        self.legend_attrs = {}
        self.legend_attrs['leftmargin' ]= 0.1
        self.legend_attrs['rightmargin']= 0.1
        self.legend_attrs['topmargin'  ]= 0.04
        self.legend_attrs['textsize'   ]= 0.03
        self.legend_attrs['entrysep'   ]= 0.3
        self.legend_attrs['entryheight']= 0.2
        self.legend_elements = 0

        # Style attributes (currently requires AtlasStyle files - to be removed)
        #set_style('ATLAS')
        ROOT.gROOT.LoadMacro('AtlasStyle.C')
        ROOT.SetAtlasStyle()
        ROOT.TGaxis.SetMaxDigits( 4 ) 

        # kwargs overwrite default args
        for key, arg in kwargs.iteritems():
            setattr(self, key, arg)

    def getAxis(self):
        return self.canvas.axes()

    def addObject(self, obj, title=False, shape_only=False, stacked=False, skip_legend=False, **kwargs):
        """Function which adds histograms to the correct stores
        Params:
        @ obj        : Plottable object (Hist, Graph, Profile, Hist2D, ect.)
        @ title      : Title for the legend
        @ stacked    : A string indicating the name of the stack. If it doesn't exist
                       it will be created and stored in the stacked dictionary
        @ skip_legend: Flag to skip addition of object to legend
        @ kwargs     : keyword arguments for applying draw options
        """
        # Apply draw options, default line is grey
        obj = obj.Clone()
        if 'drawstyle' in kwargs.keys() and kwargs['drawstyle'] == 'HIST':
            obj.linecolor = 'gray'
        if kwargs.keys():
            obj = applyDrawOptions(obj, **kwargs)

        # Set title
        if title: obj.SetTitle(title)

        # Initialise legend and add entry
        if not self.legend:
            self.__initLegend__(pad=self.pad)
        obj = obj.Clone()
        if not skip_legend:
            self.legend.AddEntry(obj, title)
            self.legend_elements += 1

        # Add 1D histos to objects, 2D to objects_2d
        # Stacked objects go to stacked and stacked_2d respectively
        if shape_only: obj.Scale(1./obj.Integral())
        if isinstance(obj, ROOT.THStack):
            self.stacked[obj.GetName()] = obj
            return
        if obj.GetDimension() == 1:
            #stacked = kwargs['stacked'] if 'stacked' in kwargs.keys() else stacked
            if stacked:
                if not stacked in self.stacked.keys():
                    self.stacked[stacked] = HistStack(name=stacked, title=stacked)
                self.stacked[stacked].Add(obj)
                self.logger.debug('Adding %s to the stack %s', blue(obj), green(self.stacked[stacked]))
            else:
                self.objects.append(obj)
                self.logger.debug('Adding %s to the objects', blue(obj))
        elif obj.GetDimension() == 2:
            self.objects_2d.append(obj)
        elif obj.GetDimension() == 3:
            self.objects_3d.append(obj)


    def makeStackUnc(self, name, **kwargs):
        """Helper function which creates a total histogram from a HistStack
        Params:
        @ name   : Name of histogram to store
        @ kwargs : Draw options for uncertainty histogram (from HistStack)
        """
        # Take histograms and sum to one total histogram
        hists = self.stacked[name].GetHists()
        for i, hist in enumerate(hists):
            if i == 0: total = hist.Clone()
            else: total.Add(hist)

        # Apply draw options and rename with 'unc_<NAME>'
        total = applyDrawOptions(total, **kwargs)
        total.SetName('unc_%s' % name)
        
        # Add to store and add new entry to legend
        self.uncs[name] = total
        self.objects.append(total)
        self.legend.AddEntry(total, 'Stat Unc\n (%s)' % name)
        self.legend_elements += 1

    def __initPlot__(self, name = False, pad = False):
        """Initialisation function. Creates canvas and pads
        Params:
        @ name       : Name of the plot, overwrites self.name
        @ pad        : A Pad object which is used to plot to. 
                       Either pass as (xmin, ymin, xmax, ymax, name) or as a Pad object.
        """
        # Set name of canvas and create canvas
        if not name: name = self.name
        if not self.canvas:
            self.canvas = Canvas(name=name, title=self.title, width=self.width, height=self.height)
            self.logger.info('Initialising canvas %s' % blue(self.canvas))

        # Create pad otherwise take from self.canvas
        if pad and pad.__class__.__name__ == 'Pad':
            self.pad = pad
        elif pad and len(pad) == 5:
            self.pad = Pad(pad[0], pad[1], pad[2], pad[3], name=pad[4])
        elif pad and not type(pad) == list:
            self.logger.warn(red('Pad requested makes no sense: %s' % pad))
            help(self.__initPlot__)
            self.logger.warn(red('Deriving default pad'))
            self.pad = self.canvas.cd()
        else:
            self.pad = self.canvas.cd()
        self.logger.info('Initialising pad %s' % blue(self.pad))
        self.pad.Draw()


    def __initLegend__(self, pad = False, legend_attrs=False):
        """Initialisation function of legend object. Legend attributes 
        Params:
        @ pad        : The pad object to plot to. Default goes to current pad.
        @ legend_attrs : Legend attributes which overwrite the stored attributes
        """
        if not self.legend:
            if not legend_attrs: legend_attrs = self.legend_attrs
            self.logger.debug('Initialising legend')
            pad = self.pad if self.pad else None
            self.legend = Legend([], pad=pad, header=self.legend_header, **legend_attrs)
        
    def __drawObjects__(self, **kwargs):
        """Main function for drawing histograms.
        Stacked objects will be passed to the objects store.
        Objects are plotted in order of 2D -> Stacks -> 1D
        Params:
        @ kwargs : Draw options for objects store (1D only)
        """
        # Add stacks to objects
        if self.stacked.keys() > 0:
            for stack_name, item in self.stacked.iteritems():
                self.objects.append(item)
                self.logger.debug('Adding stack %s to %s.objects to draw', blue(stack_name), green(self.name))
        if self.stacked_2d.keys() > 0:
            for _, item in self.stacked_2d.iteritems():
                self.objects_2d.append(item)
                self.logger.debug('Adding stack %s to %s.objects_2d to draw', blue(stack_name), green(self.name))

        # Draw elements
        # Priority: TH3 > TH2 > TStack > TH1
        axis_titles = {}
        if 'xtitle' in kwargs:
            axis_titles['X'] = kwargs['xtitle']
        if 'ytitle' in kwargs:
            axis_titles['Y'] = kwargs['ytitle']
        if 'ztitle' in kwargs:
            axis_titles['Z'] = kwargs['ztitle']
        if self.objects_3d:
            self.logger.info(green('Drawing all 3D objects'))
            self.__draw3DHistograms__(axis_titles)
        if self.objects_2d:
            self.logger.info(green('Drawing all 2D objects'))
            self.__draw2DHistograms__(axis_titles)
        if self.objects:
            self.logger.info(green('Drawing all 1D objects'))
            self.__drawHistograms__(**kwargs)


    def __drawHistograms__(self, **kwargs):
        """Main function for drawing 1D histograms.
        Plots are drawn with the stack first.
        Params:
        @ kwargs : Draw options for objects store (1D only)
        """
        # rootpy implementation
        # If stack, reverse order... draw stack first
        objs = copy(self.objects)
        if self.stacked.keys():
            objs.reverse()
        if not objs: return

        # Determine if elements exist or not
        plots_on = 0
        for element in self.pad.find_all_primitives():
            if isinstance(element, ROOT.TH1):
                plots_on += 1
        
        # Set log on stack

        # Set titles and pad to draw to
        if not 'ytitle' in kwargs:
            kwargs['ytitle'] = 'Events'
        if not 'pad' in kwargs:
            kwargs['pad'] = self.pad
        
        # Padding for legend elements
        # For information look up get_limits function in rootpy
        # Set the upper y padding as upperFraction, no padding below
        if not 'ypadding' in kwargs.keys():
            kwargs['ypadding'] = (self.upperFraction, 0.)
        #kwargs['logy_crop_value'] = 1e-1

        # Plot objects
        self.logger.info('Drawing 1D objects %s' % green(objs) )
        if plots_on > 0:
            draw(objs, same=True, **kwargs)
        else:
            draw(objs, **kwargs)

    def __draw2DHistograms__(self, axis_titles={}):
        """Main function for drawing 2D histograms.
        Extra space is made for 2D histogram with COLZ option
        """
        # PyROOT implementation since plotting.utils.draw 
        # doesn't support 2D objects
        # TODO Draw options for 2D hists

        # If stack, reverse order... draw stack first
        objs = copy(self.objects_2d)
        if self.stacked_2d.keys():
            objs.reverse()

        # Draw objects
        self.pad.cd()
        for i, obj in enumerate(objs):
            if axis_titles:
                for axis, title in axis_titles.iteritems():
                    exec( 'obj.Get%saxis().SetTitle("%s")' % (axis,title))
            if i==0 and 'Z' in obj.drawstyle:
                self.pad.Update()
                self.pad.SetRightMargin( 0.17 )
                obj.GetZaxis().SetTitle('Events')
            if i == 0 and self.pad.find_all_primitives() == 1:
                obj.Draw()
            else:
                obj.Draw("SAME")
            self.logger.info('Drawing 2D object %s' % green(obj) )
        return obj[0]

    def __draw3DHistograms__(self, axis_titles={}):
        """Main function for drawing 3D histograms.
        Extra space is made for 3D histogram with COLZ option
        """
        # PyROOT implementation since plotting.utils.draw 
        # doesn't support 3D objects
        # TODO Draw options for 3D hists

        # If stack, reverse order... draw stack first
        objs = copy(self.objects_3d)

        # Draw objects
        self.pad.cd()
        for i, obj in enumerate(objs):
            if axis_titles:
                for axis, title in axis_titles.iteritems():
                    exec( 'obj.Get%saxis().SetTitle("%s")' % (axis,title))
            if i == 0 and self.pad.find_all_primitives() == 1:
                obj.draw()
            else:
                obj.draw("SAME")
            self.logger.info('Drawing 3D object %s' % green(obj) )
        return obj[0]

    def __drawText__(self, border=False):
        """Draw legend object (should be drawn to appropriate pad)
        """
        # TODO Add support for more text elements
        # BUG rootpy can't acces primitives correctly in some cases (weird)
        if self.drawLegend:
            if border:
                self.legend.SetBorderSize(1)
                self.legend.SetFillColor(0)
                self.legend.SetFillStyle(1001)
            else:
                self.legend.SetBorderSize(0)
            if self.legend_elements > 5:
                self.legend.SetNColumns(2)
            elif self.legend_elements > 8:
                self.legend.SetNColumns(3)
            elif self.legend_elements > 11:
                self.legend.SetNColumns(4)
            self.pad.cd()
            self.legend.Draw()

    def __finalise__(self, fixAxis={}):
        """Function to finalise object placement and scaling
        Params:
        @ fixAxis : Dictionary to re-size primitives on canvas
        """
        # Taking final elements
        for obj in self.pad.find_all_primitives():
            if not isinstance(obj, ROOT.TH1): continue

            # Fix according to fixAxis dictionary
            for axis, resize_dict in fixAxis.iteritems():
                for attr, val in resize_dict.iteritems():
                    if axis == 'histo':
                        getattr(obj, attr)(val)
                    else:
                        #getattr(getattr(obj, 'Get%saxis' % axis), attr)(val) 
                        # VERY HACKY!
                        exec( 'obj.Get%saxis().%s(%s)' % (axis,attr,val))

        try:
            self.pad.Update()
        except ROOTError:
            pass
            
        try:
            self.canvas.Update()
        except ROOTError:
            pass


    def save(self, name='test.eps'):
        """Function to save canvas to file
        Params:
        @ name : String or list of names of files to save
        """
        def save_canvas(name):
            # Hack because of weird rootpy issue
            try:
                self.canvas.SaveAs(name)
            except ROOTError:
                self.logger.warn('Ignore this message if related to log Y axis')
        if type(name) == str:
            save_canvas(name)
        elif type(name) == list:
            map(save_canvas, name)
        else:
            self.logger.warn('What have you given me to save? %s' % red(name))


    def draw(self, name='test.eps',**kwargs):
        """Main draw function
        Params:
        @ name : String or list of names of file
        @ name : String or list of names
        """
        self.__initPlot__()
        self.__drawObjects__(**kwargs)
        self.__drawText__()
        self.__finalise__()
        self.save(name)

class RatioPlot(BasicPlot):
    logger = logging.getLogger( __name__ + '.RatioPlot' )
    def __init__(self, name, title = '', verbose=logging.INFO):
        """Simple class for plotting Ratio plots
        Initialise with RatioPlot(name)
        Params:
        @ name   : Name of the object
        @ title  : Title for the plot
        @ verbose: Verbosity level for logger

        Objects can be added the same way as for BasicPlot but specifying which
        pad you wish to plot to with plotOn = 'lower' or plotOn = 'upper'.

        The class consists of two BasicPlot elements self.upper and self.lower. 
        Each inherits the same functionality from BasicPlot.

        To generate a plot, the draw function will draw and save your relevant plot.
        This draw function inherits from the base function.

        Helper functions are redefined with options to setNumerator or setDenominator to 
        create a ratio with the new helper function makeRatio.

        Otherwise draw utilises the same base internal functions but with modifications 
        to accommodate the second ratio plot.
        """

        # Initialise with taller frame, with upper and lower.
        BasicPlot.__init__(self, name, title, width = 600, height = 650)
        self.logger.info('Setting up %s named %s', green('RatioPlot'), blue(self.name))
        self.upper = BasicPlot(name+'_upper', upperFraction=0.4, verbose=verbose)
        self.upper.legend_attrs['topmargin'] += -0.02
        self.lower = BasicPlot(name+'_lower', verbose=verbose)
        self.upperFraction = 0.75
        self.lowerFraction = 0.20

        # Internal store for ratio elements
        self.numerator   = False
        self.denominator = False
        self.ratio = {}
        self.ratio_unc = {}

    def __initPlot__(self):
        """Initialisation function. Creates canvas for total plot and pads in self.upper
        and self.lower to store the individual components of the plot
        """
        BasicPlot.__initPlot__( self )
        self.upper.__initPlot__(pad=(0.0,1.-self.upperFraction,1.0,1.0, self.name+'_upper'))
        low_start = (1.-self.upperFraction-self.lowerFraction)/2.
        self.lower.__initPlot__(pad=(0.0,low_start,1.0,self.lowerFraction+low_start, self.name+'_lower'))

        self.upper.pad.Draw()
        self.lower.pad.Draw()

    def addObject(self, obj, title=None, shape_only=False, stacked = False, skip_legend=False, plotOn='upper', setNumerator=False, setDenominator=False, **kwargs):
        """Inherits same functionality as addObject for BasicPlot but with three extra options.
        Params:
        @ plotOn : Indicates which pad you wish to plot onto
        @ setNumerator   : Sets the histogram as the numerator of ratio
        @ setDenominator : Sets the histogram as the denominator of ratio
        """
        if not plotOn in ['upper', 'lower']:
            self.logger.warn('Where do you want me to plot? Only "upper" or "lower" accepted. You gave me %s' % red(plotOn) )
        getattr(self, plotOn).addObject(obj, title, shape_only, stacked, skip_legend, **kwargs)
        if setNumerator:
            self.numerator   = getattr(self, plotOn).objects[-1]
            self.logger.debug('Adding %s to %s' % (blue(self.numerator), green('numerator')))
        if setDenominator:
            self.denominator = getattr(self, plotOn).objects[-1]
            self.logger.debug('Adding %s to %s' % (blue(self.numerator), green('denominator')))

    def makeStackUnc(self, name, setNumerator=False, setDenominator=False, plotOn='upper', **kwargs):
        """Inherits same functionality as makeStackUnc for BasicPlot but with two extra parameters.
        Params:
        @ setNumerator   : Sets the histogram as the numerator of ratio
        @ setDenominator : Sets the histogram as the denominator of ratio
        """
        getattr(self, plotOn).makeStackUnc(name, **kwargs)
        if setNumerator:
            self.numerator   = getattr(self, plotOn).uncs[name]
            self.logger.debug('Adding %s to %s' % (blue(self.numerator), green('numerator')))
        if setDenominator:
            self.denominator = getattr(self, plotOn).uncs[name]
            self.logger.debug('Adding %s to %s' % (blue(self.denominator), green('denominator')))

    def __drawObjects__(self, **kwargs):
        """Runs __drawObjects__ on the resepective pads
        Params:
        @ kwargs : arguments to pass to both upper and lower
        """
        # Draw to respective pads
        # Upper
        self.logger.info('Drawing %s elements' % blue('upper'))
        kwargs['pad'] = self.upper.pad
        self.upper.__drawObjects__(**kwargs)
        # Lower (do NOT draw logscale)
        self.logger.info('Drawing %s elements' % blue('lower'))
        kwargs['pad'] = self.lower.pad
        kwargs['logy'] = False
        self.lower.__drawObjects__(**kwargs)

    def __finalise__(self, logy=False):
        """Runs __finalise__ on the resepective pads. Axes can be fixed by passing dictionaries to
        the __finalise__ functions of the respective pads. 

        This procedure has been optimised but feel free to tinker with.
        """
        self.upper.pad.SetBottomMargin(0.016)
        self.lower.pad.SetTopMargin   (0.050)
        self.lower.pad.SetBottomMargin(0.4)

        fixLower = {'X': {'SetLabelSize': 0.19, 'SetTitleSize': 0.19, 'SetTitleOffset': 0.8}, 
                    'Y': {'SetLabelSize': 0.19, 'SetTitleSize': 0.19, 'SetTitleOffset': 0.3, 'SetTitle': "'Data/MC'", 'SetNdivisions': 403},
                    'histo': {'SetMinimum': 0.8, 'SetMaximum': 1.2}}

        fixUpper = {'X': {'SetLabelSize': 0., 'SetTitleSize': 0.}}

        self.upper.__finalise__(fixUpper)
        self.lower.__finalise__(fixLower)

        self.canvas.Update()

    def __drawText__(self):
        """Draw text only for upper pad.
        """
        self.upper.__drawText__()
    
    def makeRatio(self, numerator=False, denominator=False, with_uncs=False, add_lower=True):
        """Helper function to make ratio plot and add to lower plot.
        Params:
        @ numerator   : Pass histogram otherwise will retrieve from self.numerator
        @ denominator : Pass histogram otherwise will retrieve from self.denominator
        @ with_uncs   : Automatically adds an object from denominator to lower plot (properly divided)
        @ add_lower   : Flag to add to lower plot automatically
        """
        # Determine numerator and denominator histos
        numerator   = numerator   if numerator   else self.numerator
        denominator = denominator if denominator else self.denominator

        if not numerator:
            self.logger.warn(red('Numerator not specified! Skipping ratio!'))
            return
        if not denominator:
            self.logger.warn(red('Denominator not specified! Skipping ratio!'))
            return
            
        # Create ratio of two histos
        self.logger.info('Adding ratio of %s and %s' % (blue(numerator), blue(denominator)))
        ratio_name = numerator.GetName()+'_DIVIDE_'+denominator.GetName()
        self.ratio[ratio_name] = numerator.Clone()
        self.ratio[ratio_name].Divide(denominator)
        self.ratio[ratio_name].SetName(ratio_name)

        # Add to lower plot automatically
        if add_lower:
            self.lower.addObject(self.ratio[ratio_name], title = 'Total', 
                                linecolor='black', linestyle='solid', drawstyle='E0', legendstyle='LEP', skip_legend=True)

        # Create and add uncertainty band to lower plot
        if with_uncs:
            self.ratio['unc_%s' % denominator.GetName()] = denominator.Clone()
            self.ratio['unc_%s' % denominator.GetName()].Divide(denominator)
            self.lower.addObject(self.ratio['unc_%s' % denominator.GetName()], title = 'Total', 
                                 linecolor='black', linestyle='solid', drawstyle='E2', legendstyle='PL', skip_legend=True)


    def draw(self, name='test.eps',**kwargs):
        self.__initPlot__()
        self.__drawObjects__(**kwargs)
        self.__drawText__()
        logy = kwargs['logy'] if 'logy' in kwargs else False
        self.__finalise__(logy)
        self.save(name)

class Profile2Dto1DPlot(BasicPlot):
    def __init__(self, name, title = '', verbose=logging.INFO):
        # Initialise with taller frame, with upper and lower.
        BasicPlot.__init__(self, name, title, width = 700, height = 700)
        self.logger.info('Setting up %s named %s', green('Profile2Dto1DPlot'), blue(self.name))
        self. main = BasicPlot(name+'_main', verbose=verbose)
        self.xplot = BasicPlot(name+'_x',    verbose=verbose)
        self.yplot = BasicPlot(name+'_y',    verbose=verbose)
        self.mainFraction = 0.75
        self.sideFraction = 0.20

    def __initPlot__(self):
        """Initialisation function. Creates canvas for total plot and pads in self.upper
        and self.lower to store the individual components of the plot
        """
        BasicPlot.__initPlot__( self )
        #self. main.__initPlot__()#pad=(0.0,0.0,1.0,1.0, self.name+'_main'))
        self. main.__initPlot__(pad=(0.0,0.0,0.8,0.8, self.name+'_main'))
        self.xplot.__initPlot__(pad=(0.0,0.8,0.8,1.0, self.name+'_x')   )
        self.yplot.__initPlot__(pad=(0.8,0.0,1.0,0.8, self.name+'_y')   )

        self.xplot.pad.Draw()
        self.yplot.pad.Draw()
        self. main.pad.Draw()

    def addObject(self, obj, title=False, shape_only=False, stacked = False, skip_legend=False, plotOn='main', setNumerator=False, setDenominator=False, **kwargs):
        """Inherits same functionality as addObject for BasicPlot but with three extra options.
        Params:
        @ plotOn         : Indicates which pad you wish to plot onto
        @ setNumerator   : Sets the histogram as the numerator of ratio
        @ setDenominator : Sets the histogram as the denominator of ratio
        """
        if not plotOn in ['main', 'xplot', 'yplot']:
            self.logger.warn('Where do you want me to plot? Only "main" or "xplot" or "yplot" accepted. You gave me %s' % red(plotOn) )
        getattr(self, plotOn).addObject(obj, title, shape_only, stacked, skip_legend, **kwargs)
        #self.main.addObject(obj, title, shape_only, stacked, skip_legend, **kwargs)

    def makeSidePlots(self, **kwargs):
        fillstyle_order = ['/', '\\', '|', '-', '*', 'o']
        for i, obj in enumerate(self.main.objects_2d):
            kwargs['fillstyle'] = fillstyle_order[i % len(fillstyle_order)]
            kwargs['drawstyle'] = 'HBAR'
            self.yplot.addObject(asrootpy(obj.ProjectionY()), title=self.title+'_y', skip_legend=True, fillcolor=obj.GetLineColor(), **kwargs)
            kwargs['drawstyle'] =  'BAR'
            self.xplot.addObject(asrootpy(obj.ProjectionX()), title=self.title+'_x', skip_legend=True, fillcolor=obj.GetLineColor(), markersize=0., **kwargs)

    def makeProfilePlots(self, **plot_style):
        for obj in self.main.objects_2d:
            self.main.addObject(asrootpy(obj.ProfileX()), plotOn='main', linecolor=obj.GetLineColor() , markercolor=obj.GetLineColor(), skip_legend=True, **plot_style)
        
    def __drawObjects__(self, **kwargs):
        """Runs __drawObjects__ on the resepective pads
        Params:
        @ kwargs : arguments to pass to both upper and lower
        """
        # Draw to respective pads
        # Main
        self.logger.info('Drawing %s elements' % blue('main'))
        kwargs['pad'] = self.main.pad
        self.main.__drawObjects__(**kwargs)
        # xplot 
        self.logger.info('Drawing %s elements' % blue('xplot'))
        kwargs['pad'] = self.xplot.pad
        self.xplot.__drawObjects__(**kwargs)
        # yplot
        self.logger.info('Drawing %s elements' % blue('yplot'))
        kwargs['pad'] = self.yplot.pad
        self.yplot.__drawObjects__(**kwargs)

    def __finalise__(self, logy=False):
        """Runs __finalise__ on the resepective pads. Axes can be fixed by passing dictionaries to
        the __finalise__ functions of the respective pads. 

        This procedure has been optimised but feel free to tinker with.
        """
        self.main.pad.SetTopMargin    (0.0)
        self.main.pad.SetRightMargin  (0.0)
        self.xplot.pad.SetBottomMargin(0.0)
        self.xplot.pad.SetRightMargin (0.0)
        self.yplot.pad.SetTopMargin   (0.0)
        self.yplot.pad.SetLeftMargin  (0.0)

        fixSideX = {'X': {'SetLabelSize': 0.00, 'SetTitleSize': 0.00, 'SetTitleOffset': 0.8}, 
                    'Y': {'SetLabelSize': 0.19, 'SetTitleSize': 0.19, 'SetTitleOffset': 0.4, 'SetTitle': "'Events'", 'SetNdivisions': 403}}

        fixSideY = {'X': {'SetLabelSize': 0.00, 'SetTitleSize': 0.00, 'SetTitleOffset': 0.8}, 
                    'Y': {'SetLabelSize': 0.19, 'SetTitleSize': 0.19, 'SetTitleOffset': 0.4, 'SetLabelOffset': 0., 'SetTitle': "'Events'", 'SetNdivisions': 401}}

        fixMain = {'X': {'SetTitle': "'xtitle'"},
                   'Y': {'SetTitle': "'ytitle'"}
                  }

        self.main .__finalise__(fixMain)
        self.xplot.__finalise__(fixSideX)
        self.yplot.__finalise__(fixSideY)

        self.canvas.Update()

    def __drawText__(self):
        """Draw text only for main pad.
        """
        self.main.__drawText__(border=1)
    
    def draw(self, name='test.eps',**kwargs):
        self.__initPlot__()
        self.__drawObjects__(**kwargs)
        self.__drawText__()
        logy = kwargs['logy'] if 'logy' in kwargs else False
        self.__finalise__(logy)
        self.save(name)

class Profile3Dto2DPlot(BasicPlot):
    def __init__(self, name, title = '', verbose=logging.INFO):
        # Initialise with taller frame, with upper and lower.
        BasicPlot.__init__(self, name, title, width = 700, height = 700)
        self.logger.info('Setting up %s named %s', green('Profile2Dto1DPlot'), blue(self.name))
        self. main  = BasicPlot(name+'_main', verbose=verbose, drawLegend=True)
        self.yxplot = BasicPlot(name+'_xy',   verbose=verbose, drawLegend=False)
        self.zyplot = BasicPlot(name+'_yz',   verbose=verbose, drawLegend=False)
        self.zxplot = BasicPlot(name+'_xz',   verbose=verbose, drawLegend=False)
        self.mainFraction = 0.75
        self.sideFraction = 0.20
        self.drawLegend = False

    def __initPlot__(self):
        """Initialisation function. Creates canvas for total plot and pads in self.upper
        and self.lower to store the individual components of the plot
        """
        BasicPlot.__initPlot__( self )
        self.  main.__initPlot__(pad=(0.0,0.0,0.5,0.5, self.name+'_main'))
        self.yxplot.__initPlot__(pad=(0.0,0.5,0.5,1.0, self.name+'_xy'  ))
        self.zyplot.__initPlot__(pad=(0.5,0.0,1.0,0.5, self.name+'_yz'  ))
        self.zxplot.__initPlot__(pad=(0.5,0.5,1.0,1.0, self.name+'_xz'  ))

        self.zxplot.pad.Draw()
        self.zyplot.pad.Draw()
        self.zxplot.pad.Draw()
        self.  main.pad.Draw()

    def addObject(self, obj, title=False, shape_only=False, stacked = False, skip_legend=False, plotOn='main', **kwargs):
        """Inherits same functionality as addObject for BasicPlot but with one extra option.
        Params:
        @ plotOn         : Indicates which pad you wish to plot onto
        """
        if not plotOn in ['main', 'yxplot', 'zyplot', 'zxplot']:
            self.logger.warn("Where do you want me to plot? Only 'main', 'yxplot', 'zyplot', 'zxplot' accepted. You gave me %s" % red(plotOn) )
        if not skip_legend: self.drawLegend = True
        getattr(self, plotOn).addObject(obj, title, shape_only, stacked, skip_legend, **kwargs)

    def makeProfilePlots(self, **kwargs):
        for obj in self.main.objects_3d:
            self.yxplot.addObject(asrootpy(obj.Project3DProfile('yx')), title=obj.GetTitle()+'_yx', plotOn='yx', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
            self.zyplot.addObject(asrootpy(obj.Project3DProfile('zy')), title=obj.GetTitle()+'_zy', plotOn='zy', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
            self.zxplot.addObject(asrootpy(obj.Project3DProfile('zx')), title=obj.GetTitle()+'_zx', plotOn='zx', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
        
    def makeProjectionPlots(self, **kwargs):
        for obj in self.main.objects_3d:
            self.yxplot.addObject(asrootpy(obj.Project3D('yx')), title=obj.GetTitle()+'_yx', plotOn='yx', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
            self.zyplot.addObject(asrootpy(obj.Project3D('zy')), title=obj.GetTitle()+'_zy', plotOn='zy', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
            self.zxplot.addObject(asrootpy(obj.Project3D('zx')), title=obj.GetTitle()+'_zx', plotOn='zx', linecolor=obj.GetMarkerColor() , markercolor=obj.GetMarkerColor(), skip_legend=True, **kwargs)
        
    def __drawObjects__(self, **kwargs):
        """Runs __drawObjects__ on the resepective pads
        Params:
        @ kwargs : arguments to pass to both upper and lower
        """
        # Draw to respective pads
        # Main
        self.logger.info('Drawing %s elements' % blue('main'))
        kwargs['pad'] = self.main.pad
        self.main.__drawObjects__(**kwargs)
        # yxplot 
        self.logger.info('Drawing %s elements' % blue('yxplot'))
        kwargs['pad'] = self.yxplot.pad
        self.yxplot.__drawObjects__(**kwargs)
        # zyplot 
        self.logger.info('Drawing %s elements' % blue('zyplot'))
        kwargs['pad'] = self.zyplot.pad
        self.zyplot.__drawObjects__(**kwargs)
        # zxplot 
        self.logger.info('Drawing %s elements' % blue('zxplot'))
        kwargs['pad'] = self.zxplot.pad
        self.zxplot.__drawObjects__(**kwargs)

    def __finalise__(self, logy=False, **axis_title):
        """Runs __finalise__ on the resepective pads. Axes can be fixed by passing dictionaries to
        the __finalise__ functions of the respective pads. 

        This procedure has been optimised but feel free to tinker with.
        """
        fixMain   = {'X': {'SetTitle': "'%s'" % axis_title['xtitle']}, 
                     'Y': {'SetTitle': "'%s'" % axis_title['ytitle']}, 
                     'Z': {'SetTitle': "'%s'" % axis_title['ztitle']}
                     }
        fixyxplot = {'X': {'SetTitle': "'%s'" % axis_title['xtitle']}, 
                     'Y': {'SetTitle': "'%s'" % axis_title['ytitle']}
                     }
        fixzyplot = {'X': {'SetTitle': "'%s'" % axis_title['ytitle']}, 
                     'Y': {'SetTitle': "'%s'" % axis_title['ztitle']}
                     }
        fixzxplot = {'X': {'SetTitle': "'%s'" % axis_title['xtitle']}, 
                     'Y': {'SetTitle': "'%s'" % axis_title['ztitle']}
                     }

        self.yxplot.__finalise__(fixyxplot)
        self.zyplot.__finalise__(fixzyplot)
        self.zxplot.__finalise__(fixzxplot)
        self.main  .__finalise__(fixMain  )

        self.canvas.Update()

    def __drawText__(self):
        """Draw text only for main pad.
        """
        for plot in [self.main, self.yxplot, self.zyplot, self.zxplot]:
            if plot.drawLegend:
                plot.pad.cd()
                plot.__drawText__(border=1)
    
    def draw(self, name='test.eps',**kwargs):
        self.__initPlot__()
        self.__drawObjects__(**kwargs)
        self.__drawText__()
        logy = kwargs['logy'] if 'logy' in kwargs else False
        axis_title = {'xtitle': False, 'ytitle': False, 'ztitle': False}
        for axis in axis_title.keys():
            if axis in kwargs.keys():
                axis_title[axis] = kwargs[axis] 
        self.__finalise__(logy, **axis_title)
        self.save(name)



if __name__ == "__main__":
    # Data
    histA = Hist(20, -100., 100., fillcolor='red')  .FillRandom(F1('TMath::Gaus(x,-10.,10.)' ) , 500)
    histB = Hist(20, -100., 100., fillcolor='blue') .FillRandom(F1('TMath::Gaus(x, 10.,10.)' ) , 300)
    histC = Hist(20, -100., 100., fillcolor='green').FillRandom(F1('TMath::Gaus(x,  0.,10.)' ) , 800)
    hist2D_A = Hist2D(10, -100., 100., 10, -100., 100.).FillRandom(F2('(x-1.)**2+y**2'), 10000)
    hist2D_B = Hist2D(10, -100., 100., 10, -100., 100.).FillRandom(F2('(y-100.)**2+10.0*x**2'), 10000)
    hist3D_A = Hist3D(10, -100., 100., 10, -100., 100., 10, -100., 100.).FillRandom(F3('(x-30.)**2+(y+10.)**2+z**2'), 10000)
    hist3D_B = Hist3D(10, -100., 100., 10, -100., 100., 10, -100., 100.).FillRandom(F3('(x+30.)**2+(y-10.)**2+z**2'), 10000)

    # Standard plot
    plot_style = {'fillstyle': 'solid', 'drawstyle': 'HIST', 'legendstyle': 'F', 'stacked': 'Background'}
    example = BasicPlot('test1')
    example.__initPlot__()
    example.addObject(histA, title = 'Sample A', fillcolor=9001     , **plot_style)
    example.addObject(histB, title = 'Sample B', fillcolor=ROOT.kRed, **plot_style)
    example.addObject(histC, title = 'Sample C', linecolor='black', linestyle='dashed', drawstyle='E0', legendstyle='LEP')
    example.makeStackUnc('Background', fillstyle='\\', fillcolor='black', drawstyle='E2', markersize=0.)
    example.draw('test1.eps', xtitle='#varphi', ytitle='Events')#, logy=True)
    del example

    # 2D plot on top of 1D plot
    legend_attrs = {}
    legend_attrs['leftmargin' ]= 0.1
    legend_attrs['rightmargin']= 0.1
    legend_attrs['topmargin'  ]= 0.5
    legend_attrs['textsize'   ]= 0.03
    legend_attrs['entrysep'   ]= 0.3
    legend_attrs['entryheight']= 0.2
    example = BasicPlot('test2', legend_attrs=legend_attrs)
    example.__initPlot__()
    example.addObject(hist2D_A, title = 'Sample A', skip_legend =True, drawstyle='COLZ')
    example.addObject(histC,    title = 'Sample C', linecolor='red', linestyle='dashed', drawstyle='E0', legendstyle='LEP')
    example.draw('test2.eps', xtitle='#varphi', ytitle='#theta')#, logy=True)
    del example

    # Ratio plot
    ex_ratio = RatioPlot('test3')
    ex_ratio.__initPlot__()
    ex_ratio.addObject(histA, title = 'Sample A', fillcolor=9001     , plotOn='upper', **plot_style)
    ex_ratio.addObject(histB, title = 'Sample B', fillcolor=ROOT.kRed, plotOn='upper', **plot_style)
    ex_ratio.makeStackUnc('Background', fillstyle='\\', fillcolor='black', markersize=0., drawstyle='E2', plotOn='upper', setDenominator=True)
    ex_ratio.addObject(histC, title = 'Sample C', linecolor='black', linestyle='solid', drawstyle='E0', legendstyle='LEP', plotOn='upper', setNumerator=True)
    ex_ratio.makeRatio(with_uncs=True)
    ex_ratio.draw('test3.eps', xtitle='#varphi', ytitle='Events')#, logy=True)
    del ex_ratio

    # 2D projection/profile plot
    plot_style = {'drawstyle': 'CONT3', 'legendstyle': 'L'}
    example = Profile2Dto1DPlot('test4')
    example.__initPlot__()
    example.addObject(hist2D_A, title = 'Main A', plotOn='main', linecolor='red' , **plot_style)
    example.addObject(hist2D_B, title = 'Main B', plotOn='main', linecolor='blue', **plot_style)
    example.makeSidePlots()
    example.makeProfilePlots()
    example.draw('test4.eps', xtitle='x title', ytitle='y title')
    del example

    example = Profile3Dto2DPlot('test5')
    example.__initPlot__()
    example.addObject(hist3D_A, title = 'Sample A', plotOn='main', markersize=0.05, markercolor='red' , linecolor='red' , legendstyle = 'LEP', drawstyle='E')
    example.addObject(hist3D_B, title = 'Sample B', plotOn='main', markersize=0.05, markercolor='blue', linecolor='blue', legendstyle = 'LEP', drawstyle='E')
    example.makeProjectionPlots(drawstyle = 'CONT2')
    example.draw('test5.eps', xtitle='x title', ytitle='y title', ztitle='z title')
    del example
