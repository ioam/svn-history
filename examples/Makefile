# $Id$
#
# Performs simple tests that the examples at least run; should be
# replaced by more extensive tests.

all_quick: hierarchical cfsom_or som_retinotopy lissom_oo_or
all_long: som_retinotopy_40000.typ lissom_oo_or_20000.typ lissom_or_20000.typ
saved-examples: lissom_oo_or_20000.typ


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


# Generate saved examples

lissom_oo_or_20000.typ: lissom_oo_or.ty ../topo/*/*.py
	../topographica lissom_oo_or.ty -c "topo.sim.run(20000)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('$@')"


lissom_or_20000.typ: lissom_or.ty ../topo/*/*.py
	../topographica lissom_or.ty    -c "topo.sim.run(20000)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('$@')"

som_retinotopy_40000.typ: som_retinotopy.ty ../topo/*/*.py
	../topographica som_retinotopy.ty   -c "topo.sim.run(40000)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('$@')"


