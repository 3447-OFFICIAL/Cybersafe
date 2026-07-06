import os
import sys
import shutil
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import CyberCrime, CyberCrimeImage
from django.conf import settings

# Paths
brain_dir = r"C:\Users\ukpal\.gemini\antigravity-ide\brain\55695f89-6105-4112-b326-d60bf2453311"
img1 = os.path.join(brain_dir, "media__1783071497554.jpg")
img2 = os.path.join(brain_dir, "media__1783071497555.jpg")
img3 = os.path.join(brain_dir, "media__1783071497557.jpg")

# Target Paths
banners_dir = os.path.join(settings.MEDIA_ROOT, 'crime_banners')
images_dir = os.path.join(settings.MEDIA_ROOT, 'crime_images')

os.makedirs(banners_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# Find Online Sextortion crime
try:
    crime = CyberCrime.objects.get(type="Online Sextortion")
except CyberCrime.DoesNotExist:
    crime = CyberCrime.objects.filter(category="online_sextortion").first()

if crime:
    # 1. Update banner
    banner_dest_name = f"{crime.id}_user_banner.jpg"
    banner_dest_path = os.path.join(banners_dir, banner_dest_name)
    shutil.copy(img1, banner_dest_path)
    crime.banner_image = f"crime_banners/{banner_dest_name}"
    crime.save()
    print(f"Updated banner for {crime.type}")

    # 2. Update additional images
    # Delete existing ones
    crime.additional_images.all().delete()

    # Copy and create new ones
    extras = [img2, img3]
    for idx, extra_src in enumerate(extras):
        extra_dest_name = f"{crime.id}_user_extra_{idx}.jpg"
        extra_dest_path = os.path.join(images_dir, extra_dest_name)
        shutil.copy(extra_src, extra_dest_path)

        CyberCrimeImage.objects.create(
            crime=crime,
            image=f"crime_images/{extra_dest_name}",
            caption=f"Evidence Analysis Visual {idx + 1}"
        )
        print(f"Created additional image {idx + 1}")
else:
    print("Online Sextortion crime not found!")
