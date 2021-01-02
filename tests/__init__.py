from pathlib import Path

__all__ = [
    'TEST_DATA_PATH',
    'V7_PLUGIN_PATH',
]

TEST_DATA_PATH = Path(__file__).parent / 'data'

V7_PLUGIN_PATH = Path(__file__).parent.parent / 'v7'
