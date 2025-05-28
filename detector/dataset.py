import torch
from torch.utils.data import Dataset

class CovertDetectorDataset(Dataset):
    def __init__(self, covert_filename, normal_filename, window_size=50):
        file = open(covert_filename, 'r')
        lines = file.readlines()
        file.close()

        self.data = []
        self.labels = []

        for i in range(len(lines) - window_size):
            packet_sequence = []
            for j in range(window_size):
                line = lines[i + j].strip().split('\t')
                packet_type = 1 if int(line[2]) == 0 else 0
                ping_id = int(line[3])
                seq_number = int(line[4])
                packet_sequence.append([packet_type, ping_id, seq_number])
            self.data.append(packet_sequence)
            self.labels.append(1)

        file = open(normal_filename, 'r')
        lines = file.readlines()
        file.close()

        for i in range(len(lines) - window_size):
            packet_sequence = []
            for j in range(window_size):
                line = lines[i + j].strip().split('\t')
                packet_type = 1 if int(line[2]) == 0 else 0
                ping_id = int(line[3])
                seq_number = int(line[4])
                packet_sequence.append([packet_type, ping_id, seq_number])
            self.data.append(packet_sequence)
            self.labels.append(0)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        packet_sequence = self.data[idx]
        label = self.labels[idx]
        return torch.tensor(packet_sequence, dtype=torch.float32), torch.tensor(label, dtype=torch.long)