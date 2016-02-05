.. notex documentation master file, created by
   sphinx-quickstart on Fri Feb  5 12:20:59 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to notex's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2


Compiling
=================================

.. graphviz::

   digraph compile {
	  subgraph cluster_per_render {
		 label="per render";
		 graph[style=rounded,color=gray];
		 "document" [label="document"];
         subgraph cluster_per_include_2 {
		    label="second include";
			graph[style=rounded,color=gray];
			"second include" [label="same as other include"];
		 }
		 subgraph cluster_per_include_3 {
		    label="third include";
			graph[style=rounded,color=gray];
			"third include" [label="same as other include"];
		 }
         subgraph cluster_per_include_4 {
		    label="fourth include";
			graph[style=rounded,color=gray];
			"fourth include" [label="same as other include"];
		 }
		 subgraph cluster_per_include {
			label="first include";
			graph[style=rounded,color=gray];
			subgraph cluster_provisional {
               label="best-guess context";
               graph[style="rounded",color=gray];
               "provisional pre-process" [label="pre-process"];
               "provisional parse" [label="parse"];
               "provisional modules" [label="modules"];
               "provisional settings" [label="settings"];
               "provisional pre-process" -> "provisional parse" -> "provisional modules" -> "provisional settings";
			}
			"final arguments" [label="arguments"];
			subgraph cluster_final {
			   label="real context";
			   graph[style="dotted,rounded",color=gray];
               "final pre-process" [label="pre-process"];
               "final parse" [label="parse"];
               "final modules" [label="changed modules"];
               "final settings" [label="settings"];
               "final pre-process" -> "final parse" -> "final modules" -> "final settings";
			}
			"provisional settings" -> "final arguments" [label="context changed"];
			"provisional settings" -> "find includes" [label="context unchanged"];
			"final arguments" -> "final pre-process";
			"final settings" -> "find includes";
			"find includes" -> "third include";
			"find includes" -> "fourth include";
		 }
		 "initial arguments" [label="arguments"];
		 "initial arguments" -> "provisional pre-process";
		 "initial arguments" -> "second include";
		 "initial arguments" -> "third include";
		 "second include" -> "document";
		 "third include" -> "document";
	  }
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


