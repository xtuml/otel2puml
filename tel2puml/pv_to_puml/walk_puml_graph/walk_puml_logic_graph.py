"""This module holds the 'LogicBlockHolder' class"""

from collections import Counter
from itertools import chain

from networkx import DiGraph, topological_sort, has_path, all_simple_paths

from tel2puml.puml_graph import (
    PUMLEventNode,
    PUMLGraph,
    PUMLOperatorNode,
    PUMLNode,
)
from tel2puml.pv_to_puml.walk_puml_graph.node import Node, get_node_as_list, SubGraphNode
from tel2puml.tel2puml_types import PUMLEvent
from tel2puml.events import has_event_set_as_subset, get_reduced_event_set


class LogicBlockHolder:
    """Holds a logic block that keeps track of the logic blocks.

    :param start_node: The start node of the logic block.
    :type start_node: :class:`PUMLOperatorNode`
    :param end_node: The end node of the logic block.
    :type end_node: :class:`PUMLOperatorNode`
    :param logic_node: The logic node of the logic block.
    :type logic_node: :class:`Node`
    """

    def __init__(
        self,
        start_node: PUMLOperatorNode,
        end_node: PUMLOperatorNode,
        logic_node: Node,
    ) -> None:
        """Constructor method."""
        self.start_node = start_node
        self.end_node = end_node
        self.logic_node = logic_node
        self.paths = logic_node.outgoing_logic.copy()
        self._path_indexes = list(range(len(self.paths)))
        self._merged_path_indexes: list[int] = []
        self.merge_nodes: list[None | Node] = [None] * len(self.paths)
        self.puml_nodes: list[PUMLNode] = [start_node] * len(self.paths)
        self.will_merge = False
        self.merge_counter = 0
        if logic_node.lonely_merge:
            self.lonely_merge_index: int | None = self.paths.index(
                logic_node.lonely_merge
            )
        else:
            self.lonely_merge_index = None
        self.loop_kill_paths = logic_node.is_loop_kill_path.copy()
        self.impossible_and_or_merges = [False] * len(self.paths)

    @property
    def paths_non_loop_kill(self) -> list[Node]:
        """Gets the non loop kill paths.

        :return: The non loop kill paths.
        :rtype: `list`[`bool`]
        """
        return [
            path
            for path, is_loop_kill_path in zip(
                self.paths, self.loop_kill_paths
            )
            if not is_loop_kill_path
        ]

    @property
    def paths_loop_kill(self) -> list[Node]:
        """Gets the loop kill paths.

        :return: The loop kill paths.
        :rtype: `list`[`bool`]
        """
        return [
            path
            for path, is_loop_kill_path in zip(
                self.paths, self.loop_kill_paths
            )
            if is_loop_kill_path
        ]

    @property
    def current_path(self) -> Node | None:
        """Gets the current path."""
        if self.paths:
            return self.paths[-1]
        return None

    @current_path.setter
    def current_path(self, value: Node) -> None:
        """Sets the current path."""
        if self.paths:
            self.paths[-1] = value
        else:
            raise ValueError("No paths to set")

    @property
    def current_path_puml_node(self) -> PUMLNode:
        """Gets the current path PlantUML node.

        :return: The current path PlantUML node.
        :rtype: :class:`PUMLNode`
        """
        return self.puml_nodes[-1]

    @current_path_puml_node.setter
    def current_path_puml_node(self, value: PUMLNode) -> None:
        """Sets the current path PlantUML node.

        :param value: The value to set.
        :type value: :class:`PUMLNode`
        """
        self.puml_nodes[-1] = value

    def set_path_node(self, pop: bool = False) -> Node | None:
        """Gets the next path in the block and returns it

        :return: The path node.
        :rtype: :class:`Node` | `None`
        """
        if self.paths and pop:
            self.paths.pop()
            self.merge_nodes.pop()
            self.puml_nodes.pop()
            self.loop_kill_paths.pop()
            self._merged_path_indexes.append(self._path_indexes.pop())
        return self.current_path

    def rotate_path(
        self, current_node_in_path: Node, current_puml_node_in_path: PUMLNode
    ) -> tuple[PUMLNode, Node]:
        """Rotates the path by moving the current path to the end of the paths
        list.

        :return: The path node.
        :rtype: :class:`Node` | `None`
        """
        self.paths = [current_node_in_path] + self.paths[:-1]
        self.merge_nodes = [self.merge_nodes[-1]] + self.merge_nodes[:-1]
        self.loop_kill_paths = [
            self.loop_kill_paths[-1]
        ] + self.loop_kill_paths[:-1]
        self.impossible_and_or_merges = [
            self.impossible_and_or_merges[-1]
        ] + self.impossible_and_or_merges[:-1]
        self._path_indexes = [self._path_indexes[-1]] + self._path_indexes[:-1]
        self.puml_nodes = [current_puml_node_in_path] + self.puml_nodes[:-1]
        if self.lonely_merge_index is not None:
            self.lonely_merge_index = (self.lonely_merge_index + 1) % len(
                self.paths
            )
        if self.current_path is None:
            raise ValueError("No current path after rotation")
        return (
            self.current_path_puml_node,
            self.current_path,
        )

    def handle_path_merge(self, potential_merge_node: Node) -> bool:
        """Handles a potential merge node. Checks if all paths have the same
        merge node and if they do then the merge is successful.

        Also increments the merge counter if the merge node is the same as the
        previous merge node, otherwise resets the merge counter.

        :param potential_merge_node: The potential merge node.
        :type potential_merge_node: :class:`Node`
        :return: Whether the merge was successful.
        :rtype: `bool`
        """
        if self.will_merge and not self.loop_kill_paths[-1]:
            return True
        if self.current_path is None:
            raise ValueError("No current path to merge")
        # increment the merge counter if nothing has changed
        if self.merge_nodes[-1] == potential_merge_node:
            self.merge_counter += 1
        else:
            self.merge_counter = 0
        self.merge_nodes[-1] = potential_merge_node
        if self.loop_kill_paths[-1]:
            self._check_merge_is_correct(potential_merge_node)
            return False
        elif any(self.loop_kill_paths):
            return False
        else:
            # set previous merge nodes to the current merge nodes
            if len(set(self.merge_nodes)) == 1:
                # check if for AND or OR logic merges that the merge node is
                # correct to merge on
                self.will_merge = self._check_merge_is_correct(
                    potential_merge_node
                )
                return self.will_merge
        return False

    def _check_merge_is_correct(self, potential_merge_node: Node) -> bool:
        """Checks if the merge is correct for AND or OR logic nodes. This is
        performed by checking that if the logic block is an AND/OR block that
        the merge node contains the event set of all the evnet types of the
        nodes in the logic block paths at their current state
        Automatically ok for XOR

        :return: Whether the merge is correct.
        :rtype: `bool`
        """
        if self.logic_node.operator not in ["AND", "OR"]:
            return True

        # check first that the merge node contains the event set of all the
        # event types of the nodes in the logic block paths (
        # potential AND merges of same event type)
        paths_event_types = [
            node.event_type
            for node, merge_node in zip(self.paths, self.merge_nodes)
            if merge_node == potential_merge_node
        ]
        if None in paths_event_types:
            contains_event_set = False
        else:
            contains_event_set = has_event_set_as_subset(
                potential_merge_node.eventsets_incoming, [
                    event_type
                    for event_type in paths_event_types
                    if event_type is not None
                ]
            )
        if not contains_event_set:
            # check whether the merge node is a merge count and if so check if
            # at least the frozen event sets are the same
            if PUMLEvent.MERGE in potential_merge_node.get_puml_event_types():
                if frozenset(paths_event_types) in get_reduced_event_set(
                    potential_merge_node.eventsets_incoming
                ):
                    return True
            for index, merge_node in enumerate(self.merge_nodes):
                if merge_node == potential_merge_node:
                    self.impossible_and_or_merges[index] = True
            return False
        return True

    def create_logic_merge(
        self, puml_graph: PUMLGraph, merge_node: Node
    ) -> set[PUMLNode]:
        """Creates a logic merge for a given merge node.

        :param puml_graph: The PlantUML graph.
        :type puml_graph: :class:`PUMLGraph`
        :param merge_node: The merge node.
        :type merge_node: :class:`Node`
        :return: The nodes to remove.
        :rtype: `set`[:class:`PUMLNode`]
        """
        # whilst there are still loop kill paths still check if the merge node
        # is for all of the non loop kill paths, if so do nothing and return
        if not self.loop_kill_paths[
            self.merge_nodes.index(merge_node)
        ] and any(self.loop_kill_paths):
            return set()
        indices = [
            i for i, x in enumerate(self.merge_nodes) if x == merge_node
        ]
        not_indices = [
            i for i, x in enumerate(self.merge_nodes) if x != merge_node
        ]
        if len(indices) < 2:
            return set()

        nodes_to_remove = set()
        for puml_node in [self.puml_nodes[index] for index in indices]:
            paths = all_simple_paths(
                puml_graph,
                self.start_node,
                puml_node,
            )
            for path in paths:
                for path_node in path[1:]:
                    nodes_to_remove.add(path_node)

        new_node = Node(
            operator=self.logic_node.operator,
            outgoing_logic=self.logic_node.get_outgoing_logic_by_indices(
                [self._path_indexes[index] for index in indices]
            ),
        )
        # make sure the new node created has no kill paths
        new_node.is_loop_kill_path = [False] * len(indices)

        self.merge_nodes = [
            self.merge_nodes[index] for index in not_indices
        ] + [None]
        self.puml_nodes = [self.puml_nodes[index] for index in not_indices] + [
            self.start_node
        ]
        self.paths = [self.paths[index] for index in not_indices] + [new_node]
        self.loop_kill_paths = [
            self.loop_kill_paths[index] for index in not_indices
        ] + [all(self.loop_kill_paths[index] for index in indices)]
        self.logic_node.set_outgoing_logic(
            self.logic_node.get_outgoing_logic_by_indices(
                [self._path_indexes[index] for index in not_indices]
                + self._merged_path_indexes
            )
            + [new_node]
        )
        self.logic_node.is_loop_kill_path = self.loop_kill_paths.copy()
        # make sure all indexes that mirror the logic node indexes are updated
        # correctly
        not_indices_len = len(not_indices)
        merged_paths_indices_len = len(self._merged_path_indexes)
        self._path_indexes = list(range(not_indices_len))
        self._merged_path_indexes = list(
            range(not_indices_len, not_indices_len + merged_paths_indices_len)
        )
        self._path_indexes += [not_indices_len + merged_paths_indices_len]
        return nodes_to_remove

    def is_on_lonely_merge_path(self) -> bool:
        """Checks if the current path is on the lonely merge path.

        :return: Whether the current path is on the lonely merge path.
        :rtype: `bool`
        """
        if self.lonely_merge_index is not None:
            return self.lonely_merge_index == len(self.paths) - 1
        return False


def create_puml_graph_from_node_class_graph(
    node_class_graph: "DiGraph[Node]",
) -> PUMLGraph:
    """Creates a PlantUML graph from a node class graph using the logic
    held on each node and the connections between the nodes.

    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`[:class:`Node`]
    :return: The PlantUML graph.
    :rtype: :class:`PUMLGraph`
    """
    head_node: Node = list(topological_sort(node_class_graph))[0]
    puml_graph = PUMLGraph()
    if head_node.event_type is None:
        raise ValueError(
            "Head node of node graph must have an event type when creating a"
            " PUMLGraph"
        )
    previous_puml_node: PUMLNode = puml_graph.create_event_node(
        head_node.event_type,
        head_node.get_puml_event_types(),
        parent_graph_node=head_node.uid,
    )
    previous_node_class: Node = head_node
    logic_list: list[LogicBlockHolder] = []
    while True:
        # handle case in which the previous node is an event node that is
        # either a sequence or ends a sequence
        if (
            not previous_node_class.outgoing_logic
            and previous_node_class.event_type is not None
        ):
            # get the next node in the sequence if it exists
            if not previous_node_class.outgoing:
                next_node_class = None
            else:
                next_node_class = previous_node_class.outgoing[0]
            # break the loop if all logic blocks have been traversed and there
            # is no following node either
            if not logic_list and next_node_class is None:
                break
            if logic_list:
                # create a kill node if the next node is None and we are
                # within a logic block and then handle the merge point and
                # continue
                if next_node_class is None:
                    # handle the case where the previous node was a break
                    # point node
                    if (
                        PUMLEvent.BREAK
                        in previous_node_class.get_puml_event_types()
                    ):
                        kill_node: PUMLNode = previous_puml_node
                    else:
                        kill_node = puml_graph.create_kill_node()
                        puml_graph.add_puml_edge(previous_puml_node, kill_node)
                    previous_puml_node, previous_node_class = (
                        handle_reach_logic_merge_point(
                            puml_graph,
                            logic_list,
                            kill_node,
                            previous_node_class,
                        )
                    )
                    continue
                # check if the next node has an alternative path back to the
                # logic node and then handle a merge into the end of the logic
                # block and continue
                elif check_is_merge_node_for_logic_block(
                    next_node_class, logic_list[-1], node_class_graph
                ):
                    previous_puml_node, previous_node_class = (
                        handle_reach_potential_merge_point(
                            puml_graph,
                            logic_list,
                            previous_puml_node,
                            previous_node_class,
                            next_node_class,
                        )
                    )
                    continue
                else:
                    pass
            # handle the next node if it there is just a straight line sequence
            if next_node_class is None:
                raise ValueError(
                    "Next node class is None and therefore algorithm is not"
                    " performing as expected"
                )
            previous_puml_node, previous_node_class = (
                update_puml_graph_with_event_node(
                    puml_graph, next_node_class, previous_puml_node
                )
            )
        else:
            # handle the case where we have an operator node coming from an
            # event node that is part of a logic block where all other paths
            # do not join back up with the rest of the graph (i.e. a lonely
            # merge path that can be merged at any desired point)
            if logic_list:
                if logic_list[-1].is_on_lonely_merge_path():
                    previous_puml_node, previous_node_class = (
                        handle_reach_potential_merge_point(
                            puml_graph,
                            logic_list,
                            previous_puml_node,
                            previous_node_class,
                            previous_node_class.outgoing_logic[0],
                        )
                    )
                    continue
            # handle the case where there is an immediately following logic
            # node or a logic node as the previous node class
            previous_puml_node, previous_node_class = handle_logic_node_cases(
                puml_graph, logic_list, previous_puml_node, previous_node_class
            )
    return puml_graph


def handle_logic_node_cases(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
) -> tuple[PUMLNode, Node]:
    """Handles the cases where there is an immediately following logic node or
    a logic node as the previous node class.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLNode`, :class:`Node`]
    """
    # sets the logic node to the previous node class if it is a logic node or
    # the first node in the logic list if it is not
    if previous_node_class.operator is None:
        logic_node = previous_node_class.outgoing_logic[0]
    else:
        logic_node = previous_node_class
    # create the PUMLOperator node pairs and add them to the graph
    start_operator, end_operator = puml_graph.create_operator_node_pair(
        logic_node.get_operator_type()
    )
    # create and add the logic block holder to the logic list
    new_block = LogicBlockHolder(start_operator, end_operator, logic_node)
    logic_list.append(new_block)
    # add the edge between the previous PUMLNode and the start node
    # of the PUMLOperatorNode pair
    puml_graph.add_puml_edge(previous_puml_node, start_operator)
    # handle the next path in the logic list and return updated previous puml
    # node and node class
    return handle_logic_list_next_path(
        puml_graph, logic_list, previous_node_class
    )


def handle_reach_potential_merge_point(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
    next_node_class: Node,
) -> tuple[PUMLNode, Node]:
    """Handles reaching a potential merge point in the logic block.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_block: The logic block to handle.
    :type logic_block: :class:`LogicBlock
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :param next_node_class: The next node class.
    :type next_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLNode`, :class:`Node`]
    """
    logic_block = logic_list[-1]
    if logic_block.handle_path_merge(next_node_class):
        previous_puml_node, previous_node_class = (
            handle_reach_logic_merge_point(
                puml_graph, logic_list, previous_puml_node, previous_node_class
            )
        )
    else:
        # check if we are caught in an infinite loop when there are multiple
        # merge nodes
        if logic_block.merge_counter > len(logic_block.merge_nodes):
            logic_block.merge_counter = 0
            # handle case of impossible and/or merge
            if logic_block.impossible_and_or_merges[-1]:
                for index, merge_node in enumerate(logic_block.merge_nodes):
                    if merge_node == next_node_class:
                        logic_block.impossible_and_or_merges[index] = False
                # loop over all paths in the logic block and advance the path
                for i in range(len(logic_block.paths)):
                    if logic_block.merge_nodes[i] == next_node_class:
                        new_puml_node, _ = update_puml_graph_with_event_node(
                            puml_graph,
                            next_node_class,
                            logic_block.puml_nodes[i],
                        )
                        logic_block.puml_nodes[i] = new_puml_node
                        logic_block.paths[i] = next_node_class
                if logic_block.current_path is None:
                    raise ValueError("No current path after impossible merge")
                return (
                    logic_block.current_path_puml_node,
                    logic_block.current_path,
                )
            # make sure there are no more impossible merge cases lurking around
            if any(logic_block.impossible_and_or_merges):
                return logic_block.rotate_path(
                    previous_node_class, previous_puml_node
                )

            nodes_to_remove = set()
            counter = Counter(logic_block.merge_nodes)
            for merge_node, count in counter.most_common():
                if count < 2:
                    break
                if merge_node is None:
                    raise ValueError("Merge node is None")
                nodes_to_remove.update(
                    logic_block.create_logic_merge(puml_graph, merge_node)
                )

            puml_graph.remove_nodes_from(nodes_to_remove)

            return handle_logic_list_next_path(
                puml_graph=puml_graph,
                logic_list=logic_list,
                previous_node_class=logic_block.logic_node,
            )

        previous_puml_node, previous_node_class = handle_rotate_path(
            puml_graph, logic_list, previous_puml_node, previous_node_class
        )
    return previous_puml_node, previous_node_class


def handle_rotate_path(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
) -> tuple[PUMLNode, Node]:
    """Handles rotating the path in the logic block. This switched to another
    path of the logic block and updates the previous puml node and node class
    to the new path that was saved in the logic block.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_block: The logic block to handle.
    :type logic_block: :class:`LogicBlock
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLNode`, :class:`Node`]
    """
    previous_puml_node, previous_node_class = logic_list[-1].rotate_path(
        previous_node_class, previous_puml_node
    )
    # if the next path is the start of a path then we must handle the start of
    # next path to ensure the start node is connected to the first node in the
    # path
    if previous_puml_node == logic_list[-1].start_node:
        previous_puml_node, previous_node_class = handle_logic_list_next_path(
            puml_graph, logic_list, previous_node_class
        )
        logic_list[-1].current_path_puml_node = previous_puml_node
    return previous_puml_node, previous_node_class


def handle_reach_logic_merge_point(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
) -> tuple[PUMLNode, Node]:
    """Handles reaching a merge point in the logic block. Adds an edge between
    the previous node and the end node of the logic block and then grabs the
    next node from the logic list having removed the path that has just ended.

    After the above handles gettting the previous puml node and previous node
    class from the next path in the logic list. Check to see if a logic block
    has ended.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLNode`, :class:`Node`]
    """
    # when there is a merge point we must add an edge from the previous node
    # to the end node of the logic block
    puml_graph.add_puml_edge(
        previous_puml_node,
        logic_list[-1].end_node,
    )
    # handle the next path in the logic list and return updated previous puml
    # node and node class
    next_node_class = logic_list[-1].set_path_node(pop=True)
    # if there is no next path node then we must handle the end of the logic
    # block and return the updated previous puml node as the end node of the
    # logic block
    if next_node_class is None:
        previous_puml_node = logic_list.pop().end_node
    # if the next path node is a start node then we must handle the start of
    # the next path
    elif logic_list[-1].current_path_puml_node == logic_list[-1].start_node:
        previous_puml_node, previous_node_class = handle_logic_list_next_path(
            puml_graph, logic_list, previous_node_class
        )
        logic_list[-1].current_path_puml_node = previous_puml_node
    # Otherwise we grab the last puml node in the logic block and
    # set it as the previous puml node and the next node class as the previous
    # node class
    else:
        previous_puml_node = logic_list[-1].current_path_puml_node
        previous_node_class = next_node_class
    return previous_puml_node, previous_node_class


def handle_logic_list_next_path(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_node_class: Node,
) -> tuple[PUMLNode, Node]:
    """Handles the next path in the logic list.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLNode`, :class:`Node`]
    """
    # get the next path node in the logic block using the logic block holder
    next_node_class = logic_list[-1].set_path_node()
    # if there is no next path node then we must handle the end of the logic
    # block and return the updated previous puml node as the end node of the
    # logic block
    if next_node_class is None:
        previous_puml_node: PUMLNode = logic_list.pop().end_node
    # the next blocks handle the case where there is a next path node
    # if the next node is an operator node then we must make the it the next
    # node class and reset the previous puml node to the start of the logic
    # block
    elif next_node_class.operator is not None:
        previous_node_class = next_node_class
        previous_puml_node = logic_list[-1].start_node
    # if the next node is an event node then we must create a PUML node for it
    # and create an edge between this node and the start PUML node of the logic
    # block. Then we must update the previous puml node to the newly created
    # node and the previous node class to the event node
    else:
        previous_puml_node, previous_node_class = (
            update_puml_graph_with_event_node(
                puml_graph, next_node_class, logic_list[-1].start_node
            )
        )
    return previous_puml_node, previous_node_class


def update_puml_graph_with_event_node(
    puml_graph: PUMLGraph,
    event_node: Node,
    previous_puml_node: PUMLNode,
) -> tuple[PUMLEventNode, Node]:
    """Updates the PlantUML graph with an event node connecting the previous
    PlantUML node to a newly created node and then returns the newly created
    node and the event node which will be set as the previous in the next
    iteration

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param event_node: The event node to add.
    :type event_node: :class:`Node`
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLEventNode`, :class:`Node`]
    """
    if event_node.event_type is None:
        raise ValueError(
            f"Node event type is not set for node with uid {event_node.uid}"
        )
    next_puml_node = puml_graph.create_event_node(
        event_node.event_type,
        event_node.get_puml_event_types(),
        parent_graph_node=event_node.uid,
    )
    puml_graph.add_puml_edge(previous_puml_node, next_puml_node)
    return next_puml_node, event_node


def check_is_merge_node_for_logic_block(
    node: Node,
    logic_block_holder: LogicBlockHolder,
    node_class_graph: "DiGraph[Node]",
) -> bool:
    """Checks if a node has a different path to the logic node other than the
    current path of the logic block. Subsequently checks that
    the penultimate node in the paths, i.e. the node immediately previous to
    the node to check, has out going logic or not and therefore can or cannot
    be, respectively, a merge point of the current path.

    :param node: The node to check.
    :type node: :class:`Node`
    :param logic_block_holder: The logic block holder.
    :type logic_block_holder: :class:`LogicBlockHolder`
    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`[:class:`Node`]
    :return: `True` if the node has a different path to the logic node other
    than the current path of the logic block, `False` otherwise.
    :rtype: `bool`
    """
    if logic_block_holder.lonely_merge_index is not None:
        if (
            logic_block_holder.lonely_merge_index
            == len(logic_block_holder.paths) - 1
        ):
            if node != logic_block_holder.logic_node.lonely_merge:
                return True
        return False
    # check if the logic block should merge and the current path is not a loop
    # kill path
    if (
        logic_block_holder.will_merge
        and not logic_block_holder.loop_kill_paths[-1]
    ):
        return True
    # check if we are mergin kill paths or not and then check the merge node
    # is correct
    if logic_block_holder.loop_kill_paths[-1]:
        return check_has_valid_merge(
            node, logic_block_holder.paths_loop_kill[:-1], node_class_graph
        )
    else:
        return check_has_valid_merge(
            node, logic_block_holder.paths_non_loop_kill[:-1], node_class_graph
        )


def check_has_valid_merge(
    node: Node,
    paths_to_check: list[Node],
    node_class_graph: "DiGraph[Node]",
) -> bool:
    """Checks if a node has a valid merge point.

    :param node: The node to check.
    :type node: :class:`Node`
    :param paths_to_check: The paths to check.
    :type paths_to_check: `list`[:class:`Node`]
    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`[:class:`Node`]
    :return: `True` if the node has a valid merge point, `False` otherwise.
    :rtype: `bool`
    """
    # get all leaf nodes of the node classes of all the given paths.
    # Then check if there is a path
    # from the node to the node class that is not through and does not have
    # outgoing logic
    for path_node in chain(
        *[get_node_as_list(child) for child in paths_to_check]
    ):
        if path_node == node:
            continue
        if has_path(node_class_graph, path_node, node):
            # check if there is at least one incoming node that has a path to
            # the path_node and not through the current path of the logic block
            # holder and does not have outgoing logic
            for in_node, _ in node_class_graph.in_edges(node):
                if has_path(node_class_graph, path_node, in_node):
                    if not in_node.outgoing_logic:
                        return True
    return False


def walk_nested_graph(
    node_class_graph: "DiGraph[Node]",
) -> PUMLGraph:
    """Walks a nested graph and creates a PlantUML graph from it.

    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`[:class:`Node`]
    :return: The PlantUML graph.
    :rtype: :class:`PUMLGraph`
    """
    sub_graph_node_puml_graphs: list[tuple[SubGraphNode, PUMLGraph]] = []
    sub_graph_nodes = [
        node
        for node in node_class_graph.nodes
        if isinstance(node, SubGraphNode)
    ]
    for sub_graph_node in sub_graph_nodes:
        sub_graph_node_puml_graphs.append(
            (sub_graph_node, walk_nested_graph(sub_graph_node.sub_graph))
        )
    puml_graph = create_puml_graph_from_node_class_graph(node_class_graph)
    for sub_graph_node, sub_graph_puml_graph in sub_graph_node_puml_graphs:
        puml_graph.add_sub_graph_to_puml_nodes_with_ref(
            sub_graph_puml_graph, sub_graph_node.uid
        )
    return puml_graph
