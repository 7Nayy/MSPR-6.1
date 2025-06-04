let stream = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM chargé");

    // Gestionnaire pour le bouton d'import
    const importButton = document.getElementById('importButton');
    const fileInput = document.getElementById('fileInput');

    if (importButton && fileInput) {
        importButton.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            console.log("Fichier sélectionné");
            const preview = document.getElementById('preview');
            const imagePreview = document.getElementById('imagePreview');
            const file = e.target.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    preview.hidden = false;
                };
                reader.readAsDataURL(file);
            }
        });
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
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    stream.getTracks().forEach(track => track.stop());

    document.querySelector('.scan-container').innerHTML = originalContent;

    const imagePreview = document.getElementById('imagePreview');
    const preview = document.getElementById('preview');
    imagePreview.src = canvas.toDataURL('image/jpeg');
    preview.hidden = false;
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
    const imagePreview = document.getElementById('imagePreview');

    if (!imagePreview || !imagePreview.src || imagePreview.src === '') {
        console.error("Aucune image à analyser");
        displayMessage("Aucune image à analyser", "error");
        return;
    }

    // Afficher un message de chargement pendant l'analyse
    displayMessage("Analyse de la trace en cours...", "info");

    const formData = new FormData();
    console.log("Image source:", imagePreview.src.substring(0, 100) + "..."); // Pour voir le début de l'image
    formData.append('image', imagePreview.src);

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
}