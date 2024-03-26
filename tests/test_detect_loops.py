from tel2puml.detect_loops import Loop, detect_loops


class TestLoop():
    
    @staticmethod
    def test_init():
        loop = Loop()
        assert isinstance(loop.sub_loops, list)


def test_detect_loops():
    graph = NotImplemented
    loops = detect_loops(graph)
    loop, = loops
    assert isinstance(loop, Loop)
