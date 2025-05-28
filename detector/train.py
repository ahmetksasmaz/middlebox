import torch
from torch.utils.data import Dataset
from dataset import CovertDetectorDataset
from model import CovertDetectorModel
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn as nn
import argparse
import os

def test_model(model, test_loader, prefix):
    correct = 0
    total = 0
    with torch.no_grad():
        model.eval()
        for _, (inputs, labels) in enumerate(test_loader):
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f'{prefix} : %{100 * correct / total:.2f}')
    file = open(f'results/{prefix}_covert_detector_test.txt', 'a+')
    file.write(f'{correct / total}\n')
    file.close()

def train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs, prefix):
    model.train()
    for epoch in range(num_epochs):
        for i, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        test_model(model, test_loader, prefix)
        torch.save(model.state_dict(), f'models/{prefix}_covert_detector_{epoch + 1}.pth')
        print(f'Epoch [{epoch + 1}/{num_epochs}] completed and saved')

    print('Training complete')

def main(window_size, hidden_size, num_layers, num_epochs, batch_size, learning_rate):
    # Load dataset
    train_dataset = CovertDetectorDataset('dataset/covert_ping_dataset_train.txt', 'dataset/normal_ping_dataset_train.txt', window_size=window_size)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    test_dataset = CovertDetectorDataset('dataset/covert_ping_dataset_test.txt', 'dataset/normal_ping_dataset_test.txt', window_size=window_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    # Initialize model, loss function and optimizer
    model = CovertDetectorModel(hidden_size=hidden_size, num_layers=num_layers, window_size=window_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    prefix = str(hidden_size) + '_' + str(num_layers) + '_' + str(window_size) + '_' + str(num_epochs) + '_' + str(batch_size) + '_' + str(learning_rate)

    # Train the model
    train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs, prefix)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Train a covert ping detector model')
    argparser.add_argument('--window_size', type=int, default=32, required=True, help='Size of the sliding window for packet sequences')
    argparser.add_argument('--hidden_size', type=int, default=32, required=True, help='Size of the hidden layer in the LSTM')
    argparser.add_argument('--num_layers', type=int, default=1, required=True, help='Number of LSTM layers')
    argparser.add_argument('--num_epochs', type=int, default=5, required=False, help='Number of training epochs')
    argparser.add_argument('--batch_size', type=int, default=32, required=False, help='Batch size for training')
    argparser.add_argument('--learning_rate', type=float, default=0.001, required=False, help='Learning rate for the optimizer')

    args = argparser.parse_args()

    window_size = args.window_size
    hidden_size = args.hidden_size
    num_layers = args.num_layers
    num_epochs = args.num_epochs
    batch_size = args.batch_size
    learning_rate = args.learning_rate
    main(window_size, hidden_size, num_layers, num_epochs, batch_size, learning_rate)