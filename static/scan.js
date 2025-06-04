let stream = null;
let selectedFile = null; // Variable pour stocker le fichier sélectionné

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM chargé");

    // Gestionnaire pour le bouton d'import
    const importButton = document.getElementById('importButton');
    const fileInput = document.getElementById('fileInput');

    if (importButton && fileInput) {
        importButton.addEventListener('click', () => {
            fileInput.click();
        });

        // Ajoutez ces fonctions au début du fichier scan.js
        
        // Fonction pour annoncer les messages aux lecteurs d'écran
        function announceToScreenReader(message) {
            const announcer = document.createElement('div');
            announcer.setAttribute('aria-live', 'assertive');
            announcer.setAttribute('role', 'status');
            announcer.className = 'sr-only'; // Classe pour cacher visuellement mais garder accessible
            announcer.textContent = message;
            document.body.appendChild(announcer);
            
            // Supprimer après lecture (environ 3 secondes)
            setTimeout(() => {
                document.body.removeChild(announcer);
            }, 3000);
        }
        
        // Ajouter cette classe dans le CSS
        // .sr-only {
        //     position: absolute;
        //     width: 1px;
        //     height: 1px;
        //     padding: 0;
        //     margin: -1px;
        //     overflow: hidden;
        //     clip: rect(0, 0, 0, 0);
        //     white-space: nowrap;
        //     border: 0;
        // }
        
        // Modifiez les gestionnaires d'événements existants pour inclure des annonces
        
        // Dans le gestionnaire de changement de fichier
        fileInput.addEventListener('change', (e) => {
            console.log("Fichier sélectionné");
            const preview = document.getElementById('preview');
            const fileNameElement = document.getElementById('fileName');
            const file = e.target.files[0];
        
            if (file) {
                // Stocker le fichier
                selectedFile = file;
        
                // Afficher le nom du fichier
                fileNameElement.textContent = file.name;
                preview.hidden = false;
        
                // Annoncer aux lecteurs d'écran
                announceToScreenReader(`Fichier ${file.name} sélectionné. Utilisez le bouton Valider pour continuer.`);
                
                // Mettre le focus sur le bouton de validation
                setTimeout(() => {
                    document.getElementById('validateButton').focus();
                }, 100);
            }
        });
        
        // Dans la fonction takePhoto
        function takePhoto(originalContent) {
            if (!stream) return;
        
            const video = document.getElementById('camera-preview');
            const canvas = document.createElement('canvas');
        
            // Réduire la taille de l'image capturée pour économiser la bande passante
            const maxWidth = 800;
            const maxHeight = 600;
            let width = video.videoWidth;
            let height = video.videoHeight;
        
            if (width > height) {
                if (width > maxWidth) {
                    height = Math.round(height * (maxWidth / width));
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width = Math.round(width * (maxHeight / height));
                    height = maxHeight;
                }
            }
        
            canvas.width = width;
            canvas.height = height;
            canvas.getContext('2d').drawImage(video, 0, 0, width, height);
        
            stream.getTracks().forEach(track => track.stop());
        
            document.querySelector('.scan-container').innerHTML = originalContent;
        
            // Convertir en Blob pour upload
            canvas.toBlob(blob => {
                selectedFile = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
        
                // Afficher la confirmation de capture
                const preview = document.getElementById('preview');
                const fileNameElement = document.getElementById('fileName');
                fileNameElement.textContent = "Photo capturée";
                preview.hidden = false;
            }, 'image/jpeg', 0.7); // Compression à 70% pour réduire la taille
        }
        
        // Dans la fonction validateImage
        function validateImage() {
            console.log("Début de validateImage");
        
            if (!selectedFile) {
                console.error("Aucune image à analyser");
                displayMessage("Aucune image à analyser", "error");
                return;
            }
        
            // Afficher un message de chargement pendant l'analyse
            displayMessage("Analyse de la trace en cours...", "info");
        
            // Utilisation de FormData pour un envoi plus efficace
            const formData = new FormData();
        
            // Compresser l'image si elle vient d'un fichier
            compressImage(selectedFile, function(compressedBlob) {
                // Créer un nouveau fichier avec le blob compressé
                const compressedFile = new File([compressedBlob], selectedFile.name, {
                    type: 'image/jpeg',
                    lastModified: new Date().getTime()
                });
        
                formData.append('image', compressedFile);
        
                console.log("Envoi de la requête au serveur");
                fetch('/upload-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    console.log("Réponse reçue", response);
                    return response.json();
                })
                .then(data => {
                    console.log("Données reçues:", data);
                    if (data.success) {
                        console.log("Upload réussi");
        
                        // Vérifier s'il y a une redirection vers la page de résultats d'analyse
                        if (data.redirect) {
                            console.log("Redirection vers:", data.redirect);
                            window.location.href = data.redirect;
                        } else {
                            // Si pas de redirection, afficher un message de succès
                            displayMessage("Image enregistrée avec succès", "success");
                            window.location.href = '/scan';
                        }
                    } else {
                        console.error("Erreur:", data.error);
                        displayMessage('Erreur: ' + data.error, "error");
                    }
                })
                .catch(error => {
                    console.error("Erreur fetch:", error);
                    displayMessage('Erreur de connexion', "error");
                });
            });
        }
        
        // Avant l'envoi
        announceToScreenReader("Envoi de l'image en cours. Veuillez patienter...");
        
        function compressImage(file, callback) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = new Image();
                img.onload = function() {
                    // Calculer les dimensions maximales
                    const maxWidth = 800;
                    const maxHeight = 600;
                    let width = img.width;
                    let height = img.height;
        
                    // Redimensionner si nécessaire
                    if (width > height) {
                        if (width > maxWidth) {
                            height = Math.round(height * (maxWidth / width));
                            width = maxWidth;
                        }
                    } else {
                        if (height > maxHeight) {
                            width = Math.round(width * (maxHeight / height));
                            height = maxHeight;
                        }
                    }
        
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
        
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
        
                    // Convertir en Blob avec une qualité réduite
                    canvas.toBlob(callback, 'image/jpeg', 0.7);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    // Gestionnaire pour le bouton photo
    const photoButton = document.getElementById('photoButton');
    if (photoButton) {
        photoButton.addEventListener('click', startCamera);
    }

    // Gestionnaire pour le bouton de validation
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'validateButton') {
            console.log("Bouton de validation cliqué");
            validateImage();
        }
    });
});

function startCamera() {
    console.log("Démarrage caméra");

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Votre navigateur ne supporte pas l'accès à la caméra");
        return;
    }

    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: 'environment'
        }
    })
    .then(videoStream => {
        console.log("Flux vidéo obtenu");
        stream = videoStream;

        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.id = 'camera-preview';

        const container = document.querySelector('.scan-container');
        const originalContent = container.innerHTML;
        container.innerHTML = '';
        container.appendChild(video);

        const captureBtn = document.createElement('button');
        captureBtn.textContent = 'CAPTURER';
        captureBtn.className = 'connexion';
        captureBtn.onclick = () => takePhoto(originalContent);
        container.appendChild(captureBtn);
    })
    .catch(error => {
        console.error("Erreur caméra:", error);
        alert("Erreur d'accès à la caméra : " + error.message);
    });
}

function takePhoto(originalContent) {
    if (!stream) return;

    const video = document.getElementById('camera-preview');
    const canvas = document.createElement('canvas');

    // Réduire la taille de l'image capturée pour économiser la bande passante
    const maxWidth = 800;
    const maxHeight = 600;
    let width = video.videoWidth;
    let height = video.videoHeight;

    if (width > height) {
        if (width > maxWidth) {
            height = Math.round(height * (maxWidth / width));
            width = maxWidth;
        }
    } else {
        if (height > maxHeight) {
            width = Math.round(width * (maxHeight / height));
            height = maxHeight;
        }
    }

    canvas.width = width;
    canvas.height = height;
    canvas.getContext('2d').drawImage(video, 0, 0, width, height);

    stream.getTracks().forEach(track => track.stop());

    document.querySelector('.scan-container').innerHTML = originalContent;

    // Convertir en Blob pour upload
    canvas.toBlob(blob => {
        selectedFile = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });

        // Afficher la confirmation de capture
        const preview = document.getElementById('preview');
        const fileNameElement = document.getElementById('fileName');
        fileNameElement.textContent = "Photo capturée";
        preview.hidden = false;
    }, 'image/jpeg', 0.7); // Compression à 70% pour réduire la taille
}

function displayMessage(message, type) {
    // Créer ou récupérer l'élément pour le message
    let messageEl = document.getElementById('status-message');
    if (!messageEl) {
        messageEl = document.createElement('div');
        messageEl.id = 'status-message';
        document.querySelector('.scan-container').appendChild(messageEl);
    }

    // Appliquer le style en fonction du type de message
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;

    // Faire disparaître le message après 3 secondes si ce n'est pas un message d'info
    if (type !== 'info') {
        setTimeout(() => {
            messageEl.style.opacity = '0';
            setTimeout(() => {
                messageEl.remove();
            }, 500);
        }, 3000);
    }
}

function validateImage() {
    console.log("Début de validateImage");

    if (!selectedFile) {
        console.error("Aucune image à analyser");
        displayMessage("Aucune image à analyser", "error");
        return;
    }

    // Afficher un message de chargement pendant l'analyse
    displayMessage("Analyse de la trace en cours...", "info");

    // Utilisation de FormData pour un envoi plus efficace
    const formData = new FormData();

    // Compresser l'image si elle vient d'un fichier
    compressImage(selectedFile, function(compressedBlob) {
        // Créer un nouveau fichier avec le blob compressé
        const compressedFile = new File([compressedBlob], selectedFile.name, {
            type: 'image/jpeg',
            lastModified: new Date().getTime()
        });

        formData.append('image', compressedFile);

        console.log("Envoi de la requête au serveur");
        fetch('/upload-image', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log("Réponse reçue", response);
            return response.json();
        })
        .then(data => {
            console.log("Données reçues:", data);
            if (data.success) {
                console.log("Upload réussi");

                // Vérifier s'il y a une redirection vers la page de résultats d'analyse
                if (data.redirect) {
                    console.log("Redirection vers:", data.redirect);
                    window.location.href = data.redirect;
                } else {
                    // Si pas de redirection, afficher un message de succès
                    displayMessage("Image enregistrée avec succès", "success");
                    window.location.href = '/scan';
                }
            } else {
                console.error("Erreur:", data.error);
                displayMessage('Erreur: ' + data.error, "error");
            }
        })
        .catch(error => {
            console.error("Erreur fetch:", error);
            displayMessage('Erreur de connexion', "error");
        });
    });
}

function compressImage(file, callback) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const img = new Image();
        img.onload = function() {
            // Calculer les dimensions maximales
            const maxWidth = 800;
            const maxHeight = 600;
            let width = img.width;
            let height = img.height;

            // Redimensionner si nécessaire
            if (width > height) {
                if (width > maxWidth) {
                    height = Math.round(height * (maxWidth / width));
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width = Math.round(width * (maxHeight / height));
                    height = maxHeight;
                }
            }

            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            // Convertir en Blob avec une qualité réduite
            canvas.toBlob(callback, 'image/jpeg', 0.7);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}