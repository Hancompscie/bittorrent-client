import bencode # type: ignore
import hashlib
import os

class TorrentParser:
    def __init__(self, torrent_path):
        self.torrent_path = torrent_path
        self.metadata = {}
        self.info_hash = None
        self.piece_length = 0
        self.pieces = []
        self.file_path = ""
        self.total_length = 0
        
    def parse(self):
        with open(self.torrent_path, 'rb') as f:
            torrent_data = f.read()
            self.metadata = bencode.decode(torrent_data)
            
        info = self.metadata[b'info']
        self.info_hash = hashlib.sha1(bencode.encode(info)).digest()
        self.piece_length = info[b'piece length']
        
        pieces_data = info[b'pieces']
        self.pieces = [pieces_data[i:i+20] for i in range(0, len(pieces_data), 20)]
        
        if b'files' in info:
            self.total_length = sum(file[b'length'] for file in info[b'files'])
            self.file_path = self._create_multi_file_structure(info)
        else:
            self.total_length = info[b'length']
            self.file_path = info[b'name'].decode()
            
        return self
    
    def _create_multi_file_structure(self, info):
        base_path = info[b'name'].decode()
        os.makedirs(f"downloads/{base_path}", exist_ok=True)
        
        for file in info[b'files']:
            file_path = file[b'path']
            full_path = f"downloads/{base_path}/{'/'.join(p.decode() for p in file_path)}"
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
        return base_path