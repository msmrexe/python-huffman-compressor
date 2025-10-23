# huffman/node.py

"""
Defines the HuffmanNode used for building the compression tree.
"""

from dataclasses import dataclass, field

@dataclass(order=True)
class HuffmanNode:
    """
    A node in the Huffman tree.
    
    Comparison is based on frequency, which is required
    for the min-priority queue (heapq).
    """
    
    # Sort by frequency
    freq: int = field(init=True, compare=True)
    
    # 'char' is the byte value (0-255) for leaf nodes,
    # None for internal nodes.
    char: int | None = field(init=True, default=None, compare=False)
    
    # Child nodes
    left: 'HuffmanNode' | None = field(init=True, default=None, compare=False)
    right: 'HuffmanNode' | None = field(init=True, default=None, compare=False)
