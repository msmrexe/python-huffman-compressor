# main.py

"""
Huffman Coding Tool - Command-Line Interface

This script provides a CLI for compressing and decompressing
files using the HuffmanCompressor class.
"""

import argparse
import sys
from huffman.coder import HuffmanCompressor

def handle_encode(args):
    """Callback function to handle the 'encode' command."""
    if not args.input or not args.output:
        print("Error: Both input and output files are required for encoding.")
        sys.exit(1)
        
    compressor = HuffmanCompressor()
    try:
        compressor.compress(args.input, args.output)
        print(f"Successfully compressed '{args.input}' to '{args.output}'")
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_decode(args):
    """Callback function to handle the 'decode' command."""
    if not args.input or not args.output:
        print("Error: Both input and output files are required for decoding.")
        sys.exit(1)
        
    compressor = HuffmanCompressor()
    try:
        compressor.decompress(args.input, args.output)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input}'")
    except Exception as e:
        print(f"An error occurred during decompression (file may be corrupt): {e}")

def main():
    """Parses command-line arguments and runs the specified command."""
    
    parser = argparse.ArgumentParser(
        description="Huffman Coding Compression Tool",
        epilog="Example: python main.py encode -i test.txt -o test.huff"
    )
    
    subparsers = parser.add_subparsers(
        title="Commands", 
        dest="command",
        required=True,
        help="Specify 'encode' or 'decode'."
    )
    
    # --- Encode Command ---
    parser_enc = subparsers.add_parser(
        'encode',
        help="Compress a file."
    )
    parser_enc.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help="Path to the input file to compress."
    )
    parser_enc.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help="Path to save the compressed output file."
    )
    parser_enc.set_defaults(func=handle_encode)
    
    # --- Decode Command ---
    parser_dec = subparsers.add_parser(
        'decode',
        help="Decompress a file."
    )
    parser_dec.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help="Path to the compressed file to decompress."
    )
    parser_dec.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help="Path to save the decompressed output file."
    )
    parser_dec.set_defaults(func=handle_decode)
    
    # Parse args and call the correct handler function
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
