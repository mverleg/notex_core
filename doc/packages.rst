
Packages
=================================

Package index layout
---------------------------------

Multiple versions of a package can be installed on a system at one time (like virtualenv, but implicit).
Packages are collected in an online index. They can, if the author wishes, be reviewed by auditors from the community based on being functional, safe, and having an acceptable license.
Unsafe packages are removed but other rejected, pending or non-reviewed packages can still be installed if a special flag is provided.
Static files used by packages can also be served directly from the index, e.g. to reduce output size.

.. graphviz::

	digraph compile {
		graph[rankdir=LR]
		subgraph cluster_developer {
			label="developer"
			graph[style=rounded,color=gray]
			"dev package alpha" [label="package alpha",group="package group"]
			"dev v1.0.0" [label="v1.0.0"]
			"dev v1.1.0dev" [label="v1.1.0dev"]
			"dev v1.2.2" [label="v1.2.2"]
			"dev v1.3.live" [label="v1.3.live"]
			{"dev v1.0.0" "dev v1.1.0dev" "dev v1.2.2" "dev v1.3.live" "dev v1.4.37"} -> "dev package alpha" [dir=none]
		}
		subgraph cluster_PI {
			label="package index"
			graph[style=rounded,color=gray]
			"PI package alpha" [label="package alpha",group="package group"]
			"PI v1.0.0" [label="v1.0.0",peripheries=2]
			"PI v1.2.2" [label="v1.2.2"]
			"PI v1.3.live" [label="v1.3.live",peripheries=2]
			"PI v1.4.37" [label="v1.4.37"]
			{"PI v1.0.0" "PI v1.2.2" "PI v1.3.live" "PI v1.4.37"} -> "PI package alpha" [dir=none]
			subgraph cluster_auditors {
				label="auditors"
				graph[style=rounded,color=gray]
				"auditor 1" [label="auditor"]
				"auditor 2" [label="auditor"]
				"auditor 3" [label="auditor"]
				"auditors" [style=invis,height=0,label=""]
				{"auditor 1" "auditor 2" "auditor 3"} -> "auditors" [dir=none]
			}
			"auditors" -> "PI v1.0.0" [label="approved",arrowname=diamond]
			"auditors" -> "PI v1.2.2" [label="not approved",arrowname=box]
			"auditors" -> "PI v1.3.live" [label="approved",arrowname=diamond]
			"auditors" -> "PI v1.4.37" [label="pending",arrowname=none,style=dashed]
		}
		subgraph cluster_user {
			label="package manager"
			graph[style=rounded,color=gray]
			"user package alpha" [label="package alpha",group="package group"]
			"user v1.2.2" [label="v1.2.2"]
			"user v1.3.live" [label="v1.3.live",peripheries=2]
			"user v1.4.37" [label="v1.4.37"]
			{"user v1.2.2" "user v1.3.live" "user v1.4.37"} -> "user package alpha" [dir=none]
		}
		subgraph cluster_doc1 {
			label="document"
			graph[style=rounded,color=gray]
			"document I" [shape=box]
			"req1" [label="alpha==<1.4",shape=invhouse]
			"document I" -> "req1"
		}
		subgraph cluster_doc2 {
			label="document"
			graph[style=rounded,color=gray]
			"document II" [shape=box]
			"req2" [label="alpha==*",shape=invhouse]
			"document II" -> "req2"
		}
		subgraph cluster_doc3 {
			label="document"
			graph[style=rounded,color=gray,style=dashed]
			"deleted document" [shape=box,style=dashed]
			"req3" [label="alpha==1.2.2",shape=invhouse,style=dashed]
			"deleted document" -> "req3" [style=dashed]
		}
		"req1" -> "user v1.3.live"
		"req2" -> "user v1.4.37"
		"req2" -> "user v1.2.2" [label="previously",style=dashed]
		"req3" -> "user v1.2.2" [label="previously",style=dashed]

		"dev v1.0.0" -> "PI v1.0.0" [label="calc sig"]
		"dev v1.2.2" -> "PI v1.2.2" [label="calc sig"]
		"dev v1.3.live" -> "PI v1.3.live" [label="calc sig"]
		"dev v1.4.37" -> "PI v1.4.37" [label="verify sig"]
		"user v1.2.2" -> "PI v1.2.2" [label="verify sig"]
		"user v1.3.live" -> "PI v1.3.live" [label="verify sig"]
		"user v1.4.37" -> "PI v1.4.37" [label="verify sig"]
	}

Configuration example
---------------------------------

Configuration files should be valid json, but can contain comments (`#` or `//`) and dictionaries are ordered (they are read with json_tricks_ in no-numpy mode).
The structure is like this ("name", "version" and "license" are required, and you should provide at least one functional setting):

.. literalinclude:: ../../notexp/demo/config.json

Refer to the :ref:`compiler_documentation` to see what each part does.
For `package versions`_, not that the first two should be numbers that are used for filtering (e.g. ``<=2.3``).

To submit for approval, choose one of ``"Apache 2.0"``, ``"BSD 2-clause"``, ``"ISC"``, ``"MIT"`` or ``"Unlicense"``.
The first four are similar: if the license is kept they allow modification and commercial use without warranty. Unlicense is similar but also completely relinquishes your copyright.


.. _json_tricks: http://json-tricks.readthedocs.org/en/latest/
.. _package versions: https://github.com/mverleg/package_versions
.. _info about licenses: http://choosealicense.com/licenses/

