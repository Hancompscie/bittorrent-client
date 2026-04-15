import random
import time
from torrent_parser import TorrentParser
from tracker import TrackerClient
from piece_manager import PieceManager
from downloader import PeerConnection

class BitTorrentClient:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file
        self.parser = TorrentParser(torrent_file).parse()
        self.peer_id = self._generate_peer_id()
        self.piece_manager = None
        self.peers = []
        
    def _generate_peer_id(self):
        import string
        prefix = '-BT0001-'
        suffix = ''.join(random.choices(string.digits, k=12))
        return (prefix + suffix).encode()
        
    def start(self):
        print(f"Loading torrent: {self.torrent_file}")
        print(f"Total size: {self.parser.total_length} bytes")
        print(f"Piece length: {self.parser.piece_length} bytes")
        print(f"Total pieces: {len(self.parser.pieces)}")
        
        output_path = f"downloads/{self.parser.file_path}"
        
        self.piece_manager = PieceManager(
            len(self.parser.pieces),
            self.parser.piece_length,
            self.parser.total_length,
            output_path
        )
        
        announce_url = self.parser.metadata[b'announce'].decode()
        
        tracker = TrackerClient(
            announce_url,
            self.parser.info_hash,
            self.peer_id,
            6881,
            left=self.parser.total_length
        )
        
        self.peers = tracker.announce('started')
        print(f"Found {len(self.peers)} peers")
        
        self._download_pieces()
        
        if self.piece_manager.is_complete():
            self.piece_manager.save_to_file()
            print(f"Download complete! File saved to {output_path}")
        else:
            print("Download incomplete")

    def _download_pieces(self):
        missing_pieces = [i for i in range(self.piece_manager.total_pieces)
                         if self.piece_manager.is_piece_missing(i)]

        print(f"Need to download {len(missing_pieces)} pieces")

        for piece_index in missing_pieces[:10]:
            downloaded = False

            for ip, port in self.peers[:5]:
                print(f"Trying peer {ip}:{port} for piece {piece_index}")

                peer = PeerConnection(
                    ip, port,
                    self.parser.info_hash,
                    self.peer_id,
                    self.piece_manager,
                    self.parser.piece_length,
                    self.parser.total_length
                )

                if peer.connect():
                    piece_data = peer.download_piece(piece_index)
                    peer.close()

                    if piece_data:
                        self.piece_manager.add_piece(piece_index, piece_data)
                        print(f"Piece {piece_index} downloaded successfully")
                        downloaded = True
                        break

            if not downloaded:
                print(f"Failed to download piece {piece_index}")

            time.sleep(1)

        completed = sum(1 for i in range(self.piece_manager.total_pieces)
                       if not self.piece_manager.is_piece_missing(i))
        print(f"Progress: {completed}/{self.piece_manager.total_pieces} pieces")

def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <torrent_file>")
        return

    torrent_file = sys.argv[1]
    client = BitTorrentClient(torrent_file)
    client.start()

if __name__ == "__main__":
    main()