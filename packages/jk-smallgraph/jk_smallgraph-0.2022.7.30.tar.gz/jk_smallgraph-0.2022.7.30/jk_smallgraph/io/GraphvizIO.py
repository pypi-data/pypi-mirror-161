

import os
import typing

import graphviz


from ..DirectedGraph import DirectedGraph
from ..ILink import ILink
from ..INode import INode






class GraphvizIO(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	@staticmethod
	def convert(g:DirectedGraph, title:str) -> graphviz.Digraph:
		dot = graphviz.Digraph(name=title, graph_attr={ "rankdir": "LR" })

		for node in g.iterateAllNodes():
			dot.node(
				name="n" + str(node.nodeID),
				label=node.name,
				fillcolor=getattr(node, "color", None),
				style="filled",
			)

		for link in g.iterateAllLinks():
			dot.edge(
				tail_name="n" + str(link.fromNode.nodeID),
				head_name="n" + str(link.toNode.nodeID),
			)

		return dot
	#

#







