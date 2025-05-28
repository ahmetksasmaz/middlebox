import torch
import torch.nn as nn

class CovertDetectorModel(nn.Module):
    def __init__(self, hidden_size, num_layers=1, window_size=50):
        super(CovertDetectorModel, self).__init__()
        self.window_size = window_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # RNN layer
        # input size is 3 (request/response, ping id, sequence number)
        self.rnn = nn.RNN(3, hidden_size, num_layers, batch_first=True)
        
        # Fully connected 
        # output size is 2 (covert channel detected or not)
        self.fc = nn.Linear(hidden_size, 2)
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, x):
        # x shape: (batch_size, window_size, input_features)

        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate RNN
        out, _ = self.rnn(x, h0)
        
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        out = self.softmax(out)
        
        return out
    
    def predict(self, x):
        with torch.no_grad():
            return self.forward(x)