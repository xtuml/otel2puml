"""
This module contains functions that can be used to parse a logic tree created
    (created by jAlergia) into PUML.
"""

from tel2puml.node_map_to_puml.node import Node


def is_in_loop(
    target: Node, logic_lines: dict, node=None, depth=0, max_depth=100
):
    """
    Checks if a target node is in a loop within a given logic map.

    Parameters:
        target (Node): The target node to check.
        logic_lines (dict): The logic map containing loop information.
        node (Node, optional): The current node being checked.
            Defaults to equal Target.
        depth (int, optional): The current depth of recursion.
            Defaults to 0.
        max_depth (int, optional): The maximum depth of recursion.
            Defaults to 100.

    Returns:
        bool: True if the target node is in a loop, False otherwise.
    """
    output = False
    if node is None:
        node = target

    if depth > max_depth:
        return output

    outgoing_uid = [item.uid for item in node.outgoing]
    if target.uid in outgoing_uid:
        return True
    elif logic_lines["LOOP"]["end"] in outgoing_uid:
        return False

    for outgoing in node.outgoing:
        output = (
            is_in_loop(target, logic_lines, outgoing, depth + 1, max_depth)
            if not output
            else output
        )

    return output


def drill_down_tree(
    node: Node,
    lookup_table: dict,
    logic_lines: dict,
    max_depth: int = 100,
    depth: int = 0,
):
    """
    Recursively drills down a tree starting from the given node if all
        nodes only have one outgoing connection each, avoiding loops. If this
        function is run on a node in a loop, the last node in the loop will be
        returned.

    Args:
        node (Node): The starting node of the tree.
        lookup_table: A lookup table used to filter the allowed nodes.
        max_depth (int, optional): The maximum depth to drill down.
            Defaults to 10.
        depth (int, optional): The current depth of the recursion.
            Defaults to 0.

    Returns:
        Node: The resulting node after drilling down the tree.
    """
    if depth >= max_depth:
        return node

    allowed_nodes = [
        outgoing
        for outgoing in node.outgoing
        if (outgoing.uid in lookup_table)
        and (not is_in_loop(outgoing, logic_lines))
    ]
    if len(node.outgoing) == 1 or (len(allowed_nodes) == 1):
        if len(node.outgoing) > 1:
            return drill_down_tree(
                allowed_nodes[0],
                lookup_table,
                logic_lines,
                max_depth,
                depth + 1,
            )
        else:
            return drill_down_tree(
                node.outgoing[0],
                lookup_table,
                logic_lines,
                max_depth,
                depth + 1,
            )

    return node


def get_reverse_node_tree(
    node: Node, lookup_table: dict, logic_lines: dict, max_depth: int = 100
):
    """
    Returns a list of nodes in reverse order from the given node to its
        parent node.

    Args:
        node (Node): The starting node.
        lookup_table: The lookup table used to find parent nodes.
        max_depth (int, optional): The maximum depth to traverse.
            Defaults to 10.

    Returns:
        list: A list of nodes in reverse order from the given node to its
            parent node.
    """
    depth = 0
    node_end = drill_down_tree(node, lookup_table, logic_lines, max_depth)
    node_tree = []

    current_node = node

    while current_node != node_end:
        if depth >= max_depth:
            return node_tree

        current_node = drill_down_tree(
            current_node, lookup_table, logic_lines, 1
        )

        node_tree.append(current_node)

        depth += 1

    node_tree.reverse()

    return node_tree


def get_tree_distance_from_convergence(
    reverse_node_trees: dict, smallest_tree: list
):
    """
    Calculate whether all nodes in a list of reversed trees converge.

    Parameters:
    reverse_node_trees (dict): A dictionary containing reverse node trees.
    smallest_tree (list): The smallest tree present in reverse_node_trees.

    Returns:
    int: The minimum number of levels down that must be navigated from the
        starting point before all trees have the same value.
    """
    tree_distance_from_convergence = 0
    if len(smallest_tree) != 0:
        for key, val in reverse_node_trees.items():
            if val[0] != smallest_tree[0]:
                return 0

    for loop in range(0, len(smallest_tree)):
        trees_are_similar = True
        for key, val in reverse_node_trees.items():
            if val[loop] != smallest_tree[loop]:
                trees_are_similar = False

        if trees_are_similar:
            tree_distance_from_convergence += 1

    if (
        len(
            [
                tree_name
                for tree_name in reverse_node_trees
                if len(reverse_node_trees[tree_name]) == 0
            ]
        )
        > 0
    ):
        tree_distance_from_convergence = 0

    return tree_distance_from_convergence


def append_logic_middle_or_end(
    output: list, idx: int, node_tree: Node, logic_lines: dict
):
    """
    Appends a node for the middle or end of a logic branch to the output
        list.

    Args:
        output (list): The list to append the logic to.
        idx (int): The index of the current node in the outgoing logic list.
        node_tree (NodeTree): The node tree object representing the current
            node.
        logic_lines (dict): A dictionary containing the logic lines for
            different node types.

    Returns:
        list: The updated output list with the logic appended.
    """

    if idx < len(node_tree.outgoing_logic[0].outgoing) - 1:
        if (
            len(node_tree.outgoing_logic[0].outgoing) > 2
            and node_tree.outgoing_logic[0].uid == "XOR"
        ):
            uid_to_append = (
                logic_lines["SWITCH"]["middle"][0]
                + str(idx + 2)
                + logic_lines["SWITCH"]["middle"][1]
            )
        else:
            uid_to_append = logic_lines[node_tree.outgoing_logic[0].uid][
                "middle"
            ]
    else:
        if (
            len(node_tree.outgoing_logic[0].outgoing) > 2
            and node_tree.outgoing_logic[0].uid == "XOR"
        ):
            uid_to_append = logic_lines["SWITCH"]["end"]
        else:
            uid_to_append = logic_lines[node_tree.outgoing_logic[0].uid]["end"]
    output.append(
        node_tree.outgoing_logic[0].copy_node(
            uid=uid_to_append,
        )
    )

    return output


def append_logic_start(output: list, node_tree: Node, logic_lines: dict):
    """
    Appends the logic start node OR the switch start
        (as it's different to all the others) to the output list if required.

    Args:
        output (list): The list to which the logic start node will be appended.
        node_tree (NodeTree): The node tree containing the logic start node.
        logic_lines (dict): A dictionary containing the logic lines for
            different node types.

    Returns:
        list: The updated output list with the logic start node appended.
    """
    if (
        len(node_tree.outgoing_logic[0].outgoing) > 2
        and node_tree.outgoing_logic[0].uid == "XOR"
    ):
        output.append(
            node_tree.outgoing_logic[0].copy_node(
                uid=logic_lines["SWITCH"]["start"],
            )
        )
        output.append(
            node_tree.outgoing_logic[0].copy_node(
                uid='case ("1")',
            )
        )
    else:
        output.append(
            node_tree.outgoing_logic[0].copy_node(
                uid=logic_lines[node_tree.outgoing_logic[0].uid]["start"],
            )
        )
    return output


def handle_loop_start(output: list, node_tree: Node, logic_lines: dict):
    """
    Detects the start of a loop and appends a loop start node if one is
        detected.

    Args:
        output (list): The list of output nodes.
        node_tree (Node): The current node in the node tree.
        logic_lines (dict): The logic lines dictionary.

    Returns:
        list: The updated list of output nodes.
    """

    all_ancestors_in_loop = True
    possible_descendant_incoming = []

    for incoming in node_tree.incoming:
        if (
            is_in_loop(incoming, logic_lines, node_tree)
            and len(incoming.incoming) > 0
        ):
            possible_descendant_incoming.append(incoming)
        if not is_in_loop(incoming, logic_lines, node_tree):
            all_ancestors_in_loop = False

    if len(possible_descendant_incoming) > 0 and (
        not all_ancestors_in_loop
        or (
            len(node_tree.incoming) > 1
            or (
                len(node_tree.incoming) == 1
                and len(
                    [
                        outgoing
                        for outgoing in node_tree.incoming[0].outgoing
                        if outgoing.uid == logic_lines["LOOP"]["end"]
                    ]
                )
                == 1
            )
        )
    ):
        output.append(node_tree.copy_node(uid=logic_lines["LOOP"]["start"]))
    return output


def get_reverse_node_tree_dict(
    node_tree: Node, lookup_table: dict, logic_lines: dict
):
    """
    Returns a dictionary mapping each outgoing node in the given node_tree to
        its reverse node tree.

    Args:
        node_tree (NodeTree): The node tree to process.
        lookup_table (dict): A lookup table for reverse node trees.

    Returns:
        dict: A dictionary mapping each outgoing node to its reverse node tree.
    """
    reverse_node_trees = {}
    for _, outgoing_node in enumerate(node_tree.outgoing_logic[0].outgoing):
        reverse_node_trees[outgoing_node.uid] = get_reverse_node_tree(
            outgoing_node, lookup_table, logic_lines
        )
    return reverse_node_trees


def get_smallest_reverse_tree(reverse_node_trees: dict):
    """
    Get the shallowest reverse tree from a dictionary of reverse node trees.

    Parameters:
    reverse_node_trees (dict): A dictionary containing reverse node trees.

    Returns:
    list: The smallest reverse tree found.
    """
    if len(reverse_node_trees) == 0:
        return []
    smallest_tree = []
    for _ in range(0, 100):
        smallest_tree.append(".")
    for tree in reverse_node_trees:
        if len(reverse_node_trees[tree]) < len(smallest_tree):
            smallest_tree = reverse_node_trees[tree]
    return smallest_tree


def handle_immediate_children(
    node_tree: Node,
    tree_distance_from_convergence: int,
    reverse_node_trees: dict,
    output: list,
    logic_lines: dict,
    lookup_table: dict,
    depth: int,
    max_depth: int,
):
    """
    Handles the immediate children of a given node in the node tree. This is
        essentally a 'pre-read' to try and catch edge cases like nested
        branches.

    Args:
        node_tree (Node): The node tree to analyze.
        tree_distance_from_convergence (int): The distance_from_convergence
            between the current node tree and its parent.
        reverse_node_trees (dict): A dictionary mapping node uid to a list of
            node trees.
        output (str): The output string to append the analysis results to.
        logic_lines (dict): A dict of logic lines.
        lookup_table (dict): A lookup table for node uid to node names.
        depth (int): The current depth in the node tree.
        max_depth (int): The maximum depth to analyze.

    Returns:
        str: The updated output string after analyzing the immediate children.
    """
    for idx, outgoing_node in enumerate(node_tree.outgoing_logic[0].outgoing):
        if tree_distance_from_convergence > 0:
            start_depth_to_analyse = 0
            max_depth_to_analyse = (
                len(reverse_node_trees[outgoing_node.uid])
                - tree_distance_from_convergence
                + 1
            )
        else:
            start_depth_to_analyse = depth + 1
            max_depth_to_analyse = max_depth

        output = analyse_node(
            node_tree=outgoing_node,
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=True,
            depth=start_depth_to_analyse,
            max_depth=max_depth_to_analyse,
        )

        output = append_logic_middle_or_end(
            output, idx, node_tree, logic_lines
        )
    return output


def handle_divergent_tree_children(
    tree_distance_from_convergence: int,
    tree: list,
    output: list,
    logic_lines,
    lookup_table,
):
    """
    Handles all divergent child nodes in a list of trees that eventually
        converges. This is most useful when a branch node has a complicated
        'middle' section.

    Args:
        tree_distance_from_convergence (int): The distance_from_convergence
            between the trees.
        smallest_tree (list): The list of nodes in the smallest tree.
        output (str): The current output string.
        logic_lines (dict): The list of logic lines.
        lookup_table (dict): The lookup table for node mapping.

    Returns:
        str: The updated output string.
    """
    if tree_distance_from_convergence > 0:
        sliced_tree = tree[0:tree_distance_from_convergence]
        sliced_tree.reverse()
        for node in sliced_tree:
            output = analyse_node(
                node_tree=node,
                output=output,
                logic_lines=logic_lines,
                lookup_table=lookup_table,
                append_first_node=True,
                depth=0,
                max_depth=1,
            )
    return output


def create_content_logic(
    node_tree: Node,
    output: list,
    logic_lines: dict,
    lookup_table: dict,
    append_first_node: bool = True,
    depth: int = 0,
    max_depth: int = 10,
):
    """
    Analyses a logic node and appends the correct 'logic' string to the output
        list depending on what type of node it is, as well as the 'middle' and
        'end' parts of the logic chain. It then recurs (via analyse_node) for
        any child nodes using different logic depending on whether the branch
        converges (the endif is followed by another node) or not (the endif
        terminates the PUML, leaving multiple 'leaf' nodes.
        Note that as switch statements have 'middle' sections that change based
        on index, they have to be handled differently to the other statements.

    Args:
        node_tree (Node): The root node of the tree.
        output (list): The list to store the generated content logic.
        logic_lines (dict): A dictionary containing output strings for
        different logic nodes types.
        lookup_table (dict): A lookup table of all uid nodes.
        append_first_node (bool, optional): Whether to append the first node
            to the output. Defaults to True.
        depth (int, optional): The current depth of the recursion.
            Defaults to 0.
        max_depth (int, optional): The maximum depth of the recursion.
            Defaults to 10.

    Returns:
        list: The appended-to output list
    """

    if depth >= max_depth:
        return output

    output = handle_loop_start(output, node_tree, logic_lines)

    if not append_first_node:
        append_first_node = True
    else:
        output.append(node_tree)

    output = append_logic_start(output, node_tree, logic_lines)

    reverse_node_trees = get_reverse_node_tree_dict(
        node_tree, lookup_table, logic_lines
    )

    smallest_tree = get_smallest_reverse_tree(reverse_node_trees)

    tree_distance_from_convergence = get_tree_distance_from_convergence(
        reverse_node_trees, smallest_tree
    )

    output = handle_immediate_children(
        node_tree,
        tree_distance_from_convergence,
        reverse_node_trees,
        output,
        logic_lines,
        lookup_table,
        depth,
        max_depth,
    )

    output = handle_divergent_tree_children(
        tree_distance_from_convergence,
        smallest_tree,
        output,
        logic_lines,
        lookup_table,
    )

    return output


def create_content(
    node_tree: Node,
    output: list,
    logic_lines: dict,
    lookup_table: dict,
    append_first_node: bool = True,
    depth: int = 0,
    max_depth: int = 10,
):
    """
    Appends content to the output list for 'non-logic' nodes. Note that as
        'loop' nodes either don't exist or are created at the 'tree-creation'
        stage, they are inferred from the 'non-logic' nodes handled in this
        function.
        If a 'start loop' node is detected, any children of that node
        that aren't in the loop are also appended.
        If an 'end loop' node is detected, it's just appended to output
        directly with no futher processing.

    Args:
        node_tree (Node): The root node of the tree.
        output (list): The list to which the nodes will be appended.
        logic_lines (dict): A dictionary containing logic lines.
        lookup_table (dict): A dictionary used for lookup.
        append_first_node (bool, optional): Specifies whether to append the
            first node or not. Defaults to True.
        depth (int, optional): The current depth of the traversal.
            Defaults to 0.
        max_depth (int, optional): The maximum depth allowed for traversal.
            Defaults to 10.

    Returns:
        list: The updated output list.
    """
    if depth >= max_depth:
        return output

    output = handle_loop_start(output, node_tree, logic_lines)

    if not append_first_node:
        append_first_node = True
    else:
        output.append(node_tree)

        for outgoing_node in node_tree.outgoing:
            node_is_loop = False
            if outgoing_node.uid == logic_lines["LOOP"]["end"]:
                node_is_loop = True

            if (
                (not (node_is_loop))
                and (not is_in_loop(outgoing_node, logic_lines, node_tree))
                or (outgoing_node not in output)
                and (outgoing_node.uid in lookup_table)
            ):
                output = analyse_node(
                    node_tree=outgoing_node,
                    output=output,
                    logic_lines=logic_lines,
                    lookup_table=lookup_table,
                    append_first_node=True,
                    depth=depth + 1,
                    max_depth=max_depth,
                )
            else:
                if node_is_loop:
                    output.append(outgoing_node)

    return output


def analyse_node(
    node_tree: Node,
    logic_lines: dict,
    lookup_table: dict,
    output: list = None,
    append_first_node: bool = True,
    depth: int = 0,
    max_depth: int = 10,
):
    """
    Determines whether a node is a logic node, uid node, or a leaf uid node.
        A leaf uid node just means a uid node with no outgoing connections.
        Logic nodes are passed to create_content_logic,
        uid nodes are passed to create_content,
        and leaf uid nodes are ignored -
        they are handled after all recursion is finished.

    Args:
        node_tree (Node): The node to be analyzed.
        output (list): The list to which the generated content will be
            appended.
        logic_lines (dict): A dictionary containing logic lines.
        lookup_table (dict): A dictionary used for lookup operations.
        append_first_node (bool, optional): Specifies whether to append the
            first node.
            Defaults to True.
        depth (int, optional): The current depth of the analysis.
            Defaults to 0.
        max_depth (int, optional): The maximum depth allowed for the analysis.
            Defaults to 10.

    Returns:
        list: The updated output list after the analysis.
    """

    if output is None:
        output = []

    if depth >= max_depth:
        return output

    if len(node_tree.outgoing_logic) > 0:
        output = create_content_logic(
            node_tree=node_tree,
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=append_first_node,
            depth=depth,
            max_depth=max_depth,
        )

    elif (
        (len(node_tree.outgoing_logic) == 0)
        and (len(node_tree.incoming_logic) == 0)
        and (len(node_tree.outgoing) == 0)
        and (len(node_tree.incoming) > 1)
    ):
        return output

    elif node_tree.uid in lookup_table:
        output = create_content(
            node_tree=node_tree,
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=append_first_node,
            depth=depth,
            max_depth=max_depth,
        )

    return output


def get_coords_in_nested_dict(item, dictionary: dict):
    """
    Returns whether an item is present in a twice-nested dictionary, and if so,
        what second-level key is required to obtain it.

    Args:
        item (any): The item to search for.
        dictionary (dict): The nested dictionary to search in.

    Returns:
        The coordinates of the item if found, None otherwise.
    """

    for parent in dictionary:
        for child in dictionary[parent]:
            if item == dictionary[parent][child]:
                return child
    return None


def format_output(
    input: list,
    logic_lines: dict,
    tab_chars: str,
    tab_num: int,
    event_reference: dict,
):
    """
    Uses the given list of nodes to create a PUML 'body' that can then be
        combined with the 'header' and 'footer' in another function.

    Args:
        output (list): The uid to be formatted.
        logic_lines (dict): The logic lines used for formatting.
        tab_chars (str): The characters used for indentation.
        tab_num (int): The current indentation level.
        event_reference (dict): The reference for event lines.

    Returns:
        list: The formatted output.
    """
    output = []
    for line in input:
        line = line.uid
        if line not in event_reference:
            match get_coords_in_nested_dict(line, logic_lines):
                case "start":
                    output.append(f"{tab_chars*tab_num}{line}")
                    tab_num += 1
                    if logic_lines["SWITCH"]["start"] in line:
                        tab_num += 1

                case "middle":
                    tab_num -= 1
                    output.append(f"{tab_chars*tab_num}{line}")
                    tab_num += 1

                case "end":
                    tab_num -= 1
                    if logic_lines["SWITCH"]["end"] in line:
                        tab_num -= 1
                    output.append(f"{tab_chars*tab_num}{line}")

                case _:
                    if logic_lines["SWITCH"]["middle"][0] in line:
                        tab_num -= 1
                        output.append(f"{tab_chars*tab_num}{line}")
                        tab_num += 1
                    else:
                        output.append(f"{tab_chars*tab_num}{line}")

        else:
            output.append(f"{tab_chars*tab_num}:{event_reference[line]};")
    return output


def find_nearest_extant_ancestor(
    uid_list: list, node: Node, depth: int = 0, max_depth: int = 100
):
    """
    Finds the nearest extant ancestor of a given node in a tree structure.

    Args:
        uid_list (list): List of unique identifiers of nodes in the tree.
        node (Node): The node for which to find the nearest extant ancestor.
        depth (int, optional): The current depth in the tree. Defaults to 0.
        max_depth (int, optional): The maximum depth to search for the
            ancestor. Defaults to 100.

    Returns:
        Node: The nearest extant ancestor of the given node, or the node itself
            if it is in the uid_list.
    """
    if depth >= max_depth:
        return node
    if node in uid_list:
        return node
    return find_nearest_extant_ancestor(
        uid_list, node.incoming[0], depth + 1, max_depth
    )


def insert_item_using_property_key(
    node_list: list,
    node: Node,
    logic_lines: dict,
    property_key: str,
    insert_before_item: bool = False,
):
    """
    Inserts a node into a list of nodes, using the node's incoming/outgoing
        property to determine where it should be inserted.

    Args:
        node_list (list): The list of nodes to insert into.
        node (Node): The node to be inserted.
        logic_lines (dict): A dictionary containing logic lines.
        property_key (str): The property key used to determine the insertion
            position.
        insert_before_item (bool, optional): Determines whether to insert the
            node before or after the nearest relative. Defaults to False.

    Returns:
        list: The updated node_list with the node inserted.
    """
    node_property = None
    node_property = getattr(node, property_key)

    if len(node_property) > 0:

        nearest_relative = node_property[0]

        if (nearest_relative not in node_list) and (len(node.incoming) > 0):
            nearest_relative = find_nearest_extant_ancestor(node_list, node)
        elif len(node.incoming) == 0:
            node_list.insert(0, node)
            return node_list

        node_list.reverse()

        for relative in node_property:
            if nearest_relative in node_list and relative in node_list:
                if node_list.index(nearest_relative) > node_list.index(
                    relative
                ):
                    nearest_relative = relative

        node_list.reverse()

        insertion_index = 0
        for idx, item in enumerate(node_list):
            if item == nearest_relative and idx > insertion_index:
                insertion_index = idx

        while insertion_index < len(node_list):
            if insertion_index == len(node_list) - 1:
                break

            if (
                get_coords_in_nested_dict(
                    node_list[insertion_index + 1].uid, logic_lines
                )
                is not None
            ):
                insertion_index += 1
            else:
                break

        if insert_before_item:
            node_list.insert(insertion_index, node)
        else:
            node_list.insert(insertion_index + 1, node)

    return node_list


def insert_missing_nodes(
    uid_list: list, missing_nodes: list, logic_lines: dict
):
    """
    Inserts missing nodes (normally 'leaf' nodes) into the uid list.

    Args:
        uid_list (list): The original list of uid.
        missing_nodes (list): The list of missing nodes to be inserted.

    Returns:
        list: The updated uid list with the missing nodes inserted.
    """

    for missing_node in missing_nodes:
        unchanged_uid_list = []
        for item in uid_list:
            unchanged_uid_list.append(item)

        for KVP in [
            ["incoming_logic", False],
            ["incoming", False],
            ["outgoing_logic", True],
            ["outgoing", True],
        ]:
            uid_list = insert_item_using_property_key(
                uid_list, missing_node, logic_lines, *KVP
            )
            if unchanged_uid_list != uid_list:
                break

    return uid_list


def alter_node_tree_to_contain_logic_nodes(
    lookup_table: dict, logic_table: dict
):
    """
    Modifies the node tree in the lookup table to include logic nodes.

    Args:
        lookup_table (dict): A dictionary representing the node lookup table.
        logic_table (dict): A dictionary representing the logic table.

    Returns:
        dict: The modified lookup table with logic nodes included.
    """
    if len(lookup_table) > 0:
        for logic_node_name in logic_table:
            logic_node = logic_table[logic_node_name]
            for outgoing in logic_node.outgoing:
                lookup_table[outgoing.uid].incoming_logic.append(logic_node)
            for incoming in logic_node.incoming:
                lookup_table[incoming.uid].outgoing_logic.append(logic_node)
        return lookup_table
    else:
        return lookup_table


def convert_nodes_to_puml(
    lookup_table: dict,
    head_node: Node,
    event_reference: dict,
    puml_name: str,
    logic_lines: dict = {},
):
    """
    Converts a node tree to PlantUML code.

    Args:
        lookup_table (dict): A dictionary mapping event names to their
            corresponding unique identifiers.
        head_node (Node): The root node of the node tree.
        event_reference (dict): A dictionary mapping event unique identifiers
            to their corresponding names.
        puml_name (str): The name of the PlantUML partition.
        logic_lines (dict, optional): A dictionary defining the logic lines for
             different types of nodes. Defaults to the standard logic strings
             used by the client.

    Returns:
        list: A list of strings representing the PlantUML code.
    """

    if logic_lines == {}:
        logic_lines = {
            "AND": {
                "start": "fork",
                "middle": "fork again",
                "end": "end fork",
            },
            "OR": {
                "start": "split",
                "middle": "split again",
                "end": "end split",
            },
            "XOR": {
                "start": "if (XOR) then (true)",
                "middle": "else (false)",
                "end": "endif",
            },
            "LOOP": {
                "start": "repeat",
                "middle": "",
                "end": "repeat while (unconstrained)",
            },
            "SWITCH": {
                "start": "switch (XOR)",
                "middle": ['case ("', '")'],
                "end": "endswitch",
            },
        }

    output = analyse_node(
        node_tree=head_node,
        logic_lines=logic_lines,
        lookup_table=lookup_table,
        append_first_node=True,
    )

    present_event_names = [
        event.uid for event in output if event.uid in lookup_table
    ]
    missing_events = [
        lookup_table[event_name]
        for event_name in lookup_table
        if event_name not in present_event_names
    ]

    output = insert_missing_nodes(output, missing_events, logic_lines)

    puml_name = puml_name
    tab_chars = "    "
    puml_header = [
        "@startuml",
        tab_chars * 0 + 'partition "' + puml_name + '" {',
        (tab_chars * 1) + 'group "' + puml_name + '"',
    ]

    tab_num = 2

    puml_footer = [
        (tab_chars * 1) + "end group",
        (tab_chars * 0 + "}"),
        "@enduml",
    ]

    formatted_output = format_output(
        output, logic_lines, tab_chars, tab_num, event_reference
    )

    return puml_header + formatted_output + puml_footer
