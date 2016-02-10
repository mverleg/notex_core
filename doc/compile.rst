
.. _compiler_documentation:

Compiling
=================================

The process
---------------------------------

.. graphviz::

	digraph compile {
		subgraph cluster_per_render {
		label="section (per render)"
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
				label="leaf (per include)"
				graph[style="rounded",color="gray"]
				"provisional pre-process" -> "provisional parse" -> "provisional includes"
				"provisional include A" [label="include A",peripheries=2,color=gray]
				"provisional include B" [label="include B",peripheries=2,color=gray]
				"provisional include A" -> "provisional include A" [arrowname=crow]
				"provisional include B" -> "provisional include B" [arrowname=crow]
				"provisional includes" -> "provisional include A" [arrowname=crow]
				"provisional includes" -> "provisional include B" [arrowname=crow]
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
			graph[style="rounded",color="gray"]
			"final arguments" [label="arguments"]
			"final pre-process" [label="pre-process"]
			"final parse" [label="parse"]
			"final modules" [label="modules"]
			"final settings" [label="settings"]
			subgraph cluster_include_final {
				label="includes"
				graph[style="rounded",color="gray"]
				"final pre-process" -> "final parse" -> "final includes"
				"final include A" [label="include A",peripheries=2,color=gray]
				"final include B" [label="include B",peripheries=2,color=gray]
				"final include A" -> "final include A" [arrowname=crow]
				"final include B" -> "final include B" [arrowname=crow]
				"final includes" -> "final include A" [arrowname=crow]
				"final includes" -> "final include B" [arrowname=crow]
			}
			"final arguments" -> "final pre-process"
			"final parse" -> "final modules"
			"final parse" -> "final settings"
			"final out" [style=invis,height=0,label=""]
			"final includes" -> "final out" [dir=none]
			"final modules"  -> "final out" [dir=none]
			"final settings" -> "final out" [dir=none]
		}
		"provisional out" -> "final arguments" [label="context changed"]
		"provisional out" -> "find renders" [label="context unchanged"]
		"final out" -> "find renders"
		"render A" [peripheries=2,color=gray]
		"render B" [peripheries=2,color=gray]
		"find renders" -> "render A" [arrowname=crow]
		"find renders" -> "render B" [arrowname=crow]
		"render A" -> "render A" [arrowname=crow]
		"render B" -> "render B" [arrowname=crow]
		"find renders" -> "tags"
		"tags" -> "substitutions"
		}
		"substitutions" -> "link";
			"link" -> "render" -> "post-process"
			"initial arguments" [label="arguments"]
			"initial arguments" -> "provisional arguments"
	}


