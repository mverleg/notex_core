
.. _compiler_documentation:

Compiling
=================================

The process
---------------------------------

.. graphviz::

	digraph compile {
		subgraph cluster_per_section {
            label="section (per render)"
            graph[style=rounded,color=gray]
            subgraph cluster_in_context {
                label="context-dependent"
                graph[style="rounded",color="gray"]
                "arguments" [label="arguments"]
                "pre-process" [label="pre-process"]
                "parse" [label="parse"]
                "packages" [label="packages"]
                "settings" [label="settings"]
                subgraph cluster_include_final {
                    label="leaf (per include)"
                    graph[style="rounded",color="gray"]
                    "pre-process" -> "parse" -> "includes"
                    "include A" [label="include A",peripheries=2,color=gray]
                    "include B" [label="include B",peripheries=2,color=gray]
                    "include A" -> "include A" [arrowname=crow]
                    "include B" -> "include B" [arrowname=crow]
                    "includes" -> "include A" [arrowname=crow]
                    "includes" -> "include B" [arrowname=crow]
                }
                "arguments" -> "pre-process"
                "parse" -> "packages"
                "parse" -> "settings"
                "hidden-joint" [style=invis,height=0,label=""]
                "includes" -> "hidden-joint" [dir=none]
                "packages"  -> "hidden-joint" [dir=none]
                "settings" -> "hidden-joint" [dir=none]
            }
            "repeat" [shape=rounded,label="repeat if configuration changed"]
            "hidden-joint" -> "repeat"
            "repeat" -> "arguments"
            "hidden-joint" -> "find sections"
            "section A" [peripheries=2,color=gray]
            "section B" [peripheries=2,color=gray]
            "find sections" -> "section A" [arrowname=crow]
            "find sections" -> "section B" [arrowname=crow]
            "section A" -> "section A" [arrowname=crow]
            "section B" -> "section B" [arrowname=crow]
            "find sections" -> "tags"
            "tags" -> "compile"
            "compile" -> "substitutions"
            "render" -> "post-process"
		}
		"merge"
		"link"
		"result" [peripheries=2,shape=rounded]
		"substitutions" -> "merge" -> "link" -> "render"
		"post-process" -> "result"
        "standard arguments" -> "guess context" -> "arguments"
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


