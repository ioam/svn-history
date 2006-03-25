# $Id$
#
# Performs simple tests that the examples at least run; should be
# replaced by more extensive tests.

all: hierarchical cfsom_or lissom_oo_or

cfsom_or:
	cd .. ; ./topographica examples/cfsom_or.ty -c "topo.sim.run(1)"

hierarchical:
	cd .. ; ./topographica examples/hierarchical.ty -c "topo.sim.run(1)"

lissom_or:
	cd .. ; ./topographica examples/lissom_or.ty -c "topo.sim.run(1)"

lissom_oo_or:
	cd .. ; ./topographica examples/lissom_oo_or.ty -c "topo.sim.run(1)"


# Generate saved examples

lissom_oo_or_20000.typ: lissom_oo_or.ty
	../topographica lissom_oo_or.ty -c "topo.sim.run(20000)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('$@')"


lissom_or_20000.typ: lissom_or.ty
	../topographica lissom_or.ty    -c "topo.sim.run(20000)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('$@')"

