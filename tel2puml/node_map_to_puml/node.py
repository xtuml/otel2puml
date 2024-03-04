"This module holds the 'node' class"


class Node:
    """
    Represents a node in a graph.

    Attributes:
        data: The data stored in the node.
        incoming: List of incoming nodes.
        outgoing: List of outgoing nodes.
        incoming_logic: List of incoming logic.
        outgoing_logic: List of outgoing logic.
        branch_enum: List of branch enumeration values.
    """

    def __init__(
        self,
        data,
        incoming=None,
        outgoing=None,
        incoming_logic=None,
        outgoing_logic=None,
    ):
        self.data = data
        self.incoming = [] if incoming is None else incoming
        self.outgoing = [] if outgoing is None else outgoing
        self.incoming_logic = [] if incoming_logic is None else incoming_logic
        self.outgoing_logic = [] if outgoing_logic is None else outgoing_logic

        self.branch_enum = ["AND", "OR", "XOR", "LOOP"]
