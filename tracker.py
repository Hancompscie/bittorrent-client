import requests # type: ignore
import urllib.parse
import struct

class TrackerClient:
    def __init__(self, announce_url, info_hash, peer_id, port, uploaded=0, downloaded=0, left=0):
        self.announce_url = announce_url
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port
        self.uploaded = uploaded
        self.downloaded = downloaded
        self.left = left
        
    def announce(self, event='started'):
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': self.port,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'event': event,
            'compact': 1
        }
        
        url = self.announce_url + '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return self._parse_response(response.content)
        except:
            return []
            
        return []
    
    def _parse_response(self, data):
        try:
            decoded = bencode.decode(data) # type: ignore
            peers_data = decoded.get(b'peers', b'')
            
            peers = []
            for i in range(0, len(peers_data), 6):
                if i + 6 <= len(peers_data):
                    ip = '.'.join(str(b) for b in peers_data[i:i+4])
                    port = struct.unpack('>H', peers_data[i+4:i+6])[0]
                    peers.append((ip, port))
                    
            return peers
        except:
            return []