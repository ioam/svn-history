# $Id$
#
# Commands for running the example files

all_quick: hierarchical cfsom_or som_retinotopy lissom_oo_or
all_long: lissom_oo_or_20000.typ som_retinotopy_40000.typ lissom_or_20000.typ
saved-examples: lissom_oo_or_20000.typ


# Define typical commands used in the examples
SNAPSHOT = -c "from topo.commands.basic import save_snapshot ; save_snapshot"

OR_ANALYSIS = -c "from topo.commands.analysis import measure_or_pref,measure_position_pref,measure_cog,measure_or_tuning_fullfield,measure_contrast_response; \
measure_or_pref(); \
measure_position_pref(); \
measure_cog(); \
measure_or_tuning_fullfield(); \
measure_contrast_response(); \
"

RETINOTOPY_ANALYSIS = -c "from topo.commands.analysis import measure_position_pref,measure_cog ;\
measure_position_pref(); \
measure_cog(); \
"


# Perform simple tests that the examples at least run; should be
# replaced by more extensive tests.
cfsom_or:
	cd .. ; ./topographica -c "default_density=4" examples/cfsom_or.ty -c "topo.sim.run(1)"

hierarchical:
	cd .. ; ./topographica -c "default_density=4" examples/hierarchical.ty -c "topo.sim.run(1)"

lissom_or:
	cd .. ; ./topographica -c "default_density=4" examples/lissom_or.ty -c "topo.sim.run(1)"

lissom_oo_or:
	cd .. ; ./topographica -c "default_density=4" examples/lissom_oo_or.ty -c "topo.sim.run(1)"

som_retinotopy:
	cd .. ; ./topographica -c "default_density=4" examples/som_retinotopy.ty -c "topo.sim.run(1)"


# Generate saved examples of complete simulations
lissom_oo_or_20000.typ: lissom_oo_or.ty ../topo/*/*.py
	../topographica lissom_oo_or.ty -c "topo.sim.run(20000)" ${OR_ANALYSIS} ${SNAPSHOT}"('$@')"


lissom_or_20000.typ: lissom_or.ty ../topo/*/*.py
	../topographica lissom_or.ty -c "topo.sim.run(20000)" ${OR_ANALYSIS} ${SNAPSHOT}"('$@')"


obermayer_pnas90_30000.typ: obermayer_pnas90.ty ../topo/*/*.py
	../topographica obermayer_pnas90.ty -c "topo.sim.run(40000)" ${OR_ANALYSIS} ${SNAPSHOT}"('$@')"


som_retinotopy_40000.typ: som_retinotopy.ty ../topo/*/*.py
	../topographica som_retinotopy.ty -c "topo.sim.run(40000)" ${RETINOTOPY_ANALYSIS} ${SNAPSHOT}"('$@')"


