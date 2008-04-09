### import to _or_ reference simulations

def initialize_variables(BaseRN,BaseN):

    ############################################################
    # Variables that can be overridden & written into param file
    rf_radius=BaseRN/4.0+0.5
    # force odd aff weights matrix
    if (2*rf_radius)%2==0:
        rf_radius+=0.5

    inh_rad=BaseN/4.0-1.0
    # force odd inh weights matrix
    if (2*inh_rad)%2==0:
        inh_rad+=0.5

    for n,r in zip(['rf_radius','inh_rad'],[rf_radius,inh_rad]):
        assert r>=1.5, "%s = %s; smaller than 1.5 - can't compare simulations"%(n,r)

    exc_rad=max(2.5,BaseN/10.0)
    ############################################################

    rf_radius_scale=6.5/rf_radius

    min_exc_rad=max(1.5,BaseN/44)

    ############################################################
    # Variables to match 010910_or_map_512MB.param and or_defs
    area_scale=1.0
    #num_eyes=1

    gammaexc=0.9
    gammainh=0.9

    delta_i=0.1
    beta_i=delta_i+0.55

    randomness = 0.0

    xsigma=7.0/rf_radius_scale
    ysigma=1.5/rf_radius_scale
    scale_input=1.0

    retina_edge_buffer=rf_radius-0.5+(randomness*BaseRN*area_scale/2)
    RN=BaseRN*area_scale+2*retina_edge_buffer

    # should be divided by n_aff_inputs
    acs=6.5*6.5/rf_radius/rf_radius

    ecs=19.5*19.5/exc_rad/exc_rad
    ics=47.5*47.5/inh_rad/inh_rad
    alpha_input=0.007*acs
    alpha_exc=0.002*ecs
    alpha_inh=0.00025*ics

    tsettle=9
    ############################################################


    return locals()


def add_scheduled_outputfn_changes(sim):
    ### delta/beta changes
    #
    sim.schedule_command(  199, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.01; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.01')
    sim.schedule_command(  499, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.02; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.02')
    sim.schedule_command(  999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.05; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.03')
    sim.schedule_command( 1999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.08; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.05')
    sim.schedule_command( 2999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.10; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.08')
    sim.schedule_command( 3999,                                                    'topo.sim["Primary"].output_fn.upper_bound=beta_i+0.11')
    sim.schedule_command( 4999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.11; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.14')
    sim.schedule_command( 6499, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.12; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.17')
    sim.schedule_command( 7999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.13; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.20')
    sim.schedule_command(19999, 'topo.sim["Primary"].output_fn.lower_bound=delta_i+0.14; topo.sim["Primary"].output_fn.upper_bound=beta_i+0.23')

def add_scheduled_tsettle_changes(sim):
    #tsettle changes
    sim.schedule_command( 1999, 'topo.sim["Primary"].tsettle=10')
    sim.schedule_command( 4999, 'topo.sim["Primary"].tsettle=11')
    sim.schedule_command( 6499, 'topo.sim["Primary"].tsettle=12')
    sim.schedule_command( 7999, 'topo.sim["Primary"].tsettle=13')
    

def add_scheduled_exc_bounds_changes(sim):
    ### Excitatory bounds changes
    #
    # The learning rate is adjusted too because the number of units
    # changes and ecs changes (even if the learning rate is going to
    # be adjusted anyway at this time)

    change_bounds = "LE.change_bounds(BoundingBox(radius=exc_rad/BaseN,min_radius=min_exc_rad/BaseN));LE.learning_rate=alpha_exc*LE.n_units()"
    
    sim.schedule_command(199,'exc_rad=exc_rad*0.6; %s'%change_bounds)
    sim.schedule_command(499,'exc_rad=exc_rad*0.7; %s'%change_bounds)
    sim.schedule_command(999,'exc_rad=exc_rad*0.8; %s'%change_bounds)
    sim.schedule_command(1999,'exc_rad=exc_rad*0.8; %s'%change_bounds)
    sim.schedule_command(2999,'exc_rad=exc_rad*0.8; %s'%change_bounds)
    sim.schedule_command(3999,'exc_rad=exc_rad*0.6; %s'%change_bounds)
    sim.schedule_command(4999,'exc_rad=exc_rad*0.6; %s'%change_bounds)
    sim.schedule_command(6499,'exc_rad=exc_rad*0.6; %s'%change_bounds)
    sim.schedule_command(7999,'exc_rad=exc_rad*0.6; %s'%change_bounds)
    sim.schedule_command(19999,'exc_rad=exc_rad*0.6; %s'%change_bounds)


def add_scheduled_exc_Lrate_changes(sim):
    ### Excitatory learning rate changes
    #
    sim.schedule_command(499,'alpha_exc=0.001*ecs; LE.learning_rate=alpha_exc*LE.n_units()')


def add_scheduled_aff_Lrate_changes(sim,pname="Af"):
    ### Afferent learning rate changes
    #
    sim.schedule_command(499,  'alpha_input=0.0050*acs; %s.learning_rate=alpha_input*%s.n_units()'%(pname,pname))
    sim.schedule_command(1999, 'alpha_input=0.0040*acs; %s.learning_rate=alpha_input*%s.n_units()'%(pname,pname))
    sim.schedule_command(3999, 'alpha_input=0.0030*acs; %s.learning_rate=alpha_input*%s.n_units()'%(pname,pname))
    sim.schedule_command(19999,'alpha_input=0.0015*acs; %s.learning_rate=alpha_input*%s.n_units()'%(pname,pname))






    
