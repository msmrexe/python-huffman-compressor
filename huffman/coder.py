# huffman/coder.py

"""
The main HuffmanCompressor class.

This class encapsulates all logic for compression
and decompression, including:
- Building frequency tables
- Building the Huffman tree (using a min-priority queue)
- Generating the code table
- Packing/unpacking data to/from a binary file format
"""

import heapq
from collections import Counter
from .node import HuffmanNode

class HuffmanCompressor:
    """Handles the compression and decompression of files."""

    def __init__(self):
        self.tree: HuffmanNode | None = None
        self.code_table: dict[int, str] = {}
        
    def _read_file(self, path: str) -> bytes:
        """Reads a file in binary mode."""
        with open(path, 'rb') as f:
            return f.read()

    def _write_file(self, path: str, data: bytes):
        """Writes bytes to a file in binary mode."""
        with open(path, 'wb') as f:
            f.write(data)

    def _build_freq_table(self, data: bytes) -> Counter:
        """Builds a frequency table from the input data."""
        return Counter(data) # Counter is a dict-like object

    def _build_tree(self, freq_table: Counter):
        """Builds the Huffman tree using a min-priority queue."""
        
        # Create a min-priority queue (min-heap) of leaf nodes
        priority_queue = [
            HuffmanNode(freq=count, char=byte) 
            for byte, count in freq_table.items()
        ]
        heapq.heapify(priority_queue) # Turn list into a heap

        # While there is more than one node in the queue
        while len(priority_queue) > 1:
            # Pop the two nodes with the *smallest* frequency
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)

            # Create a new internal parent node
            parent_freq = left.freq + right.freq
            parent = HuffmanNode(freq=parent_freq, left=left, right=right)

            # Push the new parent node back into the queue
            heapq.heappush(priority_queue, parent)

        # The last remaining node is the root of the tree
        self.tree = priority_queue[0]

    def _build_code_table(self):
        """Generates the {char: bit_code} mapping by traversing the tree."""
        self.code_table = {}
        
        def _traverse(node: HuffmanNode, current_code: str):
            # If this is an internal node, go deeper
            if node.left: # Huffman trees are full, so no need to check right
                _traverse(node.left, current_code + '0')
                _traverse(node.right, current_code + '1')
            # If this is a leaf node, save the code
            else:
                self.code_table[node.char] = current_code

        # Handle edge case: file with only one unique byte
        if self.tree and not self.tree.left:
             self.code_table[self.tree.char] = '0'
        elif self.tree:
             _traverse(self.tree, "")

    def _serialize_tree(self) -> str:
        """
        Serializes the tree into a bit string.
        '0' = Internal Node
        '1' = Leaf Node, followed by 8 bits for the char byte.
        """
        bits = ""
        
        def _traverse(node: HuffmanNode):
            nonlocal bits
            if node.char is not None: # Leaf node
                bits += '1'
                bits += f'{node.char:08b}' # Append 8-bit byte
            else: # Internal node
                bits += '0'
                _traverse(node.left)
                _traverse(node.right)
        
        _traverse(self.tree)
        return bits

    def _encode_data(self, data: bytes) -> str:
        """Encodes the raw data into a single bit string."""
        return "".join(self.code_table[byte] for byte in data)

    def _pack_data(self, text_len: int, tree_bits: str, data_bits: str) -> bytes:
        """
        Packs the header and data into a final byte array.
        
        File Format:
        [ 8 bytes ] Original text length (for decoder)
        [ 4 bytes ] Tree bit-string length (for decoder)
        [ 1 byte  ] Padding bits (0-7)
        [ N bytes ] Packed (tree + data) bits
        """
        total_bits = tree_bits + data_bits
        
        # Calculate padding
        padding = (8 - (len(total_bits) % 8)) % 8
        total_bits += '0' * padding
        
        # Create the header
        header = bytearray()
        header.extend(text_len.to_bytes(8, 'big'))       # 8 bytes for text length
        header.extend(len(tree_bits).to_bytes(4, 'big')) # 4 bytes for tree length
        header.extend(padding.to_bytes(1, 'big'))        # 1 byte for padding

        # Pack the bits into bytes
        packed_data = bytearray()
        for i in range(0, len(total_bits), 8):
            byte_str = total_bits[i:i+8]
            packed_data.append(int(byte_str, 2))
            
        return bytes(header + packed_data)

    def compress(self, input_path: str, output_path: str) -> tuple[int, int]:
        """Compresses a file and writes the result."""
        print(f"Compressing '{input_path}'...")
        
        # 1. Read data
        data = self._read_file(input_path)
        if not data:
            print("File is empty. Nothing to compress.")
            return 0, 0
        original_size = len(data)
        
        # 2. Build frequency table and tree
        freq_table = self._build_freq_table(data)
        self._build_tree(freq_table)
        
        # 3. Build code table
        self._build_code_table()
        
        # 4. Serialize tree and encode data
        tree_bits = self._serialize_tree()
        data_bits = self._encode_data(data)
        
        # 5. Pack data into binary format
        packed_bytes = self._pack_data(original_size, tree_bits, data_bits)
        compressed_size = len(packed_bytes)
        
        # 6. Write to file
        self._write_file(output_path, packed_bytes)
        
        print(f"Original size: {original_size} bytes")
        print(f"Compressed size: {compressed_size} bytes")
        ratio = compressed_size / original_size if original_size > 0 else 0
        print(f"Compression ratio: {ratio:.2%}")
        
        return original_size, compressed_size

    def _deserialize_tree(self, bits_iter: iter) -> HuffmanNode:
        """
        Rebuilds the tree from the serialized bit string.
        This is a clean, recursive alternative to your original.
        """
        bit = next(bits_iter)
        
        if bit == '0': # Internal node
            left = self._deserialize_tree(bits_iter)
            right = self._deserialize_tree(bits_iter)
            return HuffmanNode(freq=0, left=left, right=right)
        else: # Leaf node
            byte_bits = "".join(next(bits_iter) for _ in range(8))
            byte_val = int(byte_bits, 2)
            return HuffmanNode(freq=0, char=byte_val)

    def _decode_data(self, data_bits: str, text_len: int) -> bytes:
        """Decodes the data bits using the reconstructed tree."""
        decoded_bytes = bytearray()
        
        # Handle edge case: single-character file
        if self.tree.char is not None:
            return bytearray([self.tree.char] * text_len)
            
        current_node = self.tree
        for bit in data_bits:
            current_node = current_node.left if bit == '0' else current_node.right
            
            if current_node.char is not None: # Reached a leaf
                decoded_bytes.append(current_node.char)
                current_node = self.tree # Reset to root
                
                # Stop once we've recovered all characters
                if len(decoded_bytes) == text_len:
                    break
                    
        return bytes(decoded_bytes)

    def decompress(self, input_path: str, output_path: str):
        """Decompresses a file and writes the result."""
        print(f"Decompressing '{input_path}'...")
        
        # 1. Read data
        data = self._read_file(input_path)
        if len(data) < 13: # Header size
            print("Error: File is too small or corrupt.")
            return

        # 2. Parse header
        text_len = int.from_bytes(data[0:8], 'big')
        tree_len = int.from_bytes(data[8:12], 'big')
        padding = int.from_bytes(data[12:13], 'big')
        
        # 3. Unpack bits
        packed_data = data[13:]
        bit_string = "".join(f'{byte:08b}' for byte in packed_data)
        
        # 4. Remove padding
        if padding > 0:
            bit_string = bit_string[:-padding]
            
        # 5. Separate tree and data bits
        tree_bits = bit_string[:tree_len]
        data_bits = bit_string[tree_len:]
        
        # 6. Rebuild tree
        self.tree = self._deserialize_tree(iter(tree_bits))
        
        # 7. Decode data
        decoded_data = self._decode_data(data_bits, text_len)
        
        # 8. Write to file
        self._write_file(output_path, decoded_data)
        print(f"Successfully decompressed and saved to '{output_path}'.")
