import torch
from torch.utils.data import Dataset
from dataset import CovertDetectorDataset
from model import CovertDetectorModel
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn as nn

def test_model(model, test_loader):
    correct = 0
    total = 0
    with torch.no_grad():
        model.eval()
        for _, (inputs, labels) in enumerate(test_loader):
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f'Accuracy: {100 * correct / total:.2f}%')

def train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs=10):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            if (i + 1) % 100 == 0:  # Print every 100 batches
                print(f'Epoch [{epoch + 1}/{num_epochs}], Step [{i + 1}/{len(train_loader)}], Loss: {running_loss / 100:.4f}')
                running_loss = 0.0
        test_model(model, test_loader)
        torch.save(model.state_dict(), f'covert_detector_epoch_{epoch + 1}.pth')
        print(f'Epoch [{epoch + 1}/{num_epochs}] completed and saved')

    print('Training complete')

def main():
    # Hyperparameters
    window_size = 32
    hidden_size = 32
    num_layers = 1
    batch_size = 32
    num_epochs = 10
    learning_rate = 0.001

    # Load dataset
    train_dataset = CovertDetectorDataset('dataset/covert_ping_dataset_train.txt', 'dataset/normal_ping_dataset_train.txt', window_size=window_size)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    test_dataset = CovertDetectorDataset('dataset/covert_ping_dataset_test.txt', 'dataset/normal_ping_dataset_test.txt', window_size=window_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    # Initialize model, loss function and optimizer
    model = CovertDetectorModel(hidden_size=hidden_size, num_layers=num_layers, window_size=window_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Train the model
    train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs)

if __name__ == '__main__':
    main()