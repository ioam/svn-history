define_param xunit   Param_Integer   
define_param yunit   Param_Integer   

define_param max_unit Param_Integer
set max_unit=BaseN-1

echo "saving plots for all units..."
for xunit=0 xunit<BaseN xunit=xunit+1 exec \
"for yunit=0 yunit<BaseN yunit=yunit+1 \
  plot_unit save_matrices=True xunit yunit"
