

import os
import typing

import jk_typing


from .INode import INode






class Node(INode):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, graph, nodeID:int, name:str):
		self._graph = graph
		self._nodeID = nodeID
		self._name = name
		self._incomingLinks = {}
		self._outgoingLinks = {}
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def name(self) -> str:
		return self._name
	#

	@property
	def nodeID(self) -> int:
		return self._nodeID
	#

	@property
	def isStartNode(self) -> bool:
		return len(self._incomingLinks) == 0
	#

	@property
	def isEndNode(self) -> bool:
		return len(self._outgoingLinks) == 0
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "Node<({}, {})>".format(self._nodeID, repr(self._name))
	#

	def __repr__(self):
		return "Node<({}, {})>".format(self._nodeID, repr(self._name))
	#

	def __hash__(self) -> int:
		return self._nodeID.__hash__()
	#

	def __eq__(self, other: object) -> bool:
		if isinstance(other, Node):
			return other._nodeID == self._nodeID
		else:
			return False
	#

#







