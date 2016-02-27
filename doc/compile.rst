
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
                "provisional compile" [label="compile"]
                "provisional includes" -> "provisional compile" [dir=none]
                "provisional modules"  -> "provisional compile" [dir=none]
                "provisional settings" -> "provisional compile" [dir=none]
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
                "final compile" [label="compile"]
                "final includes" -> "final compile" [dir=none]
                "final modules"  -> "final compile" [dir=none]
                "final settings" -> "final compile" [dir=none]
            }
            "provisional compile" -> "final arguments" [label="context changed"]
            "provisional compile" -> "find renders" [label="context unchanged"]
            "final compile" -> "find renders"
            "render A" [peripheries=2,color=gray]
            "render B" [peripheries=2,color=gray]
            "find renders" -> "render A" [arrowname=crow]
            "find renders" -> "render B" [arrowname=crow]
            "render A" -> "render A" [arrowname=crow]
            "render B" -> "render B" [arrowname=crow]
            "find renders" -> "tags"
            "tags" -> "substitutions"
            "render" -> "post-process"
		}
		"merge"
		"link"
		"result" [peripheries=2,shape=rounded]
		"substitutions" -> "merge" -> "link" -> "render"
		"post-process" -> "result"
        "initial arguments" [label="arguments"]
        "initial arguments" -> "provisional arguments"
	}

Settings
---------------------------------

There are three groups of settings, each with different sources

* Document

	1. Document defaults
	2. Packages
	3. In-document ``<config>``

	For example (some depend on the output format):

	* line distance
	* margins
	* which numerals
	* where are refs
	* encoding (if changable)
	* is draft warning
	* footer
	* header
	* title (<title>)
	* meta info

* Compiler

	1. Defaults
	2. Configuration files
	3. Packages (argparse)
	4. In-document ``<compileconfig>``
	5. Command-line arguments

	For example:

	* output format
	* single file
	* use external
	* strip comments
	* minified
	* file loader
	* cache (which, on/off)
	* strict mode
	* verbosity
	* signature

* Package manager

	1. Defaults
	2. Configuration files
	3. Command-line arguments

	For example:

	* where to install
	* trust which sources
	* strict mode
	* verbosity


