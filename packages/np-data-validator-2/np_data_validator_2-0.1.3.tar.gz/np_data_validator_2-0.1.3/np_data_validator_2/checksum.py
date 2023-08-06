import os
import zlib


def generate_checksum(
    filepath: str,
    chunk_size=65536,  # bytes
) -> str:
    """
    generate crc32 with for loop to read large files in chunks
    """
    size = os.path.getsize(filepath)
    with open(filepath, "rb") as f:
        crc = 0
        for _ in range(int(size / chunk_size) + 1):
            crc = zlib.crc32(f.read(chunk_size), crc)

        return "%08X" % (crc & 0xFFFFFFFF)
