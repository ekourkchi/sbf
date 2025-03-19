from .utils import *


def generate_mask():
    
    # create residual images for Source Extractor
    monsta_script = """
        rd 1 '"""+g_var+"""'
        rd 2 '"""+z_var+"""'
        clip 1 nan=0
        clip 2 nan=0
        rd 10 '"""+PS_circlemask+"""'
        mi 1 10
        mi 2 10
        box 1 nc=550 nr=550 cc=1500 cr=1500
        wind 1 box=1
        wind 2 box=1
        wd 1 '"""+outFolder+name+"""gvar.nonan'
        wd 2 '"""+outFolder+name+"""zvar.nonan'
        
        rd 1 '"""+g_fits+"""'
        rd 2 '"""+z_fits+"""'
        clip 1 nan=0
        clip 2 nan=0
        wd 1 '"""+outFolder+name+"""g.nonan'
        wd 2 '"""+outFolder+name+"""z.nonan'

        set nr="""+R1+"""/10$nint
        string nr '%i2.0' nr
        cop 3 1
        cop 4 2
        elliprof 3 model rmstar x0=1500 y0=1500 r0=7 r1="""+R1+""" nr=nr niter=5
        elliprof 4 model rmstar x0=1500 y0=1500 r0=7 r1="""+R1+""" nr=nr niter=5
        cop 5 1
        si 5 3
        cop 6 2
        si 6 4
        wd 5 '"""+outFolder+name+"""g.resid'
        wd 6 '"""+outFolder+name+"""z.resid'
        rd 10 '"""+PS_circlemask+"""'
        ac 5 500.
        ac 6 500.
        mi 5 10
        mi 6 10
        wind 5 box=1
        wind 6 box=1
        wd 5 '"""+outFolder+name+"""g.zoom.resid'
        wd 6 '"""+outFolder+name+"""z.zoom.resid'
    """
    run_monsta(monsta_script, 'monsta.pro', 'monsta.log')
