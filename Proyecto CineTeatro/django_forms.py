from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
import django
import re


if not settings.configured:
    settings.configure(
        USE_I18N=False,
        USE_TZ=False,
        SECRET_KEY='flask-django-compat-key',
    )

if not django.apps.apps.ready:
    django.setup()


class PeliculaBaseForm(forms.Form):
    CLASIFICACION_MPA_CHOICES = [
        ('G', 'G - Audiencias generales'),
        ('PG', 'PG - Guía parental sugerida'),
        ('PG-13', 'PG-13 - Menores de 13 con advertencia'),
        ('R', 'R - Restringida'),
        ('NC-17', 'NC-17 - Solo adultos'),
    ]

    nombre = forms.CharField(max_length=120)
    proveedor = forms.IntegerField(min_value=1)
    generos = forms.CharField(max_length=120)
    clasificacion = forms.ChoiceField(choices=CLASIFICACION_MPA_CHOICES)
    duracion = forms.CharField(max_length=5)
    descripcion = forms.CharField(max_length=1500)
    calificacion = forms.FloatField(min_value=0.0, max_value=10.0)
    fecha_estreno = forms.DateField(input_formats=['%Y-%m-%d'])
    portada = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif', 'webp'])],
    )

    def clean_duracion(self):
        duracion = self.cleaned_data['duracion'].strip()
        if not re.fullmatch(r"\d{1,2}:[0-5]\d", duracion):
            raise forms.ValidationError('La duración debe tener formato HH:MM, por ejemplo 02:15.')
        horas, minutos = duracion.split(':')
        return f"{int(horas):02d}:{minutos}"


class PeliculaCreateForm(PeliculaBaseForm):
    pass


class PeliculaEditForm(PeliculaBaseForm):
    id = forms.IntegerField(min_value=1)
    eliminar_portada = forms.BooleanField(required=False)
