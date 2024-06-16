import pytest
from PyQt5.QtWidgets import QApplication
from main import Window
from bidict import bidict


@pytest.fixture(scope="module")
def app():
    """Fixture for creating the QApplication instance."""
    app = QApplication([])
    return app


@pytest.fixture
def main_window(app):
    window = Window()
    window.show()
    window.wordIndexMap = bidict(
        {
            "to": 0,
            "explore": 1,
            "strange": 2,
            "new": 3,
            "worlds": 4,
            "seek": 5,
            "out": 6,
            "life": 7,
            "and": 8,
            "civilizations": 9,
        }
    )
    window.vertexNum = 10
    window.edgeTable = [
        [0, 1, -1, -1, -1, 1, -1, -1, -1, -1],
        [-1, 0, 1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, 0, 1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, 0, 1, -1, -1, 1, -1, 1],
        [1, -1, -1, -1, 0, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 0, 1, -1, -1, -1],
        [-1, -1, -1, 1, -1, -1, 0, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 0, 1, -1],
        [-1, -1, -1, 1, -1, -1, -1, -1, 0, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, 0],
    ]
    return window

@pytest.mark.parametrize("words, expected",
                         [("strange worlds", "The bridge words from strange to worlds are: new"),
                          # ("forest", "queryBridgeWords error: wrong words"),
                          ("explore forest","No explore or forest in the graph!"),
                          # ("forest strange","No forest or strange in the graph!"),
                          ("to explore", "No bridge words from to to explore !"),])

def test_query_bridge(main_window,words,expected):
    main_window.textEdit.setPlainText(words)
    main_window.queryBridgeWords()
    assert main_window.textEdit_2.toPlainText() == expected

if __name__ == '__main__':
    pytest.main()

