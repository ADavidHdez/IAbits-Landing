from django import forms

from apps.home import content as home_content

from . import content
from .models import Lead


class BaseLeadForm(forms.ModelForm):
    """Parte común de los formularios que crean un Lead (landing y contacto)."""

    # Honeypot: oculto vía CSS (.hp-field). La vista descarta en silencio los
    # envíos que lo traigan relleno, sin revelar al bot cuál es el campo trampa.
    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'hp-field',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
    )

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if len(message) > 2000:
            raise forms.ValidationError('El mensaje no puede superar los 2000 caracteres.')
        return message


class LeadForm(BaseLeadForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'company', 'service_interest', 'message']
        labels = {
            'name': 'Nombre',
            'email': 'Email',
            'company': 'Empresa',
            'message': 'Mensaje',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tu@empresa.com'}),
            'company': forms.TextInput(attrs={'placeholder': 'Nombre de tu empresa (opcional)'}),
            'message': forms.Textarea(attrs={
                'placeholder': '¿Qué proceso te gustaría automatizar?',
                'rows': 4,
                'maxlength': '2000',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Choices derivados de content.SERVICES: editar los servicios allí
        # actualiza el formulario sin migraciones.
        self.fields['service_interest'] = forms.ChoiceField(
            choices=content.service_choices(),
            required=False,
            label='Servicio de interés',
        )


class ContactForm(BaseLeadForm):
    """Formulario de la página de contacto de la home (/contacto/)."""

    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'company', 'product', 'contact_preference', 'message']
        labels = {
            'name': 'Nombre',
            'email': 'Email',
            'phone': 'Teléfono',
            'company': 'Empresa',
            'message': 'Mensaje',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tu@empresa.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000 (opcional)', 'type': 'tel'}),
            'company': forms.TextInput(attrs={'placeholder': 'Nombre de tu empresa (opcional)'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Cuéntanos qué necesitas',
                'rows': 4,
                'maxlength': '2000',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Oculto: lo fija el botón pulsado en la home (?producto=), no el
        # visitante. Se valida igual contra las opciones de apps/home/content.py,
        # así que un valor manipulado se rechaza.
        self.fields['product'] = forms.ChoiceField(
            choices=home_content.product_choices(),
            widget=forms.HiddenInput,
            error_messages={
                'required': home_content.CONTACT_FORM['invalid_request'],
                'invalid_choice': home_content.CONTACT_FORM['invalid_request'],
            },
        )
        self.fields['contact_preference'] = forms.ChoiceField(
            choices=home_content.CONTACT_PREFERENCES,
            required=False,
            label='¿Cómo prefieres que te contactemos?',
        )
