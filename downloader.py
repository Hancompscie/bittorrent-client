import socket
import struct
import random
import time
from threading import Thread, Lock

class PeerConnection:
    def __init__(self, ip, port, info_hash, peer_id, piece_manager, piece_length, total_length):
        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.piece_manager = piece_manager
        self.piece_length = piece_length
        self.total_length = total_length
        self.socket = None
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.ip, self.port))
            self._handshake()
            return True
        except:
            return False
            
    def _handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = len(pstr)
        reserved = b'\x00' * 8
        
        handshake = struct.pack('!B', pstrlen) + pstr + reserved + self.info_hash + self.peer_id
        self.socket.send(handshake)
        
        response = self.socket.recv(68)
        if len(response) >= 68:
            response_hash = response[28:48]
            if response_hash == self.info_hash:
                return True
        return False
        
    def download_piece(self, piece_index):
        if not self._send_request(piece_index):
            return None
            
        piece_data = b''
        expected_length = self.piece_length
        if piece_index == self.piece_manager.total_pieces - 1:
            last_piece = self.total_length % self.piece_length
            expected_length = last_piece if last_piece > 0 else self.piece_length
            
        while len(piece_data) < expected_length:
            try:
                message = self._receive_message()
                if not message:
                    break
                    
                msg_id = message[0]
                if msg_id == 7:
                    data = message[1:]
                    piece_data += data
            except:
                break
                
        if len(piece_data) == expected_length:
            return piece_data
        return None
        
    def _send_request(self, piece_index):
        try:
            self._send_message(6, struct.pack('!III', piece_index, 0, self.piece_length))
            return True
        except:
            return False
            
    def _send_message(self, msg_id, payload=b''):
        length = struct.pack('!I', len(payload) + 1)
        self.socket.send(length + bytes([msg_id]) + payload)
        
    def _receive_message(self):
        length_data = self.socket.recv(4)
        if len(length_data) < 4:
            return None
            
        length = struct.unpack('!I', length_data)[0]
        if length == 0:
            return None
            
        message = self.socket.recv(length)
        return message
        
    def close(self):
        if self.socket:
            self.socket.close()