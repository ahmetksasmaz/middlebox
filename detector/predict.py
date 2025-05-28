import torch
import torch.nn as nn
from model import CovertDetectorModel

def predict(model, data):
    with torch.no_grad():
        model.eval()
        data_tensor = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
        output = model.predict(data_tensor)
        _, predicted = torch.max(output, 1)
        return predicted.item()

def main(model_path, data_file):
    # Load the trained model
    file = open(data_file, 'r')
    lines = file.readlines()
    file.close()
    data = []
    for line in lines:
        packet_type, ping_id, seq_number = map(int, line.strip().split('\t'))
        data.append([packet_type, ping_id, seq_number])
    data = data[-50:]  # Use the last 50 packets as input
    data = [data]  # Wrap in a list to match batch size of 1
    model = torch.load(model_path, map_location=torch.device('cpu'))
    prediction = predict(model, data)
    if prediction == 1:
        print("Covert channel detected")
    else:
        print("No covert channel detected")
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python predict.py <model_path> <data_file>")
        sys.exit(1)
    model_path = sys.argv[1]
    data_file = sys.argv[2]
    main(model_path, data_file)