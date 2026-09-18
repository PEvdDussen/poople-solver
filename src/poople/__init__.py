from poople.base import app
from poople.finder import DEFAULT_WORD_LIST, find_shortest_paths
from poople.statistics import complete_statistics

__all__ = ["DEFAULT_WORD_LIST", "app", "complete_statistics", "find_shortest_paths"]

if __name__ == "__main__":
    app()
