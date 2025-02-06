let stream = null;

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(videoStream => {
            stream = videoStream;
            const video = document.getElementById('camera');
            video.srcObject = stream;
            video.hidden = false;
            video.addEventListener('click', takePhoto);
        })
        .catch(error => alert('Erreur d\'accès à la caméra: ' + error));
}

function takePhoto() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const preview = document.getElementById('preview');
    const imagePreview = document.getElementById('imagePreview');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    imagePreview.src = canvas.toDataURL('image/jpeg');
    video.hidden = true;
    preview.hidden = false;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

document.getElementById('fileInput').addEventListener('change', (e) => {
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

function validateImage() {
    const imagePreview = document.getElementById('imagePreview');
    const formData = new FormData();
    formData.append('image', imagePreview.src);

    fetch('/upload-image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/results';
        } else {
            alert('Erreur lors du traitement de l\'image');
        }
    })
    .catch(error => alert('Erreur: ' + error));
}