# Import des bibliothèques nécessaires
import os  # Pour la gestion des chemins et dossiers
import random  # Pour le mélange aléatoire des données
import shutil  # Pour la copie de fichiers
from tqdm import tqdm  # Pour afficher une barre de progression
import cv2  # Pour le traitement d'images
import numpy as np  # Pour les opérations numériques


def process_images_and_structure_dataset(input_dir, output_dir, image_size=(224, 224), augment=True, num_augmented=5,
                                         split_ratios=(0.7, 0.15, 0.15)):
    """
    Fonction principale qui:
    - Redimensionne les images à une taille uniforme
    - Structure le dataset en train/validation/test
    - Applique des augmentations sur les images d'entraînement

    Paramètres:
    - input_dir: Dossier contenant les images d'origine (avec sous-dossiers par classe)
    - output_dir: Dossier de destination pour le dataset structuré
    - image_size: Taille cible des images (par défaut 224x224)
    - augment: Si True, applique des augmentations aux images d'entraînement
    - num_augmented: Nombre d'images augmentées à générer par image originale
    - split_ratios: Proportions pour train/validation/test (doit sommer à 1.0)
    """
    # Vérifie que les ratios somment bien à 1
    assert sum(split_ratios) == 1.0, "Les ratios doivent avoir une somme égale à 1.0"

    # Création des chemins pour chaque ensemble de données
    train_dir = os.path.join(output_dir, "train")
    val_dir = os.path.join(output_dir, "validation")
    test_dir = os.path.join(output_dir, "test")

    # Création des dossiers s'ils n'existent pas
    for dir_path in [train_dir, val_dir, test_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # Parcours de chaque classe (sous-dossier)
    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_path):
            continue  # Ignore si ce n'est pas un dossier

        # Liste et mélange des images de la classe
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(images)  # Mélange aléatoire

        # Calcul des indices pour la séparation train/validation/test
        n = len(images)
        train_idx = int(split_ratios[0] * n)
        val_idx = train_idx + int(split_ratios[1] * n)

        # Répartition des images dans les ensembles
        splits = {
            "train": images[:train_idx],
            "validation": images[train_idx:val_idx],
            "test": images[val_idx:]
        }

        # Traitement des images pour chaque ensemble
        for split, split_images in splits.items():
            # Création du dossier de destination pour la classe
            split_dir = os.path.join(output_dir, split, class_name)
            os.makedirs(split_dir, exist_ok=True)

            # Traitement de chaque image
            for file in tqdm(split_images, desc=f"{split.upper()} - {class_name}"):
                input_path = os.path.join(class_path, file)

                # Lecture de l'image
                image = cv2.imread(input_path)
                if image is None:
                    print(f"Impossible de lire {input_path}. Ignoré.")
                    continue

                # Redimensionnement de l'image
                resized_image = cv2.resize(image, image_size, interpolation=cv2.INTER_AREA)

                # Sauvegarde de l'image redimensionnée
                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(split_dir, f"{base_name}.jpg")
                cv2.imwrite(output_path, resized_image, [cv2.IMWRITE_JPEG_QUALITY, 95])

                # Application des augmentations si demandé (uniquement pour l'ensemble train)
                if augment and split == "train":
                    for i in range(num_augmented):
                        augmented_image = augment_image(resized_image)
                        augmented_path = os.path.join(split_dir, f"{base_name}_aug_{i}.jpg")
                        cv2.imwrite(augmented_path, augmented_image, [cv2.IMWRITE_JPEG_QUALITY, 95])


def augment_image(image):
    """
    Applique plusieurs transformations aléatoires à une image:
    - Rotation
    - Zoom
    - Miroir horizontal
    - Ajustement luminosité/contraste

    Paramètres:
    - image: Image source (format numpy array)
    Retourne:
    - Image augmentée
    """
    # Application d'une rotation aléatoire
    angle = random.uniform(-30, 30)  # Angle entre -30° et +30°
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
    rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    # Application d'un zoom aléatoire
    scale = random.uniform(0.8, 1.2)  # Zoom entre 80% et 120%
    zoomed = cv2.resize(rotated, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    # Gestion du redimensionnement après zoom
    if scale > 1:  # Si l'image est agrandie, on la coupe
        start_x = (zoomed.shape[1] - w) // 2
        start_y = (zoomed.shape[0] - h) // 2
        zoomed = zoomed[start_y:start_y + h, start_x:start_x + w]
    else:  # Si l'image est réduite, on complète avec du noir
        padded = np.zeros_like(image)
        start_x = (w - zoomed.shape[1]) // 2
        start_y = (h - zoomed.shape[0]) // 2
        padded[start_y:start_y + zoomed.shape[0], start_x:start_x + zoomed.shape[1]] = zoomed
        zoomed = padded

    # Application aléatoire d'un miroir horizontal
    if random.choice([True, False]):
        zoomed = cv2.flip(zoomed, 1)

    # Ajustement aléatoire de la luminosité et du contraste
    alpha = random.uniform(0.8, 1.2)  # Contraste
    beta = random.randint(-20, 20)  # Luminosité
    final_image = cv2.convertScaleAbs(zoomed, alpha=alpha, beta=beta)

    return final_image


# Configuration des chemins
input_directory = "WildLens/Mammifères"  # Dossier contenant les images sources
output_directory = "cleaned_images"  # Dossier de destination

# Exécution du traitement
process_images_and_structure_dataset(input_directory, output_directory)