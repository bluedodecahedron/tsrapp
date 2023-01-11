import torchvision.models as models
import torch.nn as nn

NUM_CLASSES = 44


def build_model(model='resnet18', pretrained=True, fine_tune=False, num_classes=NUM_CLASSES):
    if pretrained:
        print('[INFO]: Loading pre-trained weights')
    else:
        print('[INFO]: Not loading pre-trained weights')

    if model == 'resnet18':
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    elif model == 'resnet50':
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    elif model == 'mobilenet':
        model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)

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