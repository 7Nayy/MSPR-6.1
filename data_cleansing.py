import os
import random
from tqdm import tqdm
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging
from collections import defaultdict
import pandas as pd
from supabase import create_client, Client

# URL de l'API Supabase et clé Service Role
supabase_url = "https://qmaywilajvnwvcnacfmu.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtYXl3aWxhanZud3ZjbmFjZm11Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc3MTQ0MjAsImV4cCI6MjA1MzI5MDQyMH0.s44JkNSwfCvEipUEo5ABI8ZfWPXuLOkHliDQcsK4-ug"

# Créer le client Supabase
supabase: Client = create_client(supabase_url, supabase_key)


# Configuration du logger pour enregistrer les erreurs
logging.basicConfig(filename="dataset_processing.log", level=logging.INFO)


def log_error(message):
    """
    Enregistre une erreur dans le fichier de log.
    """
    logging.error(message)


def process_single_image(file, input_path, split_dir, image_size, augment, num_augmented, split):
    """
    Traite une seule image : redimensionnement et augmentation (si applicable).
    """
    try:
        # Lecture de l'image
        image = cv2.imread(input_path)
        if image is None:
            log_error(f"Impossible de lire {input_path}. Ignoré.")
            return

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

    except Exception as e:
        log_error(f"Erreur lors du traitement de {file}: {e}")


def process_images_and_structure_dataset(input_dir, output_dir, image_size=(224, 224), augment=True, num_augmented=5,
                                         split_ratios=(0.7, 0.15, 0.15)):
    """
    Fonction principale qui:
    - Redimensionne les images à une taille uniforme
    - Structure le dataset en train/validation/test
    - Applique des augmentations sur les images d'entraînement
    """
    assert sum(split_ratios) == 1.0, "Les ratios doivent avoir une somme égale à 1.0"

    # Définition des chemins pour chaque ensemble de données
    train_dir = os.path.join(output_dir, "train")
    val_dir = os.path.join(output_dir, "validation")
    test_dir = os.path.join(output_dir, "test")

    # Création des dossiers train/validation/test au niveau racine (une seule fois)
    for dir_path in [train_dir, val_dir, test_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # Parcours de chaque classe (sous-dossier dans le dossier d'entrée)
    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_path):
            continue  # Ignore si ce n'est pas un dossier

        # Liste et mélange des images de la classe
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(images)

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
            # Chemin du sous-dossier pour la classe (sous train/validation/test)
            split_dir = os.path.join(output_dir, split, class_name)

            # Création du dossier pour la classe uniquement si nécessaire
            if not os.path.exists(split_dir):
                os.makedirs(split_dir)

            # Multithreading pour accélérer le traitement
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        process_single_image, file,
                        os.path.join(class_path, file), split_dir,
                        image_size, augment, num_augmented, split
                    )
                    for file in split_images
                ]
                for f in tqdm(futures, desc=f"{split.upper()} - {class_name}"):
                    f.result()  # Récupère les résultats pour détecter les erreurs éventuelles


def augment_image(image):
    """
    Applique plusieurs transformations aléatoires à une image.
    """
    angle = random.uniform(-30, 30)
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
    rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    scale = random.uniform(0.8, 1.2)
    zoomed = cv2.resize(rotated, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    if scale > 1:
        start_x = (zoomed.shape[1] - w) // 2
        start_y = (zoomed.shape[0] - h) // 2
        zoomed = zoomed[start_y:start_y + h, start_x:start_x + w]
    else:
        padded = np.zeros_like(image)
        start_x = (w - zoomed.shape[1]) // 2
        start_y = (h - zoomed.shape[0]) // 2
        padded[start_y:start_y + zoomed.shape[0], start_x:start_x + zoomed.shape[1]] = zoomed
        zoomed = padded

    if random.choice([True, False]):
        zoomed = cv2.flip(zoomed, 1)

    alpha = random.uniform(0.8, 1.2)
    beta = random.randint(-20, 20)
    final_image = cv2.convertScaleAbs(zoomed, alpha=alpha, beta=beta)

    return final_image


def generate_dataset_report(output_dir):
    """
    Génère un rapport sur la répartition des images dans les ensembles train/validation/test.
    """
    report = defaultdict(lambda: {"train": 0, "validation": 0, "test": 0})

    for split in ["train", "validation", "test"]:
        split_dir = os.path.join(output_dir, split)
        for class_name in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_name)
            if os.path.isdir(class_path):
                report[class_name][split] = len([
                    f for f in os.listdir(class_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                ])

    df = pd.DataFrame.from_dict(report, orient="index")
    df["total"] = df.sum(axis=1)
    print("\n=== Rapport sur le dataset ===\n")
    print(df)
    df.to_csv(os.path.join(output_dir, "dataset_report.csv"))


# Configuration des chemins
input_directory = "WildLens/Mammifères"
output_directory = "cleaned_images"

# Exécution du traitement
process_images_and_structure_dataset(input_directory, output_directory)
generate_dataset_report(output_directory)
