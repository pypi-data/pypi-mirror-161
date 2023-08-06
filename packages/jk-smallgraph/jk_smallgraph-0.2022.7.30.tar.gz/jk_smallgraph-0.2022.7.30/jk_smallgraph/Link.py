

import os
import typing

import jk_typing


from .INode import INode
from .ILink import ILink






class Link(ILink):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, graph, linkID:int, fromNode:INode, toNode:INode):
		self._graph = graph
		self._linkID = linkID
		self._fromNode = fromNode
		self._toNode = toNode
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def linkID(self) -> int:
		return self._linkID
	#

	@property
	def fromNode(self) -> INode:
		return self._fromNode
	#

	@property
	def toNode(self) -> INode:
		return self._toNode
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "Link<({}, {}->{})>".format(self._linkID, repr(self._fromNode._name), repr(self._toNode._name))
	#

	def __repr__(self):
		return "Link<({}, {}->{})>".format(self._linkID, repr(self._fromNode._name), repr(self._toNode._name))
	#

	def __hash__(self) -> int:
		return self._linkID.__hash__()
	#

#







