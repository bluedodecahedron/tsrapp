import os

import torch
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

matplotlib.style.use('ggplot')
matplotlib.use('TkAgg')

BASE_FOLDER = '../outputs/models'


class Saver:
    def __init__(self):
        time_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
        self.base_folder = f'{BASE_FOLDER}/{time_now}'

    def save_model(self, epochs, model, optimizer, criterion, final=False):
        """
        Function to save the trained model to disk.
        """
        folder = f'{self.base_folder}/epoch{epochs:03}'
        if final:
            folder = f'{folder}_final'
        os.makedirs(folder)
        torch.save({
                    'epoch': epochs,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': criterion,
                    }, f"{folder}/model.pth")

    def save_plots(self, train_acc, valid_acc, train_loss, valid_loss):
        """
        Function to save the loss and accuracy plots to disk.
        """
        # Accuracy plots.
        plt.figure(figsize=(10, 7))
        plt.plot(
            train_acc, color='green', linestyle='-',
            label='train accuracy'
        )
        plt.plot(
            valid_acc, color='blue', linestyle='-',
            label='validataion accuracy'
        )
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.savefig(f"{self.base_folder}/accuracy.png")

        # Loss plots.
        plt.figure(figsize=(10, 7))
        plt.plot(
            train_loss, color='orange', linestyle='-',
            label='train loss'
        )
        plt.plot(
            valid_loss, color='red', linestyle='-',
            label='validataion loss'
        )
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(f"{self.base_folder}/loss.png")