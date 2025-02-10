from django.core.exceptions import ValidationError


def validate_room_count(value):
    if value <= 0 or value >= 21:
        raise ValidationError("O número de quartos deve estar entre 1 e 20.")


def validate_bed_count(value):
    if value <= 0 or value >= 21:
        raise ValidationError("O número de camas deve estar entre 1 e 20.")


def validate_bathroom_count(value):
    if value <= 0 or value >= 21:
        raise ValidationError("O número de banheiros deve estar entre 1 e 20.")


def validate_guest_capacity(value):
    if value <= 0 or value >= 21:
        raise ValidationError("A capacidade de hóspedes deve estar entre 1 e 20.")
