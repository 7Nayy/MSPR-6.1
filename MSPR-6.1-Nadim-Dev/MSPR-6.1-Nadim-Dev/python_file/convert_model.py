import torch
import torch.nn as nn
from torch.serialization import safe_globals
import os

# Importer toutes les classes possibles dont nous pourrions avoir besoin
from torch.nn.modules.conv import Conv2d
from torch.nn.modules.linear import Linear
from torch.nn.modules.activation import ReLU
from torch.nn.modules.pooling import MaxPool2d, AvgPool2d
from torch.nn.modules.batchnorm import BatchNorm2d
from torchvision.models.resnet import ResNet, Bottleneck, BasicBlock

try:
    # Chemin vers votre modèle
    model_path = 'animal_footprint_model.pth'

    print(f"Tentative de conversion du modèle : {model_path}")

    # Charger le modèle en mode non sécurisé
    model = torch.load(model_path, weights_only=False)

    print("Modèle chargé avec succès!")

    # Vérifier le type de modèle
    if isinstance(model, dict):
        print("Le modèle est un state_dict")
        state_dict = model
    elif hasattr(model, 'state_dict'):
        print("Le modèle est une instance de modèle")
        state_dict = model.state_dict()
    else:
        print(f"Type de modèle non reconnu: {type(model)}")
        raise ValueError("Format de modèle non supporté")

    # Enregistrer uniquement le state_dict
    safe_model_path = 'animal_footprint_model_safe.pth'
    torch.save(state_dict, safe_model_path)

    print(f"Modèle converti avec succès et enregistré sous: {safe_model_path}")

    # Vérifier que le modèle peut être rechargé
    try:
        print("Tentative de recharger le modèle converti...")
        reloaded_state_dict = torch.load(safe_model_path)
        print("Modèle rechargé avec succès!")
    except Exception as e:
        print(f"Erreur lors du rechargement: {e}")

except Exception as e:
    print(f"Erreur lors de la conversion: {e}")