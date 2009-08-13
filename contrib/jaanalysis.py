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
    import contrib.jacommands
    exec "from topo.analysis.vision import analyze_complexity" in __main__.__dict__
					
			
    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
							    
    # Set potentially reasonable defaults; not necessarily useful
    topo.command.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.command.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.command.analysis.sheet_name=measured_sheets[0].name
    
    import numpy
    # reset treshold and desable noise before measuring maps
    m = numpy.mean(topo.sim["V1Simple"].output_fns[2].t)
    topo.sim["V1Simple"].output_fns[2].t*=0
    topo.sim["V1Simple"].output_fns[2].t+=m
    sc = topo.sim["V1Simple"].output_fns[1].generator.scale
    topo.sim["V1Simple"].output_fns[1].generator.scale=0.0
    
    #st = topo.sim["V1Complex"].in_connections[0].strength
    #topo.sim["V1Complex"].in_connections[0].strength = 0.0
    
    
									    
    save_plotgroup("Orientation Preference and Complexity")
    save_plotgroup("Activity",normalize=True)

									
    # Plot all projections for all measured_sheets
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    if(float(topo.sim.time()) > 11000.0): 
        topo.command.pylabplots.measure_or_tuning_fullfield.instance(sheet=topo.sim["V1Complex"])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0]",sheet=topo.sim["V1Complex"],coords=[(0,0)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.1)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,0.2)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,0.2)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.0)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.0)])()

    topo.sim["V1Simple"].output_fns[1].generator.scale=sc
    #topo.sim["V1Complex"].in_connections[0].strength=st

def complex_surround_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    import topo
    from topo.command.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    import contrib.jacommands
    exec "from topo.analysis.vision import analyze_complexity" in __main__.__dict__
					
			
    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
							    
    # Set potentially reasonable defaults; not necessarily useful
    topo.command.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.command.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.command.analysis.sheet_name=measured_sheets[0].name
									    
    save_plotgroup("Orientation Preference and Complexity")
    save_plotgroup("Activity",normalize=True)
										
    # Plot all projections for all measured_sheets
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    if(float(topo.sim.time()) > 11000.0): 
        topo.command.pylabplots.measure_or_tuning_fullfield.instance(sheet=topo.sim["V1Complex"])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0]",sheet=topo.sim["V1Complex"],coords=[(0,0)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.1)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,0.2)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,0.2)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.0)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.0)])()
        contrib.jacommands.surround_analysis("V1Complex").analyse(2,10,5)


													    
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
    topo.sim["V2"].measure_maps = True
    
    topo.sim["V2"].in_connections[0].strength=4
    
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
#    save_snapshot(normalize_path('snapshot.typ'))


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
    from topo.command.pylabplots import cyclic_tuning_curve
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
        s=topo.sim["V1"]
        cyclic_tuning_curve(filename_suffix=prefix,filename="OrientationTC:V1:[0,0]",sheet=s,coords=[(0,0)],x_axis="orientation")
        cyclic_tuning_curve(filename_suffix=prefix,filename="OrientationTC:V1:[0.1,0.1]",sheet=s,coords=[(0.1,0.1)],x_axis="orientation")
        cyclic_tuning_curve(filename_suffix=prefix,filename="OrientationTC:V1:[-0.1,-0.1]",sheet=s,coords=[(-0.1,-0.1)],x_axis="orientation")
        cyclic_tuning_curve(filename_suffix=prefix,filename="OrientationTC:V1:[0.1,-0.1]",sheet=s,coords=[(0.1,-0.1)],x_axis="orientation")
        cyclic_tuning_curve(filename_suffix=prefix,filename="OrientationTC:V1:[-0.1,0.1]",sheet=s,coords=[(-0.1,0.1)],x_axis="orientation")
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

def gc_homeo_af():
    import contrib.jsldefs
    import topo.command.pylabplots
    from topo.command.analysis import save_plotgroup
    from topo.analysis.featureresponses import FeatureResponses
    FeatureResponses.repetitions=10
    
    contrib.jsldefs.homeostatic_analysis_function()
    topo.command.pylabplots.fftplot(topo.sim["V1"].sheet_views["OrientationPreference"].view()[0],filename="V1ORMAPFFT")
    print float(topo.sim.time())
    if(float(topo.sim.time()) > 19002.0): 
	#topo.sim["V1"].output_fns[2].scale=0.0
	save_plotgroup("Position Preference")
        topo.command.pylabplots.measure_or_tuning_fullfield.instance(sheet=topo.sim["V1"],repetitions=10)(repetitions=10)
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0]",sheet=topo.sim["V1"],coords=[(0,0)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0.1]",sheet=topo.sim["V1"],coords=[(0.1,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,-0.1]",sheet=topo.sim["V1"],coords=[(0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0.1]",sheet=topo.sim["V1"],coords=[(-0.1,0.1)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,-0.1]",sheet=topo.sim["V1"],coords=[(-0.1,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,0.2]",sheet=topo.sim["V1"],coords=[(0.2,0.2)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,-0.2]",sheet=topo.sim["V1"],coords=[(0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,0.2]",sheet=topo.sim["V1"],coords=[(-0.2,0.2)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,-0.2]",sheet=topo.sim["V1"],coords=[(-0.2,-0.2)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.1]",sheet=topo.sim["V1"],coords=[(0.0,0.1)])()
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.1]",sheet=topo.sim["V1"],coords=[(0.0,-0.1)])()
	topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0]",sheet=topo.sim["V1"],coords=[(-0.1,0.0)])()    
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0]",sheet=topo.sim["V1"],coords=[(0.1,-0.0)])()



def saver_function():
    from topo.command.basic import save_snapshot
    save_snapshot(normalize_path('snapshot.typ'))

def empty():
    a = 10