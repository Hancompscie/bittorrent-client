import os

class PieceManager:
    def __init__(self, total_pieces, piece_length, total_length, output_path):
        self.total_pieces = total_pieces
        self.piece_length = piece_length
        self.total_length = total_length
        self.output_path = output_path
        self.bitfield = [False] * total_pieces
        self.pieces_data = {}
        
    def is_piece_missing(self, piece_index):
        return not self.bitfield[piece_index]
    
    def add_piece(self, piece_index, data):
        self.pieces_data[piece_index] = data
        self.bitfield[piece_index] = True
        
    def is_complete(self):
        return all(self.bitfield)
    
    def save_to_file(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'wb') as f:
            for i in range(self.total_pieces):
                if i in self.pieces_data:
                    f.write(self.pieces_data[i])
                else:
                    blank = b'\x00' * self._get_piece_length(i)
                    f.write(blank)
                    
    def _get_piece_length(self, piece_index):
        if piece_index == self.total_pieces - 1:
            last_piece_size = self.total_length % self.piece_length
            return last_piece_size if last_piece_size > 0 else self.piece_length
        return self.piece_length