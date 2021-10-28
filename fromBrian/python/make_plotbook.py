import os
from python.utils.plotbook_templates import presentation, section, subsection, page, end
from python.configs.vars import var_main

tex = ''

tex += presentation.format(full_title='Modelling of JSS variables in Dijet and $\gamma$+jet events', short_title='JSS Variable Modelling')
tex += section.format(section='Dijet')
for name, var in var_main.items():
    title = var.label
    tex += subsection.format(subsection=title)
    tex += page.format(tl='dask_SEP/'+name+'_dnn_cont_50.png', tl_cap='DNN Contained 50\%',
                       bl='dask_SEP/'+name+'_dnn_cont_80.png', bl_cap='DNN Contained 80\%',
                       tc='dask_SEP/'+name+'_dnn_incl_50.png', tc_cap='DNN Inclusive 50\%',
                       bc='dask_SEP/'+name+'_dnn_incl_80.png', bc_cap='DNN Inclusive 80\%',
                       tr='dask_SEP/'+name+'_w_50.png', tr_cap='Smoothed W 50\%',
                       br='dask_SEP/'+name+'_w_80.png', br_cap='Smoothed W 80\%',
                       title='Dijet - '+title)
tex += section.format(section='$\gamma$+jet')
for name, var in var_main.items():
    title = var.label
    tex += subsection.format(subsection=title)
    tex += page.format(tl='dask_JUN_gamma/'+name+'_dnn_cont_50.png', tl_cap='DNN Contained 50\%',
                       bl='dask_JUN_gamma/'+name+'_dnn_cont_80.png', bl_cap='DNN Contained 80\%',
                       tc='dask_JUN_gamma/'+name+'_dnn_incl_50.png', tc_cap='DNN Inclusive 50\%',
                       bc='dask_JUN_gamma/'+name+'_dnn_incl_80.png', bc_cap='DNN Inclusive 80\%',
                       tr='dask_JUN_gamma/'+name+'_w_50.png', tr_cap='Smoothed W 50\%',
                       br='dask_JUN_gamma/'+name+'_w_80.png', br_cap='Smoothed W 80\%',
                       title='$\gamma$+jet - '+title)
tex += end

with open('test.tex', 'w') as f:
    f.write(tex)
