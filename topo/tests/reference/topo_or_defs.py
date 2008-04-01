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

    exc_rad=max(2.5,BaseN/10.0)
    ############################################################



    ############################################################
    # Variables to match 010910_or_map_512MB.param and or_defs
    area_scale=1.0
    #num_eyes=1

    gammaexc=0.9
    gammainh=0.9

    delta_i=0.1
    beta_i=delta_i+0.55

    randomness = 0.0

    rf_radius_scale=1.0
    xsigma=7.0
    ysigma=1.5
    scale_input=1.0

    retina_edge_buffer=rf_radius-0.5+(randomness*BaseRN*area_scale/2)
    RN=BaseRN*area_scale+2*retina_edge_buffer

    acs=6.5*6.5/rf_radius/rf_radius
    ecs=19.5*19.5/exc_rad/exc_rad
    ics=47.5*47.5/inh_rad/inh_rad
    alpha_input=0.007*acs
    alpha_exc=0.002*ecs
    alpha_inh=0.00025*ics

    tsettle=9
    ############################################################


    return locals()


