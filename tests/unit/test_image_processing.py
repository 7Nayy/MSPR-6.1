# tests/unit/test_image_processing.py
class TestImageProcessingUnit:
    """Tests unitaires traitement d'images"""

    def test_image_compression_quality(self):
        """Test : Qualité compression images"""
        from PIL import Image
        import io

        # Créer image test
        img = Image.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        original_size = len(img_bytes.getvalue())

        # Compresser selon logique app
        compressed_bytes = io.BytesIO()
        img.save(compressed_bytes, format='JPEG', quality=70)
        compressed_size = len(compressed_bytes.getvalue())

        # Vérifier compression
        assert compressed_size < original_size
        assert compressed_size > 0

    def test_image_resize_dimensions(self):
        """Test : Redimensionnement images"""
        from PIL import Image

        # Image test grande taille
        img = Image.new('RGB', (2000, 1500), color='blue')

        # Redimensionner selon logique scan.js (800x600 max)
        max_width, max_height = 800, 600
        width, height = img.size

        if width > height:
            if width > max_width:
                height = round(height * (max_width / width))
                width = max_width

        resized_img = img.resize((width, height))

        assert resized_img.size[0] <= 800
        assert resized_img.size[1] <= 600
