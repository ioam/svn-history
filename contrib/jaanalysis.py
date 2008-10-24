import numpy 
import __main__

def complex_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    import topo
    from topo.command.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    exec "from topo.analysis.vision import analyze_complexity" in __main__.__dict__

    save_plotgroup("Orientation Preference and Complexity")
    save_plotgroup("Activity")

    # Plot all projections for all measured_sheets
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)
    
    from topo.misc.filepath import normalize_path
    from topo.command.basic import save_snapshot
    save_snapshot(normalize_path('snapshot.typ'))


def v2_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    import topo
    from topo.command.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    exec "from topo.analysis.vision import analyze_complexity" in __main__.__dict__
    from topo.misc.filepath import normalize_path

    topo.sim["V1Simple"].measure_maps = True
    topo.sim["V1Complex"].measure_maps = True
    save_plotgroup("Orientation Preference and Complexity")    

    # Plot all projections for all measured_sheets
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    save_plotgroup("Activity")
#    topo.sim["V1Simple"].measure_maps = False
#    topo.sim["V1Complex"].measure_maps = False
        
    save_plotgroup("Corner OR Preference")
    from topo.command.basic import save_snapshot
    save_snapshot(normalize_path('snapshot.typ'))


activity_history=numpy.array([])
def rf_analysis():
    import topo
    import pylab
    import topo.analysis.vision
    import contrib.jacommands
    from topo.command.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.command.analysis import measure_or_tuning_fullfield, measure_or_pref
    from topo.command.pylabplots import or_tuning_curve_batch
    from topo.misc.filepath import normalize_path    
    
    if(float(topo.sim.time()) <=20010): 
        save_plotgroup("Orientation Preference")
        save_plotgroup("Activity")
    
        # Plot all projections for all measured_sheets
        measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                           if hasattr(s,'measure_maps') and s.measure_maps]
        for s in measured_sheets:
            for p in s.projections().values():
                save_plotgroup("Projection",projection=p)

        prefix="WithGC"   
        measure_or_tuning_fullfield()    
        or_tuning_curve_batch(prefix,"OrientationTC:V1:[0,0]",pylab.plot,"degrees","V1",[0,0],"orientation")     
        or_tuning_curve_batch(prefix,"OrientationTC:V1:[0.1,0.1]",pylab.plot,"degrees","V1",[0.1,0.1],"orientation")    
        or_tuning_curve_batch(prefix,"OrientationTC:V1:[-0.1,-0.1]",pylab.plot,"degrees","V1",[-0.1,-0.1],"orientation")      
        or_tuning_curve_batch(prefix,"OrientationTC:V1:[0.1,-0.1]",pylab.plot,"degrees","V1",[0.1,-0.1],"orientation")     
        or_tuning_curve_batch(prefix,"OrientationTC:V1:[-0.1,0.1]",pylab.plot,"degrees","V1",[-0.1,0.1],"orientation") 
    else:
        topo.command.basic.activity_history = numpy.concatenate((contrib.jacommands.activity_history,topo.sim["V1"].activity.flatten()),axis=1)    

    if(float(topo.sim.time()) == 20000): 
        topo.sim["V1"].plastic=False
        contrib.jacommands.homeostatic_analysis_function()

    if(float(topo.sim.time()) == 21009): 
        pylab.figure()
        pylab.hist(topo.command.basic.activity_history,(numpy.arange(20.0)/20.0))

        pylab.savefig(normalize_path(str(topo.sim.time()) + 'activity_histogram.png'))
        from topo.command.basic import save_snapshot
        save_snapshot(normalize_path('snapshot.typ'))

def saver_function():
    from topo.command.basic import save_snapshot
    save_snapshot(normalize_path('snapshot.typ'))
