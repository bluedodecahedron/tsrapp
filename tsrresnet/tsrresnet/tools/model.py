import torchvision.models as models
import torch.nn as nn


def build_model(pretrained=True, fine_tune=False, num_classes=10):
    if pretrained:
        print('[INFO]: Loading pre-trained weights')
    else:
        print('[INFO]: Not loading pre-trained weights')
    # model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    # model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

    if fine_tune:
        print('[INFO]: Fine-tuning all layers...')
        for params in model.parameters():
            params.requires_grad = True
    elif not fine_tune:
        print('[INFO]: Freezing hidden layers...')
        for params in model.parameters():
            params.requires_grad = False

    # Change the final classification head.
    num_features = model.fc.in_features
    model.fc = nn.Linear(in_features=num_features, out_features=num_classes)
    # model.classifier[3] = nn.Linear(in_features=1280, out_features=num_classes)
    return model