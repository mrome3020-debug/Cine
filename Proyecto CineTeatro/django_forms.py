from django import forms
from django.core.validators import FileExtensionValidator
import re
from DB import parsear_fechas_emision


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
    fechas_emision = forms.CharField(max_length=1000)
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

    def clean_fechas_emision(self):
        fechas = parsear_fechas_emision(self.cleaned_data['fechas_emision'])
        if not fechas:
            raise forms.ValidationError('Debes seleccionar al menos una fecha de emisión.')
        return fechas


class PeliculaCreateForm(PeliculaBaseForm):
    pass


class PeliculaEditForm(PeliculaBaseForm):
    id = forms.IntegerField(min_value=1)
    eliminar_portada = forms.BooleanField(required=False)
