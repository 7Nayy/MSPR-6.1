import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io
import os
from python_file.supabase_conn import supabase
import random
import hashlib


class FootprintRecognition:
    def __init__(self):
        """
        Initialiser le modèle de reconnaissance de traces sans dépendance au fichier .pth
        """
        self.class_names = self._load_class_names()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Définir les transformations d'image standard pour PyTorch
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        print("Modèle factice initialisé avec succès.")

    def _load_class_names(self):
        """
        Charger les noms des classes (animaux) que le modèle peut reconnaître
        Ces noms correspondent exactement aux espèces dans la BDD Supabase

        Returns:
            list: Liste des noms de classes
        """
        # Liste exacte des espèces dans la table Animaux
        return [
            "Renard",
            "Loup",
            "Raton laveur",
            "Lynx",
            "Ours",
            "Castor",
            "Chat",
            "Chien",
            "Coyote",
            "Ecureuil",
            "Lapin",
            "Puma",
            "Rat"
        ]

    def preprocess_image(self, image_bytes):
        """
        Prétraiter l'image pour qu'elle soit compatible avec le modèle

        Args:
            image_bytes (bytes): Image en format bytes

        Returns:
            torch.Tensor: Image prétraitée
        """
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_tensor = self.transform(img)
            img_tensor = img_tensor.unsqueeze(0)  # Ajouter dimension de batch
            return img_tensor.to(self.device)
        except Exception as e:
            print(f"Erreur lors du prétraitement de l'image: {e}")
            # Retourner un tenseur vide en cas d'erreur
            return torch.zeros((1, 3, 224, 224)).to(self.device)

    def predict(self, image_bytes):
        """
        Simuler une prédiction d'animal à partir de l'image de trace

        Args:
            image_bytes (bytes): Image de la trace

        Returns:
            dict: Résultat de la prédiction avec animal, confiance et info
        """
        try:
            # Générer un index basé sur le hash de l'image pour obtenir une prédiction stable
            hash_obj = hashlib.md5(image_bytes)
            hash_val = int(hash_obj.hexdigest(), 16)
            random.seed(hash_val)

            # Choisir un animal basé sur le hash
            predicted_class_index = hash_val % len(self.class_names)
            confidence = 0.7 + (hash_val % 300) / 1000  # Entre 0.7 et 1.0

            # Récupérer le nom de l'animal
            animal_name = self.class_names[predicted_class_index]

            # Récupérer les informations de l'animal depuis Supabase
            animal_info = self._get_animal_info(animal_name)

            return {
                "animal": animal_name,
                "confidence": confidence,
                "card_url": animal_info.get("Card", ""),
                "fun_fact": animal_info.get("Fun fact", "")
            }
        except Exception as e:
            print(f"Erreur lors de la prédiction: {e}")
            # En cas d'erreur, retourner une valeur par défaut
            return {
                "animal": "Renard",  # Animal par défaut
                "confidence": 0.7,
                "card_url": "",
                "fun_fact": "Impossible d'analyser cette trace, mais les renards sont connus pour leur intelligence et leur adaptabilité."
            }

    def _get_animal_info(self, animal_name):
        """
        Récupérer les informations de l'animal depuis Supabase

        Args:
            animal_name (str): Nom de l'animal

        Returns:
            dict: Informations de l'animal
        """
        try:
            print(f"Tentative de récupération des informations pour l'animal: {animal_name}")

            # Recherche exacte par nom d'espèce
            response = supabase.table("Animaux").select("*").eq("Espèce", animal_name).execute()

            if response.data and len(response.data) > 0:
                print(f"Animal trouvé dans la base de données: {response.data[0]['Espèce']}")
                return response.data[0]
            else:
                print(f"Animal '{animal_name}' non trouvé, utilisation d'un animal par défaut")

                # Récupérer n'importe quel animal comme fallback
                response = supabase.table("Animaux").select("*").limit(1).execute()
                if response.data and len(response.data) > 0:
                    return response.data[0]
                else:
                    return {
                        "Card": "",
                        "Fun fact": f"Le {animal_name} est un animal fascinant que l'on peut rencontrer dans nos forêts."
                    }
        except Exception as e:
            print(f"Erreur lors de la récupération des infos de l'animal: {e}")
            return {
                "Card": "",
                "Fun fact": f"Le {animal_name} est un animal fascinant que l'on peut rencontrer dans nos forêts."
            }


# Créer directement une instance globale, sans dépendre du chargement du modèle
footprint_model = FootprintRecognition()


def initialize_model(model_path=None):
    """
    Fonction fictive pour maintenir la compatibilité avec le reste du code
    Retourne simplement l'instance déjà créée

    Args:
        model_path (str, optional): Ignoré
    """
    return footprint_model
    # Le modèle est déjà initialisé, donc on ne fait rien ici
    print(f"L'initialisation du modèle a été ignorée, utilisation du modèle factice.")
    return footprint_model