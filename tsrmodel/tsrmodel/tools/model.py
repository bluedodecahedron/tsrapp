import torchvision.models as models
import torch.nn as nn
import torch.nn.functional as F

NUM_CLASSES = 58  # 58 55 or 44


def build_model(model='efficientnet_b0', pretrained=True, fine_tune=False, num_classes=NUM_CLASSES, dropout=0.2):
    if pretrained:
        print('[INFO]: Loading pre-trained weights')
    else:
        print('[INFO]: Not loading pre-trained weights')

    if model == 'resnet18':
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_features = model.fc.in_features
        model.fc = nn.Linear(in_features=num_features, out_features=num_classes)
    elif model == 'resnet50':
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        num_features = model.fc.in_features
        model.fc = nn.Linear(in_features=num_features, out_features=num_classes)
    elif model == 'efficientnet_b0':
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        model.classifier[1] = nn.Linear(in_features=1280, out_features=num_classes)
        model.classifier[0] = nn.Dropout(p=dropout, inplace=True)
    elif model == 'efficientnet_b1':
        model = models.efficientnet_b1(weights=models.EfficientNet_B1_Weights.IMAGENET1K_V2)
        model.classifier[1] = nn.Linear(in_features=1280, out_features=num_classes)
        model.classifier[0] = nn.Dropout(p=dropout, inplace=True)
    elif model == 'efficientnet_b4':
        model = models.efficientnet_b4(weights=models.EfficientNet_B4_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(in_features=1792, out_features=num_classes)
    elif model == 'efficientnet_v2':
        model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(in_features=1280, out_features=num_classes)
    elif model == 'mobilenet':
        model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
        model.classifier[3] = nn.Linear(in_features=1280, out_features=num_classes)

    model.features.register_forward_hook(lambda m, inp, out: F.dropout(out, p=0.5, training=m.training))

    if fine_tune:
        print('[INFO]: Fine-tuning all layers...')
        for params in model.parameters():
            params.requires_grad = True
    elif not fine_tune:
        print('[INFO]: Freezing hidden layers...')
        for params in model.parameters():
            params.requires_grad = False

    return model
