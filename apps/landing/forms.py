from django import forms

from . import content
from .models import Lead


class LeadForm(forms.ModelForm):
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

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if len(message) > 2000:
            raise forms.ValidationError('El mensaje no puede superar los 2000 caracteres.')
        return message
