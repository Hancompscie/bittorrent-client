import os
import hashlib
import struct
import time
from pathlib import Path

def create_torrent(file_path, trackers, piece_size=16384):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    pieces = []
    for i in range(0, len(data), piece_size):
        piece = data[i:i+piece_size]
        piece_hash = hashlib.sha1(piece).digest()
        pieces.append(piece_hash)
    
    info = {
        b'name': file_name.encode(),
        b'length': file_size,
        b'piece length': piece_size,
        b'pieces': b''.join(pieces)
    }
    
    info_encoded = bencode_encode(info)
    info_hash = hashlib.sha1(info_encoded).digest()
    
    torrent = {
        b'announce': trackers[0].encode(),
        b'announce-list': [[t.encode()] for t in trackers],
        b'info': info
    }
    
    torrent_encoded = bencode_encode(torrent)
    
    output_file = f"{file_name}.torrent"
    with open(output_file, 'wb') as f:
        f.write(torrent_encoded)
    
    print(f"Torrent created: {output_file}")
    print(f"Info hash: {info_hash.hex()}")
    return output_file

def bencode_encode(obj):
    if isinstance(obj, str):
        obj = obj.encode()
    
    if isinstance(obj, bytes):
        return str(len(obj)).encode() + b':' + obj
    elif isinstance(obj, int):
        return b'i' + str(obj).encode() + b'e'
    elif isinstance(obj, list):
        return b'l' + b''.join(bencode_encode(item) for item in obj) + b'e'
    elif isinstance(obj, dict):
        items = []
        for k, v in sorted(obj.items()):
            if isinstance(k, str):
                k = k.encode()
            items.append(bencode_encode(k))
            items.append(bencode_encode(v))
        return b'd' + b''.join(items) + b'e'
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")

if __name__ == "__main__":
    trackers = [
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://tracker.leechers-paradise.org:6969/announce"
    ]
    
    create_torrent("test.txt", trackers)