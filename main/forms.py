import os

from django import forms
from django.core.exceptions import ValidationError
from PIL import Image

from .models import ChatbotConfig, CyberCrime

MODEL_CHOICES = [
    ('gemini-1.5-pro', 'Gemini 1.5 Pro'),
    ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
    ('gemini-2.0-pro', 'Gemini 2.0 Pro'),
    ('gemini-2.0-flash-lite', 'Gemini 2.0 Flash-Lite'),
    ('gemini-2.5-flash', 'Gemini 2.5 Flash'),
    ('gemini-2.5-pro', 'Gemini 2.5 Pro'),
    ('gemini-exp-1206', 'Gemini Experimental 1206'),
]

# ---------------------------------------------------------------------------
# Secure image validator
# ---------------------------------------------------------------------------

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


def validate_image_secure(file):
    """Validate uploaded image files for extension, MIME type, size, and integrity."""

    # --- Extension check ---
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError('Unsupported file extension')

    # --- MIME type check ---
    if hasattr(file, 'content_type') and file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError('Invalid file type')

    # --- File size check ---
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError('File too large (max 2MB)')

    # --- Actual image verification via Pillow ---
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception:
        raise ValidationError('Invalid or corrupted image')


# ---------------------------------------------------------------------------
# ChatbotConfigForm  (UNCHANGED)
# ---------------------------------------------------------------------------

class ChatbotConfigForm(forms.ModelForm):
    """Form for ChatbotConfig model"""
    
    class Meta:
        model = ChatbotConfig
        fields = ['gemini_model', 'system_prompt']
        widgets = {
            'gemini_model': forms.Select(attrs={
                'class': 'form-control'
            }, choices=MODEL_CHOICES),
            'system_prompt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter the system prompt for the AI assistant'
            })
        }


# ---------------------------------------------------------------------------
# CyberCrimeForm  (SECURED)
# ---------------------------------------------------------------------------

class CyberCrimeForm(forms.ModelForm):
    """Form for CyberCrime model with secure image validation"""

    banner_image = forms.ImageField(
        validators=[validate_image_secure],
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )
    
    # Field for multiple additional images
    additional_images_upload = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'multiple': True}),
        required=False,
        help_text="Upload multiple additional images (infographics, etc.)"
    )
    
    prevention_tips = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    reporting_steps = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def clean_additional_images_upload(self):
        if not self.files:
            return []
        if hasattr(self.files, 'getlist'):
            files = self.files.getlist('additional_images_upload')
        else:
            files = self.files.get('additional_images_upload', [])
            if not isinstance(files, list):
                files = [files] if files else []
        for file in files:
            validate_image_secure(file)
        return files


    class Meta:
        model = CyberCrime
        fields = [
            'type', 'description', 'category', 'severity',
            'banner_image', 'how_it_works', 'impact', 'solution',
            'prevention_tips', 'reporting_steps'
        ]
        widgets = {
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter crime type'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter crime description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prevention_tips': forms.HiddenInput(),
            'reporting_steps': forms.HiddenInput(),
        }

    def _parse_json_list(self, raw_value):
        import json
        if not raw_value:
            return []
        if isinstance(raw_value, list):
            return raw_value
        try:
            parsed = json.loads(raw_value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return [item.strip() for item in str(raw_value).split('\n') if item.strip()]

    def clean_prevention_tips(self):
        return self._parse_json_list(self.cleaned_data.get('prevention_tips'))

    def clean_reporting_steps(self):
        return self._parse_json_list(self.cleaned_data.get('reporting_steps'))

    def clean(self):
        """Centralized double-validation for all image fields and sanitization."""
        cleaned_data = super().clean()
        from .utils import sanitize_input
        
        # Sanitize all character and text fields
        for field_name, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field_name] = sanitize_input(value)
            elif isinstance(value, list):
                cleaned_data[field_name] = [sanitize_input(str(item)) for item in value if item]

        banner_image = cleaned_data.get('banner_image')
        if banner_image:
            validate_image_secure(banner_image)

        # We can't validate additional_images_upload here easily if it's multiple 
        # since it's not a single file, but in views we will validate them.
        
        return cleaned_data
