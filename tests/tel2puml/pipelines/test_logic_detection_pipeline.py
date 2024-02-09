"""Test the logic detection pipeline.
"""
from test_harness.utils import check_dict_equivalency
from tel2puml.pipelines.logic_detection_pipeline import Event


class TestEvent:
    @staticmethod
    def test_add_new_edge_to_conditional_count_matrix():
        """Tests for method add_new_edge_to_conditional_count_matrix"""
        event = Event("A")
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [[0]]
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [[0, 0], [0, 0]]
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        event.conditional_count_matrix[0, 0] = 1
        event.conditional_count_matrix[2, 2] = 1
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0],
        ]

    @staticmethod
    def test_add_new_edge_to_edge_counts_per_data_point():
        """Tests for method add_new_edge_to_edge_counts_per_data_point"""
        event = Event("A")
        for i, edge_tuple in enumerate(
            [("A", "B"), ("B", "C"), ("C", "D")]
        ):
            event.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
            assert edge_tuple in event.edge_counts_per_data_point
            check_dict_equivalency(
                event.edge_counts_per_data_point[edge_tuple],
                {
                    "data_count": 0,
                    "total_count": 0,
                    "index": i,
                }
            )

    @staticmethod
    def test_update_conditional_count_matrix():
        """Tests for method update_conditional_count_matrix"""
        event = Event("A")
        data_point_edges = {("A", "B"), ("B", "C"), ("C", "D")}
        for _ in range(len(data_point_edges)):
            event.add_new_edge_to_conditional_count_matrix()
        for edge_tuple in data_point_edges:
            event.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
        event.update_conditional_count_matrix(data_point_edges)
        assert event.conditional_count_matrix.tolist() == [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        data_point_edges = {("A", "B"), ("B", "C")}
        event.update_conditional_count_matrix(data_point_edges)
        to_check_list = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        index_ab = event.edge_counts_per_data_point[("A", "B")]["index"]
        index_bc = event.edge_counts_per_data_point[("B", "C")]["index"]
        for i in [index_ab, index_bc]:
            for j in [index_ab, index_bc]:
                to_check_list[i][j] += 1
        assert event.conditional_count_matrix.tolist() == to_check_list
