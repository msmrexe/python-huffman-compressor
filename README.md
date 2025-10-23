# Python Huffman Coding

This project is a Python implementation of the Huffman coding algorithm for lossless data compression. It was developed for an Algorithms & Data Structures course and has been built as an efficient command-line tool.

This implementation builds the Huffman tree using a **min-priority queue** (via `heapq`) for optimal $O(n \log n)$ performance and packs the encoded data into a **binary file** to achieve true compression.

## Features

* **Real Compression**: Data is packed bit-by-bit into a binary file.
* **Efficient Tree Building**: Uses `heapq` (a min-priority queue) to construct the Huffman tree efficiently.
* **Modular Design**: Logic is separated into a `huffman` module (containing `coder.py` and `node.py`) and a `main.py` CLI.
* **Handles Any File**: Can compress and decompress any file type (text, images, binaries) by operating on raw bytes.
* **Robust CLI**: A clean command-line interface using `argparse` with `encode` and `decode` commands.
* **Custom Binary Format**: Uses a custom header to store the tree and file metadata, allowing the decoder to reconstruct the data perfectly.

## How It Works

### Algorithm

1.  **Frequency Analysis**: Read the input file and count the frequency of each byte (0-255).
2.  **Tree Building**:
    * Create a leaf `Node` for each unique byte and add it to a min-priority queue (min-heap).
    * While the queue has more than one node:
        * Pop the two nodes with the *lowest* frequency.
        * Create a new internal parent node with a frequency equal to the sum of its children.
        * Push the new parent node back into the queue.
    * The final node in the queue is the root of the Huffman tree.
3.  **Code Generation**: Traverse the tree from the root. Assign '0' for a left turn and '1' for a right turn. The path to each leaf node (a byte) is its new, variable-length binary code.
4.  **Encoding**:
    * Serialize the Huffman tree itself into a bit string (e.g., `0` for internal, `1` + 8-bit-byte for leaf).
    * Encode the entire file's data by replacing each byte with its new bit code.
    * Pack the tree bits, data bits, and a header into a single binary file.

### Binary File Format

The compressed `.huff` file has a custom header to allow for decompression:

| Size (bytes) | Description |
| :--- | :--- |
| 8 | **Original File Size**: The total number of bytes in the decoded file (needed to stop decoding). |
| 4 | **Tree Length**: The number of *bits* used by the serialized tree. |
| 1 | **Padding Bits**: The number of '0' bits (0-7) added to the end to make a full byte. |
| N | **Packed Data**: The rest of the file, containing the tree bits and the data bits packed tightly into bytes. |

## Project Structure

```
huffman-coding/
├── .gitignore               # Ignores generated files
├── LICENSE                  # MIT license file
├── README.md                # This documentation
├── main.py                  # The main runnable script (CLI)
└── huffman/
    ├── __init__.py          # Makes 'huffman' a Python package
    ├── node.py              # Defines the HuffmanNode dataclass
    └── coder.py             # Contains the HuffmanCompressor class
```

## Usage

No external libraries are required (only built-in Python modules).

### 1. Encode (Compress) a File

Use the `encode` command.

```bash
# Compress a text file
python main.py encode -i my_document.txt -o compressed.huff

# Compress an image
python main.py encode -i my_image.png -o compressed.huff
```
You will see an output showing the original and compressed sizes and the compression ratio.

### 2. Decode (Decompress) a File

Use the `decode` command to restore the original file.

```bash
# Decode the compressed file
python main.py decode -i compressed.huff -o my_document.restored.txt

# Decode the image
python main.py decode -i compressed.huff -o my_image.restored.png
```
The restored file will be a perfect, byte-for-byte copy of the original.

---

## Author

Feel free to connect or reach out if you have any questions!

* **Maryam Rezaee**
* **GitHub:** [@msmrexe](https://github.com/msmrexe)
* **Email:** [ms.maryamrezaee@gmail.com](mailto:ms.maryamrezaee@gmail.com)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
