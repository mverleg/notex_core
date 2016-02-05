.. notex documentation master file, created by
   sphinx-quickstart on Fri Feb  5 12:20:59 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NoTeX documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2


Compiling
=================================

.. graphviz::

   digraph compile {
	  subgraph cluster_per_render {
		 label="per render"
		 graph[style=rounded,color=gray]
		 subgraph cluster_provisional {
			label="best-guess context"
			graph[style="rounded",color="gray"]
			"provisional arguments" [label="arguments"]
			"provisional pre-process" [label="pre-process"]
			"provisional parse" [label="parse"]
			"provisional modules" [label="modules"]
			"provisional settings" [label="settings"]
			subgraph cluster_include_provisional {
               label="includes"
               graph[style="rounded",color="gray"]
               "provisional pre-process" -> "provisional parse" -> "provisional includes"
               "provisional include A" [label="include A",peripheries=2,color=gray]
		       "provisional include B" [label="include B",peripheries=2,color=gray]
		       "provisional include A" -> "provisional include A" [arrowhead=crow]
		       "provisional include B" -> "provisional include B" [arrowhead=crow]
		       "provisional includes" -> "provisional include A" [arrowhead=crow]
		       "provisional includes" -> "provisional include B" [arrowhead=crow]
			}
			"provisional arguments" -> "provisional pre-process"
			"provisional parse" -> "provisional modules"
			"provisional parse" -> "provisional settings"
			"provisional out" [style=invis,height=0,label=""]
            "provisional includes" -> "provisional out" [dir=none]
			"provisional modules"  -> "provisional out" [dir=none]
			"provisional settings" -> "provisional out" [dir=none]
		 }
		 subgraph cluster_final {
			label="real context"
			graph[style="dotted,rounded",color=gray]
			"final arguments" [label="arguments"]
			"final pre-process" [label="pre-process"]
			"final parse" [label="parse"]
			"final modules" [label="modules"]
			"final settings" [label="settings"]
			"final arguments" -> "final pre-process" -> "final parse" -> "final modules"
			"final parse" -> "final settings"
			"final out" [style=invis,height=0,label=""]
			"final modules" -> "final out" [dir=none]
			"final settings" -> "final out" [dir=none]
		 }
		 "provisional out" -> "final arguments" [label="context changed"]
		 "provisional out" -> "find renders" [label="context unchanged"]
		 "final out" -> "find renders"
		 "render A" [peripheries=2,color=gray]
		 "render B" [peripheries=2,color=gray]
		 "find renders" -> "render A" [arrowhead=crow]
		 "find renders" -> "render B" [arrowhead=crow]
		 "render A" -> "render A" [arrowhead=crow]
		 "render B" -> "render B" [arrowhead=crow]
		 "find renders" -> "tags"
		 "find renders" -> "substitutions"
         "render out" [style=invis,height=0,label=""]
         "tags" -> "render out" [dir=none]
         "substitutions" -> "render out" [dir=none]
	  }
	  "render out" -> "link";
	  "link" -> "render" -> "post-process"
	  "initial arguments" [label="arguments"]
	  "initial arguments" -> "provisional arguments"
   }

Packages
=================================

arguments I
FOR document:
	pre-process I (defaults or cached)
	parse I (defaults or cached)
	get modules & settings
	arguments II
	IF pre-processing or parsing is different:
		  pre-process II (completely redo)
		  parse II (complete redo, ignore requirements)
	  include >>
	  tags
	  substitutions
linking
external files
rendering
post-process



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


