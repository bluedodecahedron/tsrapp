import torch
import argparse
import torch.nn as nn
import torch.optim as optim
import time

from tqdm.auto import tqdm

from tsrresnet.tools.model import build_model
from datasets import get_datasets, get_data_loaders
from utils import Saver

seed = 42
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = True

# Training function.
def train(
    model, trainloader, optimizer, 
    criterion, scheduler=None, epoch=None
):
    model.train()
    print('Training')
    train_running_loss = 0.0
    train_running_correct = 0
    counter = 0
    iters = len(trainloader)

    with tqdm(enumerate(trainloader), total=len(trainloader), position=0, leave=False) as pbar:
        for i, data in pbar:
            counter += 1
            image, labels = data
            image = image.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            # Forward pass.
            outputs = model(image)
            # Calculate the loss.
            loss = criterion(outputs, labels)
            train_running_loss += loss.item()
            # Calculate the accuracy.
            _, preds = torch.max(outputs.data, 1)
            _, labels = torch.max(labels, 1)
            train_running_correct += (preds == labels).sum().item()
            # Backpropagation.
            loss.backward()
            # Update the weights.
            optimizer.step()

            if scheduler is not None:
                scheduler.step(epoch + i / iters)

    # Loss and accuracy for the complete epoch.
    epoch_loss = train_running_loss / counter
    epoch_acc = 100. * (train_running_correct / len(trainloader.dataset))
    return epoch_loss, epoch_acc


# Validation function.
def validate(model, testloader, criterion, class_names):
    model.eval()
    print('Validation')
    valid_running_loss = 0.0
    valid_running_correct = 0
    counter = 0

    # We need two lists to keep track of class-wise accuracy.
    class_correct = list(0. for i in range(len(class_names)))
    class_total = list(0. for i in range(len(class_names)))

    with torch.no_grad():
        for i, data in tqdm(enumerate(testloader), total=len(testloader)):
            counter += 1
            
            image, labels = data
            image = image.to(device)
            labels = labels.to(device)
            # Forward pass.
            outputs = model(image)
            # Calculate the loss.
            loss = criterion(outputs, labels)
            valid_running_loss += loss.item()
            # Calculate the accuracy.
            _, preds = torch.max(outputs.data, 1)
            _, labels = torch.max(labels, 1)
            valid_running_correct += (preds == labels).sum().item()

            # Calculate the accuracy for each class.
            correct = (preds == labels).squeeze()
            for i in range(len(preds)):
                label = labels[i]
                class_correct[label] += correct[i].item()
                class_total[label] += 1
        
    # Loss and accuracy for the complete epoch.
    epoch_loss = valid_running_loss / counter
    epoch_acc = 100. * (valid_running_correct / len(testloader.dataset))

    # Print the accuracy for each class after every epoch.
    print('\n')
    for i in range(len(class_names)):
        print(f"Accuracy of class {class_names[i]}: {100*class_correct[i]/class_total[i]}")
    print('\n')
    return epoch_loss, epoch_acc


def train_hyper():
    # Load the model.
    model = build_model(
        pretrained=config['pretrained'],
        fine_tune=config['fine_tune'],
        dropout=config['dropout']
    ).to(device)

    # Total parameters and trainable parameters.
    total_params = sum(p.numel() for p in model.parameters())
    print(f"{total_params:,} total parameters.")
    total_trainable_params = sum(
        p.numel() for p in model.parameters() if p.requires_grad)
    print(f"{total_trainable_params:,} training parameters.")

    # Optimizer.
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config['learning_rate'],
        betas=(config['beta1'], config['beta2']),
        weight_decay=config['weight_decay']
    )
    # optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=weight_decay)

    # Loss function.
    criterion = nn.CrossEntropyLoss(label_smoothing=config['label_smoothing']).to(device)

    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer,
        T_0=config['restart_cycle'],
        T_mult=config['cycle_mult'],
        eta_min=config['lr_min']
    )

    # Lists to keep track of losses and accuracies.
    train_loss, valid_loss = [], []
    train_acc, valid_acc = [], []
    # Start the training.
    for epoch in range(config['epochs']):
        print(f"[INFO]: Epoch {epoch+1} of {config['epochs']}")
        train_epoch_loss, train_epoch_acc = train(
            model, train_loader,
            optimizer, criterion,
            scheduler=scheduler, epoch=epoch
        )
        valid_epoch_loss, valid_epoch_acc = validate(model, valid_loader,
                                                    criterion, dataset_classes)
        train_loss.append(train_epoch_loss)
        valid_loss.append(valid_epoch_loss)
        train_acc.append(train_epoch_acc)
        valid_acc.append(valid_epoch_acc)
        print(f"Training loss: {train_epoch_loss:.3f}, training acc: {train_epoch_acc:.3f}")
        print(f"Validation loss: {valid_epoch_loss:.3f}, validation acc: {valid_epoch_acc:.3f}")
        print('-'*50)
        time.sleep(5)
        # Save final model
        if epoch == config['epochs']-1:
            saver.save_model(epoch, model, optimizer, criterion, final=True)
        # Save model every x epochs
        elif epoch == 0 or (epoch+1) % config['restart_cycle'] == 0:
            saver.save_model(epoch, model, optimizer, criterion)
        # Save the loss and accuracy plots.
        saver.save_plots(train_acc, valid_acc, train_loss, valid_loss)
    print('TRAINING COMPLETE')


if __name__ == '__main__':
    # Load the training and validation datasets.
    dataset_train, dataset_valid, dataset_classes, aug_config = get_datasets()
    print(f"[INFO]: Number of training images: {len(dataset_train)}")
    print(f"[INFO]: Number of validation images: {len(dataset_valid)}")
    print(f"[INFO]: Class names: {dataset_classes}\n")
    # Load the training and validation data loaders.
    train_loader, valid_loader = get_data_loaders(dataset_train, dataset_valid)

    device = ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Computation device: {device}\n")

    config = {
        'pretrained': True,
        'fine_tune': True,
        'epochs': 100,
        'learning_rate': 0.0001,
        'beta1': 0.9,
        'beta2': 0.999,
        'weight_decay': 0.00025,
        'restart_cycle': 10,
        'cycle_mult': 1,
        'lr_min': 0.0,
        'dropout': 0.2,
        'label_smoothing': 0.05
    }

    print(f"Training with the following hyperparameters:")
    for key, value in config.items():
        print(f"{key}: {value}")

    saver = Saver()
    saver.save_parameters(config)
    saver.save_augmentations(aug_config)

    train_hyper()
