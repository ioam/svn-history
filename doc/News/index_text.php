2009-02-11  jbednar

	* [r9984] topo/base/cf.py:
	  Added mask_threshold value (fixes ALERT)

2009-02-11  ceball

	* [r9983] doc/Tutorials/gca_lissom_text.php,
	  doc/Tutorials/lissom_oo_or_text.php:
	  Added section about visualizing map measurement.

	* [r9982] doc/Tutorials/lissom_oo_or_text.php:
	  Fixed link to GeneratorSheet reference.

2009-02-11  jbednar

	* [r9981] topo/plotting/plot.py:
	  Suppressed extra staleness_warnings

	* [r9980] examples/gca_lissom.ty:
	  Changed defaults for map measurement to match lissom_oo_or.ty

	* [r9979]
	  topo/command/disp_key_white_vert_small.png:
	  Cleaned up number spacing

2009-02-11  ceball

	* [r9978] doc/Tutorials/gca_lissom_text.php,
	  doc/Tutorials/images/gca_lissom_activity_010000.png,
	  doc/Tutorials/images/gca_lissom_activity_010000_or.png,
	  doc/Tutorials/images/gca_lissom_cf_center_010000.png,
	  doc/Tutorials/images/gca_lissom_cf_center_010000_or.png,
	  doc/Tutorials/images/gca_lissom_cf_vertical_010000_or.png,
	  doc/Tutorials/images/gca_lissom_network_diagram.png,
	  doc/Tutorials/images/gca_lissom_or_pref_010000.png,
	  doc/Tutorials/images/gca_lissom_ormap_ft.png,
	  doc/Tutorials/images/gca_lissom_projection_010000.png,
	  doc/Tutorials/images/gca_lissom_test_pattern.png,
	  doc/Tutorials/lissom_oo_or_text.php:
	  Initial version of GCA-LISSOM tutorial.

	* [r9977] examples/run.py:
	  Added 'gca_lissom_10000.typ' target.

2009-02-10  jbednar

	* [r9976] doc/Tutorials/lissom_oo_or_text.php,
	  doc/Tutorials/lissom_or_text.php:
	  Fixed broken URL

	* [r9975] topo/tkgui/editor.py:
	  Fixed activity and density display options

	* [r9974] contrib/jacommands.py,
	  topo/sheet/lissom.py:
	  Moved add_gc back to jacommands now that gca_lissom.ty does not
	  need it

2009-02-10  antolikjan

	* [r9973] contrib/gc_alissom.ty:
	  bug repair

	* [r9972] contrib/gc_alissom.ty:
	  some more minor simplifications and parameter changes

	* [r9971] contrib/cc_lissom_oo_or_simple_rv.ty:
	  change of default parameter value

2009-02-10  jbednar

	* [r9970] examples/gca_lissom.ty:
	  Removed dependence on add_gc, and fixed selectivity_multiplier

	* [r9969] topo/base/arrayutil.py:
	  Made divide_with_constant available globally

2009-02-10  ceball

	* [r9968]
	  doc/Tutorials/images/activity_line_oo.png,
	  doc/Tutorials/images/activity_line_oo_or.png,
	  doc/Tutorials/images/lissom_oo_or_activity_rightclick.png,
	  doc/Tutorials/images/lissom_oo_or_orpref_ft.png,
	  doc/Tutorials/images/natural_image_oo_or.png,
	  doc/Tutorials/images/oo_or_map.png,
	  doc/Tutorials/images/projection_oo.png,
	  doc/Tutorials/images/test_pattern_oo.png,
	  doc/Tutorials/images/unit_weights_0_0_oo.png,
	  doc/Tutorials/images/unit_weights_0_0_oo_or.png,
	  doc/Tutorials/images/unit_weights_41_24_oo_or.png,
	  doc/Tutorials/lissom_oo_or_text.php:
	  Updated lissom_oo_or tutorial images.

2009-02-10  antolikjan

	* [r9967] contrib/cc_lissom_oo_or_simple_rv.ty:
	  change of default parameter value

2009-02-10  ceball

	* [r9966]
	  doc/Tutorials/images/topographica_console.png,
	  doc/Tutorials/lissom_oo_or_text.php:
	  Files missed from r9965.

	* [r9965]
	  doc/Tutorials/images/som_topographica_console.png,
	  doc/Tutorials/images/topographica_console.png,
	  doc/Tutorials/som_retinotopy_text.php:
	  Renamed som_retinotopy's topographica_console.png to
	  som_topographica_console.png (tutorials can't share a console
	  image now the simulation name is displayed).

	* [r9964]
	  doc/Tutorials/images/som_activity_000000.png,
	  doc/Tutorials/images/som_activity_000001.png,
	  doc/Tutorials/images/som_cog_000000.png,
	  doc/Tutorials/images/som_cog_005000.png,
	  doc/Tutorials/images/som_projection_000000.png,
	  doc/Tutorials/images/som_projection_000001.png,
	  doc/Tutorials/images/som_projection_000005.png,
	  doc/Tutorials/images/som_projection_010000.png,
	  doc/Tutorials/images/som_projection_040000.png,
	  doc/Tutorials/images/som_projection_activity_000001.png,
	  doc/Tutorials/images/topographica_console.png,
	  doc/Tutorials/som_retinotopy_text.php:
	  Updated SOM retinotopy tutorial with new screenshots.

2009-02-10  antolikjan

	* [r9963] contrib/gc_alissom.ty:
	  parameter value change

2009-02-10  ceball

	* [r9962] doc/User_Manual/commandline_text.php,
	  doc/User_Manual/plotting_text.php,
	  topo/plotting/plotgroup.py,
	  topo/tkgui/plotgrouppanel.py:
	  More renaming related to update_command -> pre_plot_hooks.

2009-02-09  jbednar

	* [r9961] topo/transferfn/basic.py:
	  Fixed typo

	* [r9960] topo/sheet/lissom.py:
	  Expanded comment

	* [r9959] topo/analysis/featureresponses.py:
	  Removed unused imports

	* [r9958] topo/plotting/plotgroup.py:
	  Fixed to provide a default sheet in more cases

	* [r9957] topo/transferfn/basic.py:
	  Minor cleanup

	* [r9956] topo/base/simulation.py:
	  Changed EventProcessor.input_event to deepcopy the data only
	  once, regardles of the number of destinations for the message

2009-02-09  ceball

	* [r9955] contrib/jacommands.py:
	  Added links to classes recently removed.

	* [r9954] examples/gca_lissom.ty,
	  topo/transferfn/basic.py:
	  Renamed ActivityHysteresis to Hysteresis, and updated docs.

	* [r9953] contrib/jacommands.py,
	  examples/gca_lissom.ty,
	  topo/sheet/lissom.py:
	  Moved contrib.jacommands.AddGC() to topo.sheet.lissom.add_gc().

	* [r9952] contrib/jacommands.py,
	  examples/gca_lissom.ty:
	  AddGC() now takes arguments rather than looking in __main__, and
	  works on one sheet at a time.

	* [r9951] contrib/jacommands.py,
	  examples/gca_lissom.ty,
	  topo/transferfn/basic.py:
	  Moved ActivityHysteresis from contrib.jacommands to
	  topo.transferfn.basic.

	* [r9950] contrib/jacommands.py:
	  Minor changes (should be no visible change).

	* [r9949] contrib/jacommands.py,
	  examples/gca_lissom.ty,
	  topo/transferfn/basic.py:
	  Moved HomeostaticResponse from contrib.jacommands to
	  topo.transferfn.basic.

	* [r9948] contrib/jacommands.py,
	  examples/gca_lissom.ty:
	  Renamed SimpleHomeoLinearRelative to HomeostaticResponse (and
	  made minor formatting changes).

	* [r9947] examples/gca_lissom.ty:
	  Added missing svn properties to gca_lissom.ty.

2009-02-09  jbednar

	* [r9946] examples/gca_lissom.ty:
	  Fixed comment

	* [r9945] Makefile,
	  examples/Makefile,
	  examples/gc_alissom.ty,
	  examples/gca_lissom.ty,
	  topo/tests/gc_alissom.ty_DATA,
	  topo/tests/gc_alissom.ty_SPEEDDATA,
	  topo/tests/gca_lissom.ty_DATA,
	  topo/tests/gca_lissom.ty_SPEEDDATA:
	  Renamed gc_alissom to gca_lissom to make it pronounceable

	* [r9944] examples/gc_alissom.ty:
	  Added defaults to match lissom_oo_or.ty. Changed feature curves
	  as Jan did in contrib

2009-02-06  antolikjan

	* [r9943] contrib/cc_lissom_oo_or_simple_rv.ty:
	  added half rectified TF option for V1Simple

	* [r9942] topo/transferfn/basic.py:
	  modified half rectified TFs to use threshold

	* [r9941] contrib/gc_alissom.ty:
	  changed the selectivity multiplier

2009-02-06  ceball

	* [r9940] doc/User_Manual/plotting_text.php,
	  topo/command/analysis.py:
	  Added note about alternative implementation of measure_or_pref().

	* [r9939] doc/User_Manual/images/edit_list.png,
	  doc/User_Manual/images/list_item_properties.png,
	  doc/User_Manual/plotting_text.php:
	  Updated to show list editing via the GUI.

2009-02-06  jbednar

	* [r9938] doc/User_Manual/scripts_text.php:
	  Fixed typo

2009-02-06  ceball

	* [r9937] topo/misc/commandline.py:
	  Fixed quotation error.

	* [r9936] doc/Tutorials/lissom_oo_or_text.php,
	  doc/Tutorials/som_retinotopy_text.php,
	  doc/User_Manual/batch_text.php,
	  doc/User_Manual/scripts_text.php,
	  topo/misc/commandline.py:
	  Updated documentation relating to -p and global_params.

2009-02-06  antolikjan

	* [r9935] contrib/cc_lissom_oo_or_simple_rv.ty:
	  allowed for parametrization for the strength of the LGN channels
	  strength randomization

	* [r9934] topo/analysis/vision.py:
	  reduced the number of samples for phase scatter plot to match
	  DeAngelis 1999

2009-02-06  ceball

	* [r9933] examples/run.py:
	  Updated location of some commands (now in pylabplots).

2009-02-05  ceball

	* [r9932] topo/misc/legacy.py:
	  Added comment.

	* [r9931] topo/param/parameterized.py:
	  Minor modification to snapshot warning messages.

	* [r9930] topo/param/parameterized.py:
	  Snapshot loading: made Parameter restoration warning message more
	  useful (can now see more work needs to be done on legacy support
	  even for the lissom_oo_or.ty snapshot).

	* [r9929] topo/command/basic.py:
	  Removed unused import.

	* [r9928] topo/param/parameterized.py:
	  Fixed command for importing module while restoring class
	  attributes (previous command committed by mistake during other
	  work).

	* [r9927] contrib/rgbimages.py:
	  Updated to match recent changes to output_fns.

	* [r9926] doc/Downloads/git_text.php:
	  Minor additions to git documentation.

	* [r9925] contrib/rgbhsv.py:
	  Inital version (from CSNG repository).

	* [r9924] contrib/rgbimages.py:
	  Various changes to rgb-related classes. Added various online
	  analysis classes.

2009-02-04  jbednar

	* [r9923] topo/command/analysis.py:
	  Suppressed rarely-useful message

	* [r9922] doc/Future_Work/current_text.php:
	  Removed some completed tasks

	* [r9921] doc/Future_Work/index_text.php:
	  Added link to pytables, and new spiking model

	* [r9920] doc/User_Manual/commandline_text.php:
	  Added example of looking up a SheetView

2009-02-04  antolikjan

	* [r9919] contrib/gc_alissom.ty:
	  made changes regarding the new output function mechanism

	* [r9918] contrib/cc_lissom_oo_or_simple_rv.ty:
	  made changes regarding output function updates

	* [r9917] contrib/cc_lissom_oo_or_simple_rv.ty:
	  bug repair

2009-02-04  jbednar

	* [r9916] topo/tests/lissom_fsa.ty_DATA,
	  topo/tests/lissom_fsa.ty_SPEEDDATA:
	  Committed 2008-10-02 results of running the lissom_fsa.ty tests

2009-02-04  ceball

	* [r9915] external:
	  More to ignore.

2009-02-04  antolikjan

	* [r9914] contrib/cc_lissom_oo_or_simple_rv.ty:
	  got rid of PipelineTF

	* [r9913] contrib/gc_alissom.ty:
	  got rid of PipelineTF

2009-02-04  jbednar

	* [r9912] topo/analysis/featureresponses.py:
	  Changed _fullmatrix handling to work the same for subclasses as
	  for FeatureResponses

2009-02-03  ceball

	* [r9911] etc/update_095_to_096:
	  Attempt to make update script. Still unusable.

	* [r9910] etc/update_095_to_096:
	  More things to update. Still a sketch.

	* [r9909] topo/misc/legacy.py,
	  topo/param/parameterized.py:
	  Support change of output_fn=x to output_fns=[x]. Plus some
	  additional cleanup.

2009-02-03  antolikjan

	* [r9908] topo/analysis/featureresponses.py:
	  made _fullmatrix in FeatureResponses static

	* [r9907] contrib/gc_alissom.ty:
	  decreased the default selectivity multiplier

2009-02-03  ceball

	* [r9906] topo/param/tk.py:
	  Uncommented code to get buttons on list widget.

2009-02-03  jbednar

	* [r9905] topo/tkgui/icons/arrow-down-2.0.png,
	  topo/tkgui/icons/arrow-up.png,
	  topo/tkgui/icons/edit_add.png,
	  topo/tkgui/icons/edit_remove.png,
	  topo/tkgui/icons/star-button.png,
	  topo/tkgui/icons/stop-2.1.png,
	  topo/tkgui/icons/trashcan_empty-2.1.png:
	  Committed results of 'make -C external bluesphere to get icons
	  for list widget

2009-02-03  ceball

	* [r9904] topo/param/tk.py:
	  Upgraded list editing in the GUI. Can now add, remove, and
	  reorder items. Need to add icons for buttons. But: what started
	  out as simple code to implement this feature has become a mess,
	  for various irrelevant reasons; some specific problems are noted
	  in the commit.

	* [r9903] topo/misc/legacy.py:
	  Added comment.

	* [r9902] topo/misc/legacy.py:
	  Cleaned up teststimuli support.

2009-02-02  ceball

	* [r9901] doc/Future_Work/current_text.php,
	  doc/User_Manual/commandline_text.php,
	  doc/User_Manual/noise_text.php,
	  doc/User_Manual/overview_text.php,
	  doc/User_Manual/parameters_text.php:
	  Updated documentation about output functions/transfer functions.

	* [r9900] topo/base/cf.py,
	  topo/base/patterngenerator.py,
	  topo/base/projection.py,
	  topo/pattern/image.py,
	  topo/projection/basic.py,
	  topo/sheet/basic.py:
	  Restored type specification to some output_fns HookLists (didn't
	  restore in cases where type specification should be inherited
	  from a parent class). Removed output_fns parameter in some cases
	  (where I believe the parameter is already suitably specified in a
	  parent class.

2009-02-02  jbednar

	* [r9899]
	  external/BlueSphere-SVG-snapshot-Nov-29-2002_Makefile:
	  Added more icons to topo/tkgui for Chris's list widget

2009-02-02  ceball

	* [r9898] topo/misc/legacy.py:
	  Added legacy support for PipelineOF. Presumably not yet complete,
	  but current snapshot-compatibility-tests now pass without errors
	  or warnings.

	* [r9897] contrib/jacommands.py,
	  doc/User_Manual/commandline_text.php,
	  doc/User_Manual/plotting_text.php,
	  examples/gc_alissom.ty,
	  examples/hierarchical.ty,
	  examples/leaky_lissom_or.ty,
	  examples/lissom.ty,
	  examples/lissom_fsa.ty,
	  examples/lissom_oo_or.ty,
	  examples/lissom_oo_or_cr.ty,
	  examples/lissom_or.ty,
	  examples/lissom_whisker_barrels.ty,
	  examples/obermayer_pnas90.ty,
	  examples/som_retinotopy.ty,
	  examples/sullivan_neurocomputing04.ty,
	  examples/tiny.ty,
	  topo/analysis/featureresponses.py,
	  topo/base/cf.py,
	  topo/base/functionfamily.py,
	  topo/base/patterngenerator.py,
	  topo/base/projection.py,
	  topo/command/analysis.py,
	  topo/command/basic.py,
	  topo/misc/legacy.py,
	  topo/pattern/image.py,
	  topo/pattern/random.py,
	  topo/pattern/rds.py,
	  topo/projection/basic.py,
	  topo/sheet/basic.py,
	  topo/sheet/lissom.py,
	  topo/sheet/slissom.py,
	  topo/tests/gui_tests.py,
	  topo/tests/testimage.py,
	  topo/transferfn/basic.py:
	  Changed output_fn parameters to be HookLists, and renamed
	  output_fn (and related) variable names to output_fns. No legacy
	  support yet.

2009-02-01  ceball

	* [r9896] topo/param/tk.py:
	  Fixed bug introduced in an earlier checkin.

	* [r9895] topo/param/tk.py:
	  Fixed bug introduced in previous checkin.

	* [r9894] topo/param/tk.py:
	  More cleanup. Should be no visible change.

	* [r9893] topo/param/tk.py:
	  More cleanup. Should be no visible change.

	* [r9892] topo/param/tk.py:
	  More cleanup. Should be no visible change.

	* [r9891] topo/param/tk.py:
	  More cleanup. Should be no visible change.

	* [r9890] topo/param/tk.py:
	  Cleanup - should be no visible change.

	* [r9889] topo/param/tk.py:
	  Simplified on_set() and on_modify().

	* [r9888] topo/param/tk.py:
	  Minor simplification: don't need to store row information (grid()
	  stores it already).

	* [r9887] topo/param/tk.py,
	  topo/tests/testtkparameterizedobject.py,
	  topo/tkgui/featurecurvepanel.py,
	  topo/tkgui/plotgrouppanel.py,
	  topo/tkgui/projectionpanel.py,
	  topo/tkgui/templateplotgrouppanel.py,
	  topo/tkgui/testpattern.py:
	  Renamed on_change() to on_set() (to distinguish from on_modify().

	* [r9886] etc/update_095_to_096,
	  topo/command/basic.py:
	  Cleaned up some notices about filing bug reports.

	* [r9885] topo/misc/legacy.py:
	  More simplification of legacy support.

	* [r9884] topo/param/parameterized.py:
	  When unpickling class attributes, no longer uses
	  __main__.__dict__ as a space in which to work. Added note about
	  intention to remove try/catches around class attribute
	  unpickling.

	* [r9883] topo/misc/legacy.py:
	  Fixed bug in legacy's module_redirect() (for cases where a
	  module's parent is already a redirected module). Added support
	  for OneDPowerSpectrum's moves between topo.pattern.audio and
	  .basic.

2009-01-30  antolikjan

	* [r9882] topo/analysis/featureresponses.py:
	  corrected the problem with ACDC tuning curve and added hook to
	  FeatureCurves

2009-01-30  jbednar

	* [r9881] examples/gc_alissom.ty:
	  Cleaned up and reorganized to match lissom_oo_or.ty

	* [r9880] examples/gc_alissom.ty:
	  Removed unused bounding box

	* [r9879] examples/gc_alissom.ty:
	  Converted locals to parameters

	* [r9878] topo/analysis/featureresponses.py:
	  Temporarily commented out broken code

	* [r9877] examples/hierarchical.ty,
	  examples/leaky_lissom_or.ty,
	  examples/lissom.ty,
	  examples/lissom_fsa.ty,
	  examples/lissom_oo_or.ty,
	  examples/lissom_or.ty,
	  examples/obermayer_pnas90.ty,
	  examples/perrinet_retina.ty,
	  examples/som_retinotopy.ty,
	  examples/sullivan_neurocomputing04.ty,
	  examples/tiny.ty:
	  Added note explaining parameters

2009-01-30  antolikjan

	* [r9876] topo/analysis/vision.py:
	  corrected and import problem

	* [r9875] contrib/gc_alissom.ty:
	  added NoisyDisks and the change from NoisyDisks to Natural into
	  the simulation

2009-01-30  ceball

	* [r9874] topo/param/tk.py:
	  Disabled ListEntry text box, but made foreground color same as
	  normal text box (otherwise nobody will try clicking on it...).

	* [r9873] topo/param/tk.py:
	  Changed list widget to have right-click menu with 'properties' on
	  it for editing a list (rather than it being a left click).

2009-01-29  jbednar

	* [r9872] examples/gc_alissom.ty:
	  Converted imports to new simpler style

2009-01-29  antolikjan

	* [r9871] topo/analysis/vision.py:
	  repaired circular imports

	* [r9870] topo/command/pylabplots.py:
	  corrected circular import bug

	* [r9869] contrib/cc_lissom_oo_or_simple_rv.ty:
	  one parameter change and one import renaming

	* [r9868] contrib/jacommands.py:
	  tiny cosmetic changes

	* [r9867] topo/analysis/featureresponses.py:
	  plugged in the new ACDC way of computing tuning curves

	* [r9866] topo/analysis/vision.py:
	  added new way of computing tuning curves - the AC DC max

	* [r9865] contrib/gc_alissom.ty:
	  a working version of the same file in examples

2009-01-29  jbednar

	* [r9864] Makefile,
	  topo/tests/gc_alissom.ty_DATA,
	  topo/tests/gc_alissom.ty_SPEEDDATA:
	  Added gc_alissom.ty tests

	* [r9863] examples/gc_alissom.ty:
	  Changed name of density parameters to match other examples

2009-01-29  ceball

	* [r9862] topo/tests/test_script.py:
	  Reduced combinations of densities for c++ comparisons. See SF.net
	  #2545559.

	* [r9861] doc/buildbot/master.cfg:
	  Removed fixed-parameters c++ lissom comparisons.

	* [r9860] Makefile,
	  topo/tests/reference/Makefile,
	  topo/tests/reference/fixed_params:
	  Removed fixed-parameters C++ lissom comparisons.

2009-01-28  ceball

	* [r9859] Makefile:
	  Rearranged comment; no visible change.

	* [r9858] doc/buildbot/master.cfg:
	  Set cloud to use 'clobber'. Reduced unoptimized matching
	  requirement from 7 dp to 6 dp.

	* [r9857] topo/tests/test_script.py:
	  Added print out of no. of decimal places on failure.

	* [r9856] topo/misc/legacy.py:
	  Legacy support: simplified; should be no visible change.

	* [r9855] topo/misc/legacy.py:
	  Further simplifications.

	* [r9854] topo/misc/legacy.py:
	  Simplified support for package name changes.

	* [r9853] topo/misc/legacy.py:
	  Simplified support for module name changes. Still more to go...

2009-01-28  jbednar

	* [r9852] doc/News/index_text.php:
	  Fixed typo that was breaking doc build

	* [r9851] external/Makefile:
	  Fixed broken odict clean and uninstall targets

2009-01-27  antolikjan

	* [r9850]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  some more parameter changes

	* [r9849] examples/gc_alissom.ty:
	  made default lateral exc. learning rate 0

	* [r9848]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  changed some parameters

	* [r9847] examples/gc_alissom.ty:
	  allowed for lat exc connections to learn

2009-01-27  ceball

	* [r9846] topo/misc/legacy.py:
	  Fixed problem with fake_package() where wrong module was being
	  returned by __import__.

	* [r9845] external/Imaging.diff,
	  external/Imaging_OSX.diff:
	  Restored Imaging.diff and removed Imaging_OSX.diff (wrong one
	  mistakenly removed in r9728).

2009-01-27  jbednar

	* [r9844] topo/command/pylabplots.py:
	  Fixed tuning curve plots to show full coordinates, instead of
	  cropped to integers

	* [r9843] doc/News/index_text.php,
	  topo/tkgui/plotgrouppanel.py:
	  Added right-click option for plotting orientation tuning curves

	* [r9842] topo/param/parameterized.py:
	  Fixed typo in doc

2009-01-27  ceball

	* [r9841] topo/outputfn:
	  Removed topo.outputfn; apparently removal didn't carry over from
	  git.

2009-01-26  ceball

	* [r9840] topo/param/tk.py:
	  Can now edit lists in the GUI. Clicking on a list parameter
	  brings up a new window with the list entries. Initial version:
	  cannot add or remove items from the list (plus see other bugs on
	  sf.net). Works by representing the list with a Parameterized
	  object.

	* [r9839] external/Makefile:
	  Added odict to default target (provides OrderedDictionary).

	* [r9838] topo/param/parameterized.py:
	  Fixed ParameterizedFunction's script_repr() method (so that it
	  includes '.instance()').

	* [r9837] topo/param/parameterized.py:
	  Fixed typo in code.

	* [r9836] topo/param/parameterized.py:
	  Delete params() cache when adding a new parameter to a class.

2009-01-25  ceball

	* [r9835] doc/User_Manual:
	  More to ignore.

	* [r9834] topo/transferfn:
	  Set svn:ignore on topo/transferfn/

	* [r9833] external:
	  More to ignore.

	* [r9832] etc/update_095_to_096:
	  Initial version.

	* [r9831] contrib/cc_lissom_oo_or_simple_rv.ty,
	  contrib/gc_lissom_oo_or_homeostatic_new.ty,
	  contrib/jacommands.py,
	  contrib/jsldefs.py,
	  contrib/laminar_oo_or.ty,
	  contrib/laminar_or.ty,
	  contrib/lesi.ty,
	  contrib/lesi_whisker_barrels.ty,
	  contrib/lgn_lateral.ty,
	  contrib/lissom.ty,
	  contrib/lissom_oo_dr.ty,
	  contrib/lissom_oo_or_homeostatic.ty,
	  contrib/lissom_oo_or_homeostatic_tracked.ty,
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty,
	  contrib/lissom_oo_or_noshrinking.ty,
	  contrib/lissom_oo_or_noshrinking_latswitch.ty,
	  contrib/lissom_oo_or_species.ty,
	  contrib/lissom_oo_or_species_tracked.ty,
	  contrib/lissom_or_noshrinking.ty,
	  contrib/lissom_or_noshrinking_latswitch.ty,
	  contrib/modelfit.py,
	  contrib/sparse_connectivity_LESI.ty,
	  contrib/sparse_connectivity_model.ty,
	  contrib/species_cf_jitter.ty,
	  contrib/species_lateral_sparsity.ty,
	  contrib/wordcolor.ty,
	  doc/Developer_Manual/imports_text.php,
	  doc/Developer_Manual/optimization_text.php,
	  doc/FAQ/index_text.php,
	  doc/Future_Work/current_text.php,
	  doc/Future_Work/index_text.php,
	  doc/Reference_Manual/index_text.php,
	  doc/User_Manual/commandline_text.php,
	  doc/User_Manual/noise_text.php,
	  doc/User_Manual/overview_text.php,
	  doc/User_Manual/scripts_text.php,
	  examples/gc_alissom.ty,
	  examples/hierarchical.ty,
	  examples/leaky_lissom_or.ty,
	  examples/lissom.ty,
	  examples/lissom_fsa.ty,
	  examples/lissom_oo_or.ty,
	  examples/lissom_oo_or_cr.ty,
	  examples/lissom_or.ty,
	  examples/lissom_whisker_barrels.ty,
	  examples/obermayer_pnas90.ty,
	  examples/som_retinotopy.ty,
	  examples/sullivan_neurocomputing04.ty,
	  examples/tiny.ty,
	  topo/__init__.py,
	  topo/base/cf.py,
	  topo/base/functionfamily.py,
	  topo/base/patterngenerator.py,
	  topo/base/projection.py,
	  topo/command/basic.py,
	  topo/command/pylabplots.py,
	  topo/learningfn/som.py,
	  topo/misc/legacy.py,
	  topo/outputfn/__init__.py,
	  topo/outputfn/basic.py,
	  topo/outputfn/optimized.py,
	  topo/outputfn/projfn.py,
	  topo/pattern/image.py,
	  topo/pattern/random.py,
	  topo/pattern/rds.py,
	  topo/projection/basic.py,
	  topo/sheet/basic.py,
	  topo/sheet/lissom.py,
	  topo/sheet/optimized.py,
	  topo/tests/reference/fixed_params/lissom_oo_or_reference_fixed.ty,
	  topo/tests/reference/lissom_fsa_reference.ty,
	  topo/tests/reference/lissom_oo_dr_reference.ty,
	  topo/tests/reference/lissom_oo_or_reference.ty,
	  topo/tests/reference/lissom_or_reference.ty,
	  topo/tests/testimage.py,
	  topo/tests/testoutputfnsbasic.py,
	  topo/tests/testtkparameterizedobject.py,
	  topo/tkgui/__init__.py,
	  topo/transferfn,
	  topo/transferfn/__init__.py,
	  topo/transferfn/basic.py,
	  topo/transferfn/optimized.py,
	  topo/transferfn/projfn.py:
	  Renamed topo.outputfn to topo.transferfn. Renamed OutputFn to
	  TransferFn. Renamed OFs to TFs. Added legacy support.

	* [r9830] topo/command/basic.py:
	  Added snapshot version printing to load_snapshot().

2009-01-24  ceball

	* [r9829] topo/analysis/featureresponses.py,
	  topo/base/functionfamily.py:
	  Renamed after_analysis_session to post_analysis_session_hooks. No
	  legacy support added.

	* [r9828] topo/analysis/featureresponses.py,
	  topo/base/functionfamily.py:
	  Renamed before_analysis_session to pre_analysis_session_hooks. No
	  legacy support added.

	* [r9827] topo/analysis/featureresponses.py,
	  topo/base/functionfamily.py:
	  Renamed after_pattern_presentation to post_presentation_hooks. No
	  legacy support added.

	* [r9826] contrib/jacommands.py,
	  topo/analysis/featureresponses.py,
	  topo/base/functionfamily.py:
	  Renamed before_pattern_presentation to pre_presentation_hooks. No
	  legacy support added.

	* [r9825] topo/__init__.py,
	  topo/param/parameterized.py:
	  Updated comments.

	* [r9824] topo/__init__.py,
	  topo/base/simulation.py,
	  topo/misc/legacy.py,
	  topo/param/__init__.py:
	  Added general support for pickling/copying instance methods.
	  Removed InstanceMethodWrapper and wrap_callable.

	* [r9823] doc/buildbot/master.cfg:
	  Added cloud as a buildslave.

	* [r9822] doc/buildbot/master.cfg:
	  Reorganization of buildmaster configuration: should be no visible
	  change.

	* [r9821] Makefile:
	  Renamed default_density etc.

	* [r9820] examples/som_retinotopy.ty:
	  Undid accidental change to default retina_density (changed from
	  from 24.0 to 10.0 in r9809).

	* [r9819] topo/tests/test_script.py:
	  Added support for old test data files containing
	  'default_density' etc.

	* [r9818] topo/tests/lissom.ty_DATA:
	  Data from r9776 (after random seed change).

	* [r9817] topo/tests/test_script.py:
	  Added support for test data that contains old 'default_'
	  arguments.

	* [r9816] topo/tests/test_script.py:
	  TestScript now prints arguments that were specifed for a script
	  (so that we can see what arguments were used).

2009-01-23  jbednar

	* [r9815] examples/Makefile:
	  Removed long-gone or_dr simulation. Added gc_alissom simulation.

	* [r9814] examples/perrinet_retina.ty:
	  Added URL and minor notes, plus made sim time controllable and
	  forced density to be an integer (as NEST requires)

	* [r9813] topo/learningfn/optimized.py:
	  Removed redundant option

2009-01-22  ceball

	* [r9812] contrib/expressionparam.py:
	  Initial version.

	* [r9811] external/Makefile,
	  external/termcap-1.3.1.tar.gz:
	  Added termcap, and made readline depend on it. Made Python depend
	  on readline, and passed EXTRA_CFLAGS to Python's make so that
	  Topographica's include directory is used. Added readline and
	  termcap to uninstall and clean targets.

2009-01-22  antolikjan

	* [r9810] examples/gc_alissom.ty:
	  added external parameters and made activity to reset between
	  input presentations

2009-01-21  jbednar

	* [r9809] examples/som_retinotopy.ty:
	  Converted locals() calls to explicit global parameters

	* [r9808] doc/News/index_text.php:
	  Updated with a recent change

	* [r9807] Makefile:
	  Removed cfsom_or references

	* [r9806] topo/tests/test_script.py:
	  Changed default_density to cortex_density to match changes in
	  examples/; still needs work

	* [r9805] examples/leaky_lissom_or.ty,
	  examples/lissom_fsa.ty,
	  examples/lissom_or.ty,
	  examples/obermayer_pnas90.ty,
	  examples/perrinet_retina.ty,
	  examples/sullivan_neurocomputing04.ty:
	  Converted locals() calls to explicit global parameters

	* [r9804] examples/hierarchical.ty:
	  Updated to match lissom.ty style parameters

	* [r9803] examples/tiny.ty:
	  Updated to match lissom.ty style parameters

	* [r9802] doc/Future_Work/current_text.php,
	  doc/User_Manual/commandline_text.php,
	  doc/User_Manual/scripts_text.php,
	  examples/cfsom_or.ty,
	  examples/run.py:
	  Removed unused cfsom_or.ty example file

	* [r9801] examples/tiny.ty:
	  Updated to match lissom.ty style parameters

	* [r9800] examples/lissom_oo_or.ty:
	  Fixed previous checkin

	* [r9799] examples/lissom.ty,
	  examples/lissom_oo_or.ty:
	  Cleaned up and expanded docs and params

	* [r9798] examples/lissom.ty:
	  Cleaned up and expanded docs and params

	* [r9797] examples/lissom.ty:
	  Renamed density parameters to avoid confusing 'default'

2009-01-20  antolikjan

	* [r9796]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  loads of small changes

2009-01-20  ceball

	* [r9795] contrib/lissom.ty,
	  examples/lissom.ty,
	  topo/command/pylabplots.py,
	  topo/plotting/plotgroup.py,
	  topo/tkgui/plotgrouppanel.py,
	  topo/tkgui/testpattern.py:
	  Renamed Plotgroup's plot_command to plot_hooks.

	* [r9794] contrib/jsldefs.py,
	  contrib/lesi.ty,
	  contrib/lesi_whisker_barrels.ty,
	  contrib/lissom.ty,
	  contrib/lissom_oo_or_species_tracked.ty,
	  contrib/species_cf_jitter.ty,
	  contrib/species_lateral_sparsity.ty,
	  doc/User_Manual/commandline_text.php,
	  examples/lissom.ty,
	  examples/lissom_whisker_barrels.ty,
	  topo/analysis/featureresponses.py,
	  topo/analysis/vision.py,
	  topo/command/analysis.py,
	  topo/command/pylabplots.py,
	  topo/param/parameterized.py,
	  topo/plotting/plotgroup.py,
	  topo/tests/gui_tests.py,
	  topo/tests/test_map_measurement.py,
	  topo/tkgui/plotgrouppanel.py,
	  topo/tkgui/testpattern.py:
	  Renamed Plotgroup's update_command to pre_plot_hooks.

2009-01-20  jbednar

	* [r9793] topo/misc/legacy.py:
	  Minor fix to comment

2009-01-20  ceball

	* [r9792] topo/param/__init__.py:
	  Added some comments.

	* [r9791] topo/tkgui/projectionpanel.py:
	  UnitsPanel now knows which sheet bounds are exclusive, and passes
	  that information to its sliders.

	* [r9790] topo/param/tk.py:
	  TaggedSlider now supports exclusive bounds.

	* [r9789] topo/misc/legacy.py,
	  topo/param/__init__.py:
	  Allow Number to work with exclusive bounds.

2009-01-18  jbednar

	* [r9788] examples/lissom.ty:
	  Cleaned up parameter formatting

2009-01-18  ceball

	* [r9787] topo/command/pylabplots.py:
	  Removed stray print statement.

	* [r9786] topo/base/parameterclasses.py,
	  topo/tests/testsheetview.py:
	  Removed topo/base/parameterclasses.py.

	* [r9785] doc/User_Manual/commandline_text.php,
	  examples/gc_alissom.ty,
	  examples/goodhill_network90.ty,
	  examples/leaky_lissom_or.ty,
	  examples/obermayer_pnas90.ty,
	  examples/saccade_demo.ty,
	  examples/tiny.ty,
	  topo/command/analysis.py,
	  topo/command/basic.py,
	  topo/misc/legacy.py,
	  topo/sheet/generator.py,
	  topo/sheet/saccade.py,
	  topo/tests/gui_tests.py,
	  topo/tests/reference/fixed_params/lissom_oo_or_reference_fixed.ty,
	  topo/tests/reference/lissom_fsa_reference.ty,
	  topo/tests/reference/lissom_oo_dr_reference.ty,
	  topo/tests/reference/lissom_oo_or_reference.ty,
	  topo/tests/reference/lissom_or_reference.ty,
	  topo/tests/testCompositePatternGenerators.txt,
	  topo/tests/testcfsom.py,
	  topo/tests/testfeaturemap.py,
	  topo/tests/testplotfilesaver.py,
	  topo/tests/testsnapshots.py,
	  topo/tests/utils.py,
	  topo/tkgui/plotgrouppanel.py,
	  topo/tkgui/projectionpanel.py,
	  topo/tkgui/testpattern.py:
	  Removed topo/sheet/generator.py.

	* [r9784] examples/lissom.ty:
	  Fixed typo (introduced during a git merge).

	* [r9783] examples/lissom.ty:
	  Simplified setting of default value of default_retina_density.

	* [r9782] topo/param/parameterized.py:
	  Added set_default() to Parameterized. x.set_default(name,val) is
	  a simple way of doing x.params(name).default=val, or,
	  equivalently, setattr(type(x),name,val).

	* [r9781] topo/misc/commandline.py:
	  Renamed -s to -p (for parameter setting, to match 'p' used
	  elsewhere.

	* [r9780] examples/lissom.ty:
	  Import global_params as p to match existing convention.

	* [r9779] examples/lissom.ty:
	  Simplified setting of default_retina_density.

	* [r9778] examples/lissom.ty:
	  Begin to use global_params in lissom.ty.

	* [r9777] examples/lissom.ty:
	  Fixed typo.

	* [r9776] examples/lissom.ty:
	  Random input pattern parameters now use a seed generated from a
	  single base seed, allowing all random input parameters to be
	  changed at once. Simulations using Gaussian input patterns will
	  now have different results (differences should be insignificant)
	  because the input seeds have changed in that case.

2009-01-15  antolikjan

	* [r9775] topo/command/pylabplots.py:
	  Made orientation tuning curve plots have limited number of xticks
	  (they will allways now have 7)

2009-01-15  ceball

	* [r9774] topo/misc/commandline.py:
	  GlobalParams: set name to 'global_params' to match other uses.

	* [r9773] topo/misc/commandline.py:
	  GlobalParams: added warning for duplicate parameter specification
	  after any scripts have been executed (already detects duplicate
	  specifications before scripts are executed.

2009-01-15  antolikjan

	* [r9772] topo/analysis/vision.py:
	  improved the phase scatter plot

	* [r9771] topo/command/pylabplots.py:
	  more update to plot_modulation_ratio

2009-01-15  ceball

	* [r9770] examples/lissom.ty:
	  Image inputs: all random streams (i.e. all random parameters for
	  all images) now have a distinct seed. Shouldn't change results
	  significantly.

2009-01-15  antolikjan

	* [r9769] topo/command/pylabplots.py:
	  repaired plot_modultion_ratio

2009-01-15  ceball

	* [r9768] examples/lissom.ty:
	  Image inputs: made selection of input patch (x and y), plus
	  orientation of the patch, have dfferent random number streams for
	  each image (rather than every different image having the same
	  stream of x, y, and orientation). Although simulation results
	  will change, they should not be different in any significant way.

2009-01-15  jbednar

	* [r9767] topo/pattern/image.py:
	  Fixed confusing attribute name

	* [r9766] topo/base/sheetview.py,
	  topo/plotting/plot.py:
	  Made row_precedence always be 0.5 by default, to fix sf bug
	  #2456002

2009-01-15  antolikjan

	* [r9765] examples/gc_alissom.ty:
	  changes to external parametrization

2009-01-13  ceball

	* [r9764] doc/Downloads/git_text.php,
	  doc/Future_Work/current_text.php:
	  More cleaning of git documentation.

	* [r9763] topo/base/simulation.py:
	  Fixed typo.

	* [r9762] doc/Downloads/git_text.php:
	  Minor cleanup.

2009-01-12  antolikjan

	* [r9761] contrib/cc_lissom_oo_or_simple_rv.ty:
	  chaneged some external parametrization

2009-01-12  ceball

	* [r9760] topo/command/basic.py:
	  Use global_params.set_in_context(), rather than
	  .exec_in_context(), for setting parameter values.

	* [r9759] topo/misc/commandline.py:
	  Added set_in_context() method to GlobalParams.

2009-01-12  antolikjan

	* [r9758]
	  contrib/gc_lissom_oo_or_homeostatic_new.ty:
	  changed SimpleHomeoLinear to SimpleHomeoLinearRelative

2009-01-12  ceball

	* [r9757] topo/command/basic.py:
	  Made snaphots include the GlobalParams instance.

	* [r9756] topo/misc/commandline.py:
	  Made GlobalParams not save its context attribute when it is
	  pickled.

	* [r9755] topo/param/parameterized.py:
	  Clarified a comment.

2009-01-12  antolikjan

	* [r9754] topo/analysis/vision.py:
	  small change to scatter plot : change of diameter and small bug
	  correction

2009-01-11  ceball

	* [r9753] doc/Future_Work/current_text.php:
	  Added some links for my future reference.

	* [r9752] examples/tiny.ty:
	  Changed to use global_params instead of locals().

	* [r9751] topo/command/basic.py:
	  Converted run_batch() to use global_params. Should be no change
	  for current users of run_batch(), except that warnings will be
	  printed about values being unused.

	* [r9750] topo/misc/commandline.py,
	  topo/param/__init__.py:
	  Moved MainParams class and mainparams variable from topo.param to
	  topo.misc. Renamed MainParams to GlobalParams, and mainparams to
	  global_params.

2009-01-09  jbednar

	* [r9749]
	  doc/Developer_Manual/optimization_text.php:
	  Fixed bogus title, and other minor cleanup for line-by-line
	  profiling

	* [r9748] topo/learningfn/optimized.py:
	  Added missing import

2009-01-09  antolikjan

	* [r9747] examples/gc_alissom.ty:
	  adding gc_allissom

2009-01-07  ceball

	* [r9746] topo/misc/legacy.py:
	  Added support for SineGratingDisk, SineGratingRectangle, and
	  SineGratingRing. Removed broken support for
	  topo.pattern.teststimuli (fixes failing snapshot test); support
	  could be restored if required.

2009-01-06  ceball

	* [r9745] topo/tests/utils.py:
	  Added docstring.

	* [r9744]
	  doc/Developer_Manual/optimization_text.php:
	  Added information about line-by-line profiling. SF.net feature
	  request #2478100.

	* [r9743] topo/misc/commandline.py:
	  Added -s (--set-parameters) option.

	* [r9742] topo/param/__init__.py:
	  MainParams: for specifically defined parameters (script-level
	  parameters specified on the commandline via -s), warn if
	  duplicate values are specified, and keep track of parameter names
	  so that unused parameters can be detected.

2009-01-04  ceball

	* [r9741] topo/param/__init__.py:
	  Added MainParams: support for script-level parameters.

	* [r9740] topo/base/simulation.py,
	  topo/param/parameterized.py:
	  Moved OptionalSingleton from topo.base.simulation to
	  topo.base.parameterized.

	* [r9739] topo/param/parameterized.py:
	  Made Parameterized._add_parameter() be callable by a class or
	  instance.

	* [r9738] topo/param/parameterized.py:
	  Added method to Parameterized allowing new Parameter objects to
	  be installed into a Parameterized class.

	* [r9737] topo/param/parameterized.py:
	  ParameterizedMetaclass: moved parameter initialization
	  (inheritance, attribute name setting) into a separate method.
	  Should be no visible change.

2009-01-03  ceball

	* [r9736] topo/param/parameterized.py:
	  When instantiating Parameters, avoid redundantly instantiating
	  objects from superclasses.

	* [r9735] topo/param/parameterized.py,
	  topo/tests/testparameterizedobject.py:
	  Fixed inheritance for Parameter's instantiate slot (SF #2483932).

	* [r9734] topo/misc/trace.py:
	  Fixed variable name in InMemoryRecorder's get_data().

	* [r9733] topo/sheet/basic.py:
	  Clarified ALERT.

2009-01-02  ceball

	* [r9732] topo/tests/utils.py:
	  Added wrapper that gives simple access to a generator (for test
	  files).

	* [r9731] contrib/tracker.py:
	  Classes for tracking attribute access.

2008-12-31  ceball

	* [r9730] external/Makefile,
	  external/line_profiler-582df342463a.tar.gz:
	  Added line_profiler, for line-by-line profiling. From
	  http://www.enthought.com/~rkern/cgi-bin/hgwebdir.cgi/line_profiler/
	  (last change: Sat, 29 Nov 2008 21:32:35 -0600).

	* [r9729] external/Cython-0.9.8.1.1.tar.gz,
	  external/Makefile:
	  Added Cython 0.9.8.1.1 from cython.org.

2008-12-27  ceball

	* [r9728] external/Imaging.diff,
	  external/Makefile:
	  Removed PIL patch that is no longer required (at least, it isn't
	  required on Sake).

2008-12-21  ceball

	* [r9727] contrib/rgbimages.py:
	  Use multiple input images in example.

	* [r9726] topo/command/analysis.py:
	  Added combined RedActivity, GreenActivity, BlueActivity plot.

	* [r9725] topo/analysis/featureresponses.py:
	  Removed unnecessary line; should have no effect.

	* [r9724] examples/lissom.ty:
	  Added row_precedence specifications.

	* [r9723] topo/tkgui/plotgrouppanel.py:
	  Added row_precedence handling to PlotGroupPanel.

	* [r9722] topo/analysis/featureresponses.py,
	  topo/analysis/vision.py,
	  topo/base/sheet.py,
	  topo/base/sheetview.py,
	  topo/command/analysis.py,
	  topo/command/pylabplots.py,
	  topo/plotting/plot.py:
	  Added row_precedence to Sheet, to allow grouping before
	  precedence is applied. (Handling of parameters by SheetView etc
	  needs to be cleaned up; this change just copies previous code in
	  that respect.)

2008-12-20  ceball

	* [r9721] external/Makefile,
	  external/Tkinter_bool_none.diff,
	  topo/param/tk.py:
	  GUI: Added support for None in boolean variables.

	* [r9720] topo/param/parameterized.py,
	  topo/param/tk.py:
	  Made GUI use script_repr() rather than repr() for displaying
	  ordinary Parameters. Currently has the side effect that full
	  paths are displayed (e.g.
	  'topo.command.analysis.update_command()' rather than just
	  'update_command()').

	* [r9719] topo/param/tk.py:
	  Added parameter to control whether or not labels are displayed on
	  ParametersFrames.

2008-12-19  jbednar

	* [r9718] topo/pattern/basic.py:
	  Fixed typo

	* [r9717] topo/pattern/teststimuli.py:
	  Removed now-unused file

	* [r9716] topo/pattern/random.py:
	  Removed outdated note

	* [r9715] topo/misc/legacy.py:
	  Added note about faking SineGratingDisk

	* [r9714] topo/analysis/featureresponses.py,
	  topo/command/pylabplots.py,
	  topo/pattern/basic.py:
	  Added new, simpler OrientationContrast pattern, and changed
	  clients of OrientationContrastPattern to use it instead.

	* [r9713] topo/command/pylabplots.py,
	  topo/tests/lissom_oo_or_t000100.00_Retinotopy.data:
	  Changed SineGratingRectangle to
	  SineGrating(mask_shape=Rectangle()). Updated saved Retinotopy
	  data array; plot hasn't visibly changed, but apparently the
	  underlying matrix values differ.

	* [r9712] topo/analysis/featureresponses.py:
	  Replaced SineGratingDisk with SineGrating(mask_shape=Disk())

	* [r9711] topo/base/patterngenerator.py:
	  Changed pattern mask to be applied before scaling and offset, to
	  allow mask to be used to set the shape but otherwise leave the
	  pattern acting like other patterns.

	* [r9710]
	  contrib/lissom_oo_or_species_tracked.ty,
	  contrib/species_cf_jitter.ty,
	  contrib/species_lateral_sparsity.ty,
	  topo/analysis/featureresponses.py,
	  topo/command/pylabplots.py,
	  topo/pattern/teststimuli.py,
	  topo/tkgui/editor.py:
	  Fixed 'centre' to be 'center' to make spelling consistent

	* [r9709]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  Fixed typo

2008-12-19  ceball

	* [r9708] external/Makefile:
	  Enabled patch to address SF #2119256 (32-bit/64-bit machines &
	  snapshots).

	* [r9707] external/Makefile,
	  external/Python_64bit_pickle.diff:
	  Added commented-out patch to Python to address problem loading
	  32-bit pickles on 64-bit machines (and vice versa).

2008-12-18  antolikjan

	* [r9706]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  minor changes

2008-12-18  jbednar

	* [r9705] topo/command/pylabplots.py:
	  Removed outdated processing of sheet and coords params

2008-12-18  antolikjan

	* [r9704] contrib/cc_lissom_oo_or_simple_rv.ty:
	  minor changes

2008-12-18  jbednar

	* [r9703] topo/command/pylabplots.py,
	  topo/tkgui/templateplotgrouppanel.py:
	  Moved implementation of FFT plots out of the GUI and into
	  pytlabplots, to make it possible to call in batch mode. Fixed
	  parameter passing for gradientplots, for the same reason.

2008-12-17  antolikjan

	* [r9702] topo/analysis/vision.py:
	  removed default parameters from measure_and_analyze_complexity
	  measure_or_pref call

2008-12-17  ceball

	* [r9701] external:
	  Updated svn:ignore.

	* [r9700] external/Makefile,
	  external/tcl8.5.1-src.tar.gz,
	  external/tcl8.5.5-src.tar.gz,
	  external/tk8.5.1-src.tar.gz,
	  external/tk8.5.5-src.tar.gz:
	  Upgraded to Tcl/Tk 8.5.5.

	* [r9699] external/Imaging-1.1.5.tgz,
	  external/Imaging-1.1.6.tgz,
	  external/Makefile:
	  Upgraded to PIL 1.1.6.

	* [r9698] topo/plotting/plotfilesaver.py:
	  Explicitly specified array dtype in preparation for upgrade to
	  PIL 1.1.6.

2008-12-16  ceball

	* [r9697] examples/lissom.ty:
	  Fixed bug introduced in r9682 (when I fixed the bug where scale
	  was varying when there was no OD, I inadvertently removed the
	  'scalingfactors' for natural images).

	* [r9696] topo/pattern/basic.py:
	  Altered Selector's get_current_generator() so that it does not
	  cause the index to advance.

2008-12-16  antolikjan

	* [r9695]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  minor changes

	* [r9694] contrib/jacommands.py:
	  "changed to use x_avg instead of lr_x_avg in
	  SimpleHomeoLinearRelative"

	* [r9693] contrib/jsldefs.py:
	  "commented out some things and also change lr_x_avg to x_avg"

	* [r9692] topo/sheet/lissom.py:
	  "made it possible to switch off scaling with parameter"

2008-12-15  ceball

	* [r9691] contrib/rgbimages.py:
	  Initial sketch of RGB image support; work in progress.

	* [r9690] topo/pattern/basic.py:
	  Added method to Selector allowing external access to the current
	  generator.

	* [r9689] topo/pattern/image.py:
	  Removed _create_pattern_sampler() (should be no visible change).

	* [r9688] topo/pattern/image.py:
	  Removed apparently unused method.

	* [r9687] topo/pattern/image.py:
	  Renamed __setup_pattern_sampler() to _create_pattern_sampler()
	  (so it can be used by subclasses).

2008-12-15  antolikjan

	* [r9686] contrib/cc_lissom_oo_or_simple_rv.ty:
	  minor parameter changes

	* [r9685]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  made LGN and Retina bigger to get rid of edge effects

	* [r9684] contrib/cc_lissom_oo_or_simple_rv.ty:
	  made new default scale for map measurment

2008-12-12  antolikjan

	* [r9683] contrib/jacommands.py:
	  changed the activity histogram measurement

2008-12-12  ceball

	* [r9682] examples/lissom.ty:
	  Fixed input pattern scale where 'od' not in dims (SF #2413540).

2008-12-11  chrisjeffery

	* [r9681] contrib/lissom.ty:
	  added new direction map measurement, which is not working. Also
	  added changes from examples/lissom.ty for preference maps.

2008-12-10  antolikjan

	* [r9680]
	  contrib/gc_lissom_oo_or_homeostatic_new.ty:
	  enlarged LGN and Retina to get rid of edge effects

2008-12-10  ceball

	* [r9679] contrib/lissom_oo_dr.ty:
	  Adjusted parameters to match lissom.ty dims=or,dr.

2008-12-09  antolikjan

	* [r9678] contrib/cc_lissom_oo_or_simple_rv.ty:
	  added simple linear homeostatic control

2008-12-09  chrisjeffery

	* [r9677] contrib/lissom.ty:
	  Forked lissom.ty for separate development of new dr model.
	  Currently broken, just checking in to keep track of changes.
	  Removed multiple sheets for direction, and changed connections to
	  use staggered delays. Inputs are not set up correctly yet.

2008-12-08  jbednar

	* [r9676] examples/lissom.ty:
	  Updated combined plots definitions to match recent changes in
	  topo.command.

	* [r9675] topo/command/pylabplots.py:
	  Made overlaid_plots arguments into documented Parameters.

2008-12-08  ceball

	* [r9674] topo/param/tk.py:
	  More simplification of param.tk.Menu. Should be no visible
	  change.

	* [r9673] topo/param/tk.py:
	  Should be no visible change: updated documentation of
	  param.tk.Menu

	* [r9672] topo/param/tk.py:
	  Fixed SF #2406957 (right-click menus broken).

2008-12-08  antolikjan

	* [r9671] contrib/cc_lissom_oo_or_simple_rv.ty:
	  "Made some consolidation/simplification of the code"

2008-12-08  jbednar

	* [r9670] doc/News/index_text.php:
	  Added recent news (up to r9630)

	* [r9669] topo/command/pylabplots.py:
	  Fixed circular import and made topo.analysis.vision be loaded
	  only when required

2008-12-06  jbednar

	* [r9668] topo/tkgui/topoconsole.py:
	  Removed unused plot

2008-12-05  jbednar

	* [r9667] topo/analysis/featureresponses.py,
	  topo/command/pylabplots.py,
	  topo/plotting/plotgroup.py:
	  Changed update_command and plot_command into HookLists, now
	  requiring lists rather than commands or strings. Changed passing
	  of sheet, input_sheet, projection, and coords arguments to be
	  done by calling the instance with those values, rather than the
	  previous indirect, complicated, and error-prone method of setting
	  various class attributes. Changed default_measureable_sheet and
	  default_input_sheet to be calculated in the plotgroup rather than
	  separately in the update_command and plot_command (with the
	  accompanying difficulty making the values match).

2008-12-05  antolikjan

	* [r9666] contrib/jacommands.py:
	  SimpleHomeoLinearRelative

2008-12-05  jbednar

	* [r9665] contrib/jacommands.py:
	  Typo fixes

2008-12-05  antolikjan

	* [r9664]
	  contrib/lissom_oo_or_homeostatic_tracked_new.ty:
	  Modified version of judes homeostatic model with GC

	* [r9663] contrib/jacommands.py:
	  Added SimpleHomeoLinear and SimpleHomeoLinearRelative

2008-12-05  jbednar

	* [r9662] ChangeLog.txt:
	  Added recent changes

	* [r9661] doc/Home/news_text.php:
	  Updated release date estimate

	* [r9660] topo/command/basic.py:
	  Added ALERT

2008-12-04  jbednar

	* [r9659] topo/command/analysis.py:
	  Removed unused imports

	* [r9658] topo/command/pylabplots.py,
	  topo/plotting/plotgroup.py:
	  Converted plot_commands from strings to lists of callables. Added
	  parameters to measure_cog.

2008-12-04  ceball

	* [r9657] contrib/lissom_oo_dr.ty,
	  topo/analysis/featureresponses.py,
	  topo/command/basic.py:
	  Added direction map measurement for new motion model.

2008-12-04  jbednar

	* [r9656] topo/plotting/plotgroup.py:
	  Added support for plot_command lists

	* [r9655] topo/command/analysis.py,
	  topo/command/pylabplots.py,
	  topo/tests/gui_tests.py,
	  topo/tests/test_map_measurement.py:
	  Moved all plots requiring MatPlotLib to pylabplots.py, so that
	  they can switch plot_command from strings to actual commands
	  (which much thus have all imports be available). Should not
	  change behavior at all.

	* [r9654] doc/User_Manual/commandline_text.php:
	  Minor update to example

	* [r9653] contrib/lesi_whisker_barrels.ty,
	  examples/lissom.ty,
	  examples/lissom_whisker_barrels.ty,
	  topo/analysis/featureresponses.py,
	  topo/analysis/vision.py,
	  topo/command/analysis.py,
	  topo/plotting/plotgroup.py,
	  topo/tests/gui_tests.py:
	  Changed ParameterizedFunction update_commands to use .instance()
	  to allow flexible handling of their parameters. Changed plot
	  update_commands into lists, to allow them to be declared as type
	  HookList and to provide a simple [] empty default. Cleaned up
	  PatternPresenter warnings to avoid overwhelming output.

	* [r9652] doc/Tutorials/lissom_oo_or_text.php:
	  Minor clarification

2008-12-04  ceball

	* [r9651] contrib/lissom_oo_dr.ty,
	  topo/pattern/basic.py:
	  Moved Translator(PatternGenerator) to topo.pattern.basic.

2008-12-03  ceball

	* [r9650] examples/lissom.ty:
	  Initial version of ocular preference overlaid with hue preference
	  boundaries.

	* [r9649] examples/lissom.ty,
	  topo/command/analysis.py:
	  Moved combined plots to lissom.ty; script selects appropriate
	  combinations (depending on dims).

2008-12-02  ceball

	* [r9648] topo/tkgui/topoconsole.py:
	  Added method to allow Plots menu to be refreshed.

	* [r9647] topo/param/tk.py:
	  param.tk.Menu: fixed deletion of a range.

	* [r9646] topo/param/tk.py:
	  Cleaned up tk.param.Menu (simplified code and fixed deletion of
	  items).

	* [r9645] topo/tkgui/topoconsole.py:
	  Change missed from r9644.

	* [r9644] topo/param/tk.py:
	  tk.param.Menu: Renamed 'entries' to 'named_commands'; Menu now
	  only stores commands in named_commands if they are actually
	  named.

	* [r9643] topo/param/tk.py:
	  Change missed from r9641 (insert() now adds the index as a
	  string).

	* [r9642] topo/param/tk.py:
	  param.tk.Menu: fixed delete() method, which removed the internal
	  index before actually deleting the associated menu item.

	* [r9641] topo/param/tk.py:
	  Made param.tk.Menu's internal indexing more consistent (if an
	  index has no name associated with it, its string representation
	  is used as a key in the internal name-index dictionary, to match
	  how named items are stored). Should have no visible impact.

	* [r9640] topo/tkgui/topoconsole.py:
	  Topoconsole now alphabetically sorts Plot submenu items.

2008-12-01  ceball

	* [r9639] topo/param/parameterized.py:
	  Fixed ParameterizedFunction's __reduce__ (was resulting in
	  reconstructed instances reverting to ParameterizedFunctions,
	  instead of whatever subclass they were).

2008-12-01  antolikjan

	* [r9638] contrib/sparse_connectivity_model.ty:
	  Made few parameters external

	* [r9637]
	  contrib/gc_lissom_oo_or_homeostatic_new.ty:
	  Made few parameters external

2008-11-29  ceball

	* [r9636] topo/plotting/bitmap.py:
	  Minor simplification: should be no visible change.

	* [r9635] topo/misc/filepath.py:
	  Made resolve_path() raise an error if a file is not found when an
	  absolute path is supplied (it already raises an error when an
	  unfound relative path is supplied, so now it is more consistent).

	* [r9634] doc/User_Manual/batch_text.php:
	  Fixed reference.

2008-11-27  rczhao

	* [r9633] /trunk/facespace/fs1mf.ty:
	  Added measure_or_in_face function

2008-11-25  ceball

	* [r9632] topo/plotting/plot.py:
	  Removed unused import.

2008-11-25  jbednar

	* [r9631] topo/command/analysis.py:
	  Removed unused measure_rfs_noise class

2008-11-24  ceball

	* [r9630] examples/lissom.ty:
	  Fixed typo.




<p><b>25 November 2008:</b> Version 0.9.6 is in preparation;
updates are currently available in the latest SVN version:

<!-- So far updated only to r9630 -->
<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<!--CB: surely these divs should be some kind of li?-->
<!--  <div class="i2">- optional XML snapshot
  <A HREF="../Reference_Manual/topo.command.basic-module.html#save_snapshot">saving</A> and
  <A HREF="../Reference_Manual/topo.command.basic-module.html#load_snapshot">loading</A></div>
-->
<!-- incomplete <A HREF="../Downloads/git.html">Instructions</A> for checking out Git version of repository<BR> -->
<!--  mouse model (examples/lissom_oo_or_species.ty)<BR> -->
<dt>General improvements:</dt>
<dd>
<!--CB: surely these divs should be some kind of li?-->
  <div class="i2">- significant performance improvements (nearly 2X)</div>
  <div class="i2">- significant startup time improvements for large networks</div>
  <div class="i2">- minor bugfixes</div>
<!--  <div class="i2">- updated Windows packages</div> -->
  <div class="i2">- more options for 
  <A target="_top" href="../User_Manual/noise.html">adding noise</A>
  to ConnectionField shapes</div>
</dd>
<dt>GUI:</dt>
<dd>
  <div class="i2">- model editor supports non-Sheet EventProcessors
  and non-CFProjection EPConnections</div>
  <div class="i2">- right-click option for plotting tuning curves</div>
</dd>
<dt>Component library:</dt>
<dd>
  <div class="i2">- PatternGenerators: 
  <?php classref('topo.pattern.basic','Translator')?>; 
    mask_shape parameter also now makes it easy to specify a mask
    for any pattern, e.g. in the GUI</div>
  <div class="i2">- OutputFns: 
  <?php classref('topo.outputfn.basic','HalfRectifyAndPower')?></div>
  <div class="i2">- Sheets: 
  <?php classref('topo.sheet.basic','ActivityCopy')?></div>
  <div class="i2">- LearningFns: 
  <?php classref('topo.learningfn.optimized','CFPLF_BCMFixed_opt')?>,
  <?php classref('topo.learningfn.optimized','CFPLF_Scaled_opt')?></div>
  <div class="i2">- Added <?php classref('topo.param','HookList')?>
  parameters to
  <?php classref('topo.analysis.featureresponses','FeatureResponses')?> and
  <?php classref('topo.sheet.lissom','LISSOM')?> to make it easier to
  add user-defined functionality.</div>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>Command-line and batch:</dt>
<dd>
  <div class="i2">- -v option to print verbose messages</div>
  <div class="i2">- -d option to print debugging messages</div>
  <div class="i2">- new options to
  <?php classref('topo.command.basic','run_batch')?> and better progress messages</div>
  <div class="i2">- replaced most commands with
  <?php classref('topo.param.parameterized','ParameterizedFunction')?>s,
  which have documented, type and bound-checked arguments and allow
  inheritance of shared functionality</div>
  <div class="i2">- replaced map measurement commands in
  <A target="_top" HREF="../Reference_Manual/topo.command-module.html">topo.command</A>
  with simpler, general-purpose, easily .ty-file controllable versions (see
  lissom_oo_or.ty and lissom.ty for examples)</div>
  <div class="i2">- <?php classref('topo.command.analysis','save_plotgroup')?>: 
  more useful default values; results can be cached to avoid recomputation</div>
  <div class="i2">- <?php classref('topo.command.analysis','measure_sine_pref')?>:
  general purpose measurement for any preference that can be tested
  with a sine grating</div>
  <div class="i2">- Added support for script-level parameters 
  (<?php classref('topo.misc.commandline','GlobalParams')?>;
  see examples/lissom.ty</div>
</dd>
<dt>Example scripts:</dt>
<dd>
  <div class="i2">- example file for
  <a href="../User_Manual/interfacing.html">interfacing to external simulators</a>
  (examples/perrinet_retina.ty)</div>
  <div class="i2">- removed outdated or in-progress examples</div>
  <div class="i2">- greatly simplified remaining example scripts</div>
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>


<p><b>05 September 2008:</b> Version 0.9.5 
<A target="_top" href="../Downloads/index.html">released</A>, including:
<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
<!--CB: surely these divs should be some kind of li?-->
  <div class="i2">- numerous bugfixes and performance improvements</div>
<!-- fixed a number of pychecker warnings.<BR> -->
<!-- moved current to-do items to the sf.net trackers<BR> -->
<!-- EventProcessor.start() run only when Simulation starts, e.g. to allow joint normalization across a Sheet's projections<BR> -->

  <div class="i2">- simulation can now be locked to real time</div>

<!--  <div class="i2">- optional XML snapshot
  <A HREF="../Reference_Manual/topo.command.basic-module.html#save_snapshot">saving</A> and
  <A HREF="../Reference_Manual/topo.command.basic-module.html#load_snapshot">loading</A></div>
-->

  <div class="i2">- simpler and more complete support for dynamic parameters</div>  
<!-- dynamic parameters now update at most once per simulation time<BR> -->

  <div class="i2">- updated to Python 2.5 and numpy 1.1.1.</div>

  <div class="i2">- source code moved from CVS to Subversion (<A HREF="../Downloads/cvs.html">SVN</A>)</div>
<!--  replaced FixedPoint with gmpy for speed and to have rational no. for time<BR> -->
  <div class="i2">- automatic Windows and Mac <A target="_top" href="http://buildbot.topographica.org">daily builds</A></div>
  <div class="i2">- automatic running and startup <A target="_top" href="http://buildbot.topographica.org">performance measurement</A></div>
<!--CEBALERT: we're removing that for the release!-->
  <div class="i2">- contrib dir</div>
  <div class="i2">- divisive and multiplicative connections</div>
  <div class="i2">- simulation time is now a rational number for precision</div>
  <div class="i2">- PyTables HDF5 interface</div>
  <div class="i2">- more options for 
  <A target="_top" href="../User_Manual/noise.html">adding noise</A></div>
<!-- topo/misc/legacy.py i.e. we can now support old snapshots if necessary<BR> -->
<!-- incomplete <A HREF="../Downloads/git.html">Instructions</A> for checking out Git version of repository<BR> -->
</dd>
<BR>
<dt>Command-line and batch:</dt>
<dd>
  <div class="i2">- simplified example file syntax
  (see examples/lissom_oo_or.ty and som_retinotopy.py)</div>
  <div class="i2">- command prompt uses <A HREF="http://ipython.scipy.org/">IPython</A> for better debugging, help</div>
  <div class="i2">- simulation name set automatically from .ty script name by default</div>
  <div class="i2">- command-line options can be called explicitly</div>
  <!-- , e.g.
  <A HREF="../Reference_Manual/topo.misc.commandline-module.html#gui">topo.misc.commandline.gui()</A> or
  ;<A HREF="../Reference_Manual/topo.misc.commandline-module.html#auto_import_commands">topo.misc.commandline.auto_import_commands()</A><BR>-->
</dd>
<BR>
<dt>GUI:</dt>
<dd>
  <div class="i2">- model editor fully supports dynamic parameters
  (described in the lissom_oo_or tutorial)</div>
  <div class="i2">- plot windows can be docked into main window</div>
  <div class="i2">- uses tk8.5 for anti-aliased fonts <!--and potential to move to platform-specific themes--></div>
<!--  cleaned up ParametersFrame and TaggedSlider behavior<BR> -->
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>Plotting:</dt>
<dd>
  <div class="i2">- new preference map types (Hue, Direction, Speed)</div>
  <div class="i2">- combined (joint) plots using contour and arrow overlays</div>
  <div class="i2">- example of generating activity movies
  (examples/lissom_or_movie.ty)</div>
</dd>
<BR>
<dt>Example scripts:</dt>
<dd>
  <div class="i2">- example files for robotics interfacing (<A HREF="../Reference_Manual/topo.misc.playerrobot-module.html">misc/playerrobot.py</A>,
  <A HREF="../Reference_Manual/topo.misc.robotics-module.html">misc/robotics.py</A>)</div>
  <div class="i2">- simulation, plots, and analysis for modelling of any combination of position, orientation, ocular dominance, stereoscopic disparity, motion direction, speed, spatial frequency, and color (examples/lissom.ty).</div>
<!--  mouse model (examples/lissom_oo_or_species.ty)<BR> -->
</dd>
<BR>
<dt>Component library:</dt>
<dd>
  <div class="i2">- OutputFns: 
  <?php classref('topo.outputfn.basic','PoissonSample')?>,<BR>
  <?php classref('topo.outputfn.basic','ScalingOF')?> (for homeostatic plasticity),<BR>
  <?php classref('topo.outputfn.basic','NakaRushton')?> (for contrast gain control)<BR>
  <?php classref('topo.outputfn.basic','AttributeTrackingOF')?> (for analyzing or plotting values over time)</div>
<!-- &nbsp;&nbsp;&nbsp;('x=HalfRectify() ; y=Square() ; z=x+y' gives 'z==PipelineOF(output_fns=x,y)')<BR> -->
<div class="i2">- PatternGenerator: <?php classref('topo.misc.robotics','CameraImage')?> (for real-time camera inputs)</div>
<!--  allowed <?php classref('topo.sheet.lissom','LISSOM')?>  normalization to be 
  <A HREF="../Reference_Manual/topo.sheet.lissom.LISSOM-class.html#post_initialization_weights_output_fn">changed</A>
  after initialization<BR> -->

  <div class="i2">- CoordMapper: <?php classref('topo.coordmapper.basic','Jitter')?></div>
  <div class="i2">- SheetMasks: <?php classref('topo.base.projection','AndMask')?>,
  <?php classref('topo.base.projection','OrMask')?>,
  <?php classref('topo.base.projection','CompositeSheetMask')?></div>
  <div class="i2">- command: <A HREF="../Reference_Manual/topo.command.analysis-module.html#decode_feature">decode_feature</A> (for estimating perceived values)
  (e.g. for calculating aftereffects)</div>
  <div class="i2">- functions for analyzing V1 complex cells</div>
  <div class="i2">- <?php classref('topo.base.functionfamily','PipelineOF')?> OutputFns can now be constructed easily using +</div>
  <div class="i2">- <?php classref('topo.numbergen.basic','NumberGenerator')?>s
  can now be constructed using +,-,/,*,abs etc.
<!-- (e.g. abs(2*UniformRandom()-5) is now a NumberGenerator too).--></div>
<!-- provide stop_updating and restore_updating to allow functions with state to freeze their state<BR> -->
</dd>
</font>
</dl>
</td>
</tr>
<tr><td colspan='2'><small>We also provide a utility to <A
HREF="../Downloads/update_script.html">update scripts</A>
that were written for version 0.9.4.</small> </td></tr>
</table>
</center>

<p><b>26 October 2007:</b> Version 0.9.4 
<A target="_top" href="../Downloads/index.html">released</A>, including:

<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes<br>
  set up <A target="_top" href="http://buildbot.topographica.org">automatic daily builds</A><br>
</dd>
<dt>Example scripts:</dt>
<dd>
  new whisker barrel cortex simulation<br>
  &nbsp;&nbsp;(using transparent Matlab wrapper)<br>
  new elastic net ocular dominance simulation<br>
  new spiking example; still needs generalizing<br>
</dd>
<dt>Command-line and batch:</dt>
<dd>
  <!-- <A target="_top" href="../User_Manual/commandline.html#option-a">-a
  option to import commands automatically<br> -->
  <A target="_top" href="../User_Manual/batch.html">batch 
  mode</A> for running multiple similar simulations<br>
  <A target="_top" href="../User_Manual/commandline.html#saving-bitmaps">saving 
  bitmaps</A> from script/command-line (for batch runs)<br>
  script/command-line <A target="_top" href="../User_Manual/commandline.html#scripting-gui">control over GUI</A><br>
  <!-- grid_layout command to simplify model diagrams<br> -->
  <!-- options for controlling plot sizing<br> -->
  added auto-import option (-a and -g) to save typing<br>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  greatly simplified adding GUI code <!--<A target="_top" href="../Developer_Manual/gui.html#programming-tkgui">adding GUI code</A>--><br>
  <!--  added GUI tests<br> -->
  <!--  added optional pretty-printing for parameter names in GUI<br> -->
  added progress bars, scroll bars, window icons<br>
  new Step button on console
  <!-- changed -g to launch the GUI where it is specified, to allow more control<br> -->
  <!-- added categories for plots to simplify GUI<br> -->
</dd>
<dt>Plotting:</dt>
<dd>
  <A target="_top" href="../User_Manual/plotting.html#rfplots">reverse-correlation RF mapping</A><br>
  <A target="_top" href="../User_Manual/commandline.html#3d-plotting">3D 
  wireframe plotting</A> (in right-click menu)<br>
  gradient plots, histogram plots (in right-click menu)<br>
  <A target="_top" href="../User_Manual/plotting.html#measuring-preference-maps">simplified
  bitmap plotting</A> (removed template classes)<br>
  GUI plots can be saved as PNG or EPS (right-click menu)<br>
  automatic collection of plots for animations (see ./topographica examples/lissom_or_movie.ty)<br>
</dd>
<dt>Component library:</dt>
<dd>
  new
  <A HREF="../Reference_Manual/topo.coordmapper-module.html">
  coordmapper</A>s (Grid, Pipeline, Polar/Cartesian)<br>
  <!-- OutputFnDebugger for keeping track of statistics<br> -->
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>

Screenshots: 
<A target="_top" href="../images/071018_plotting1_ubuntu.png">plotting 1</A>, 
<A target="_top" href="../images/071018_plotting2_ubuntu.png">plotting 2</A>, 
<A target="_top" href="../images/071018_modeleditor_ubuntu.png">model editor</A>.
<br><br>

<p><b>23 April 2007:</b> Version 0.9.3 
<A target="_top" href="../Downloads/index.html">released</A>, including:

<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes<br>
  significant optimizations (~5 times faster)<br>
  <!-- (about 5 times faster than 0.9.2 for most scripts, with more improvements to come)<br>  -->
  compressed snapshots (1/3 as large)<br>
  <!-- more comprehensive test suite checking both speed and functionality<br> -->
  much-improved reference manual<br>
  <!-- arrays based on Numpy rather than Numeric<br> -->
</dd>
<dt>Component library:</dt>
<dd>
  adding noise to any calculation<br>
  lesioning units and non-rectangular sheet shapes (see PatternCombine)<br>
  basic auditory pattern generation<br>
<!--  greatly simplified convolutions<br>--> <!-- SharedWeightCFProjection -->
  greatly simplified SOM support<br> <!-- now can be mixed and matched with any other components<br> -->
  more dynamic parameters (such as ExponentialDecay)<br> 
  flexible mapping of ConnectionField centers between sheets<br>
</dd>
<dt>Example scripts:</dt>
<dd>
  examples that more closely match published simulations<br>
  new simulations for face processing and for
  self-organization from natural images<br>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  Better OS X and Windows support<br>
  progress reporting for map measurement<br>
  dynamic display of coordinates in plots<br>
  stop button to interrupt training safely<br>
  ability to plot and analyze during training<br>
  right-click menu for analysis of bitmap plots<br>
  saving current simulation as an editable .ty script<br>
</dd>
<dt>Command-line and batch:</dt>
<dd>
<!--  more-informative command prompt<br> -->
  site-specific commands in ~/.topographicarc<br>
  simple functions for doing optimization<br>
<!--  saving of plot data with snapshots<br> -->
</dd>
<dt>Plotting:</dt>
<dd>
  spatial frequency map plots<br>
  tuning curve plots<br>
  FFT transforms (in right-click menu)<br>
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>

Screenshots: 
<A target="_top" href="../images/topographica-0.9.3_ubuntu.png">Plotting</A>, 
<A target="_top" href="../images/topographica-0.9.3_modeleditor_ubuntu.png">Model editor</A>.
<br><br>


<p><b>29 November 2006:</b> There will be a short talk on Topographica
at the <A target="_top" href="http://us.pycon.org/TX2007/">PyCon 2007</A>
convention, February 23-25, 2007.
<br><br>

<p><b>22 November 2006:</b> Version 0.9.2
<A target="_top" href="../Downloads/index.html">released</A>, including
numerous bugfixes (e.g. to support GCC 4.1.x compilers),
much more complete user manual,
more useful reference manual,
more sample models,
flexible joint normalization across Projections,
arbitrary control of mapping CF centers (see CoordinateMapperFn),
Composite and Selector patterns to allow flexible combinations of input patterns,
homeostatic learning and output functions,
sigmoid and generalized logistic output functions,
and a new disparity map example (including a
random dot stereogram input pattern).
<!-- Choice class to select randomly from a list of choices -->
<br><br>

<p><b>02 November 2006:</b> Some users have reported problems when using
optimized code on systems with the most recent GCC 4.1.x C/C++
compilers.  We have added a patch to the included weave
inline-compilation package that should fix the problem, currently
available only on the most recent CVS version of Topographica.
Affected users may need to do a <A target="_top"
href="../Downloads/cvs.html">CVS</A> update, then "make -C external
weave-uninstall ; make".  These changes will be included in the next
official release.
<br><br>

<p><b>23 July 2006:</b> Version 0.9.1
<A target="_top" href="../Downloads/index.html">released</A>.
This is a bugfix release only, upgrading the included Tcl/Tk package
to correct a syntax error in its configure script, which had
been preventing compilation on platforms using bash 3.1 (such as
Ubuntu 6.06).  There is no benefit to updating if 0.9.0 already runs
on your platform.
<br><br>

<p><b>07 June 2006:</b> Version 0.9.0
<A target="_top" href="../Downloads/index.html">released</A>, including 
numerous bugfixes, 
context-sensitive (balloon) help for nearly every parameter and control,
full Windows support (<A target="_top" href="../images/060607_topographica_win_screenshot.png">screenshot</A>),
full Mac OS X support,
downloadable installation files,
significant performance increases (7X faster on the main example scripts, with more
speedups to come),
faster startup,
better memory management,
simpler programming interface,
improved state saving (e.g. no longer requiring the original script),
independently controllable random number streams,
plot window histories,
more library components (e.g. Oja rule, CPCA, covariance),
<!-- plotting in Sheet coordinates, -->
<!-- better plot size handling, -->
<!-- command history buffer, -->
prototype spiking neuron support, and
much-improved <A target="_top" href="../User_Manual/modeleditor.html">model editor</A>.<BR><BR>

<p><b>15 May 2006:</b> New book <A target="_top"
HREF="http://computationalmaps.org"><i>Computational Maps in the
Visual Cortex</i></A> available, including background on modeling
computational maps, a review of visual cortex models, and <A
target="_top" HREF="http://computationalmaps.org/docs/chapter5.pdf">an
extended set of examples of the types of models supported by
Topographica</a>.
<br><br>

<p><b>20 February 2006:</b> Version 0.8.2 released, including numerous
bugfixes, 
circular receptive fields,
shared-weight projections,
<A TARGET="_top" href="../Tutorials/lissom_oo_or.html">tutorial with ON/OFF LGN model</A>,
<A TARGET="_top" href="../Tutorials/som_retinotopy.html">SOM retinotopy tutorial</A>,
Euclidean-distance-based response and learning functions,
density-independent SOM parameters,
<A TARGET="_top" href="../Downloads/cvs.html#osx">Mac OS X instructions</A>,
<A TARGET="_top" href="../Developer_Manual/index.html">developer manual</A>,
<A TARGET="_top" href="../User_Manual/index.html">partial user manual</A>,
much-improved 
<A target="_top" href="../images/060220_model_editor_screen_shot.png">model editor</A>,
<A TARGET="_top" href="../User_Manual/commandline.html#pylab">generic Matlab-style plotting</A>,
topographic grid plotting,
RGB plots,
user-controllable plot sorting,
plot color keys,
<!-- Normally distributed random PatternGenerator, -->
and progress reports during learning.  See the 
<A target="_top" href="../images/060220_topographica_screen_shot.png">Linux screenshot</A>.
<br><br>

<p><b>22 December 2005:</b> Version 0.8.1 released, including numerous
bugfixes, more flexible plotting (including weight colorization),
user-controllable optimization, properties panels, more-useful
<A TARGET="_top" href="../Reference_Manual/index.html">reference manual</A>,
image input patterns, and a prototype graphical
model editor.  <!-- Plus SOMs with selectable Projections -->
<br><br>

<p><b>8 November 2005:</b> New site launched with Topographica version
0.8.0, including a new
 <a target="_top" href="../Tutorials/lissom_or.html">LISSOM tutorial</a>.
(<a target="_top" href="../images/051107_topographica_screen_shot_white.png">Linux screenshot</a>).
