import re
from datetime import datetime, date, timedelta
import string
import random
import logging

logger = logging.getLogger("my_logger")


def validate_username(username):
    if username is None or len(username) < 3:
        return "O nome de usuário deve ter pelo menos 3 caracteres."
    if not all(c.isalnum() or c.isspace() or c in "-_" for c in username):
        return "O nome de usuário deve conter apenas caracteres alfanuméricos, espaços, - e _."
    return None


def validate_birth_date(birth_date):
    if not isinstance(birth_date, date):
        return "Formato de data inválido."
    today = date.today()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    if birth_date >= today:
        return "Data de nascimento inválida. A data deve estar a frente da atual."
    if age < 18:
        return "O usuário deve ter pelo menos 18 anos."
    return None


def validate_email(email):
    if email is None or not re.match(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email
    ):
        return "Formato de e-mail inválido."
    return None


def validate_password(password):
    if password is None or len(password) < 8:
        return "A senha deve ter pelo menos 8 caracteres."
    if not re.search(r"\d", password):
        return "A senha deve conter pelo menos um número."
    if not re.search(r"[A-Z]", password):
        return "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"[a-z]", password):
        return "A senha deve conter pelo menos uma letra minúscula."
    return None


def validate_cpf(cpf):
    if cpf == "":
        return "O CPF não pode estar vazio."
    if len(cpf) != 11:
        return "CPF inválido. Deve ter 11 dígitos."
    if not re.match(r"^\d{11}$", cpf):
        return "CPF deve conter apenas números."


def validate_phone_number(phone_number):
    if phone_number is None or not re.match(r"^\+?1?\d{9,15}$", phone_number):
        return "Número de telefone inválido. Certifique-se de que tem entre 9 e 15 dígitos, incluindo o código do país, se aplicável."
    return None


def validate_social_name(social_name):
    if social_name is None or len(social_name) < 2:
        return "O nome social deve ter pelo menos 2 caracteres."
    return None


def validate_profile_picture(profile_picture):
    if isinstance(profile_picture, str) and profile_picture.startswith("http"):
        return None
    if not hasattr(profile_picture, "name") or not hasattr(profile_picture, "size"):
        return "Arquivo de imagem inválido."
    valid_extensions = ["jpg", "jpeg", "png", "gif"]
    if not any(profile_picture.name.lower().endswith(ext) for ext in valid_extensions):
        return "Imagem de perfil inválida. Formatos suportados: jpg, jpeg, png, gif."
    if profile_picture.size > 5 * 1024 * 1024:
        return "A imagem de perfil deve ter no máximo 5MB."
    return None


def validate_authenticated(authenticated):
    if authenticated not in [True, False]:
        return "Autenticado deve ser True ou False."
    return None


def validate_internal_images(internal_images):
    valid_extensions = ["jpg", "jpeg", "png", "gif"]
    for image in internal_images:
        if not hasattr(image, "name") or not hasattr(image, "size"):
            return "Arquivo de imagem inválido."
        if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
            return "Imagem interna inválida. Formatos suportados: jpg, jpeg, png, gif."
        if image.size > 5 * 1024 * 1024:
            return "A imagem interna deve ter no máximo 5MB."
    return None


def generate_random_filename(length=14):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def validate_room_count(room_count):
    if room_count is None:
        return "O número de quartos é obrigatório."
    if room_count < 1 or room_count > 20:
        return "O número de quartos deve estar entre 1 e 20."
    return None


def validate_bed_count(bed_count):
    if bed_count is None:
        return "O número de camas é obrigatório."
    if bed_count < 1 or bed_count > 20:
        return "O número de camas deve estar entre 1 e 20."
    return None


def validate_category(category):
    valid_categories = ["inn", "chalet", "apartment", "home", "room"]
    if category not in valid_categories:
        return f"A categoria deve ser uma das seguintes: {', '.join(valid_categories)}."
    return None


def validate_bathroom_count(bathroom_count):
    if bathroom_count is None:
        return "O número de banheiros é obrigatório."
    if bathroom_count < 1 or bathroom_count > 20:
        return "O número de banheiros deve estar entre 1 e 20."
    return None


def validate_guest_capacity(guest_capacity):
    if guest_capacity is None:
        return "A capacidade de hóspedes é obrigatória."
    if guest_capacity < 1 or guest_capacity > 20:
        return "A capacidade de hóspedes deve ser entre 1 e 20."
    return None


def validate_price_per_night(price_per_night):
    if price_per_night < 0:
        return "O preço por noite deve ser um valor positivo."
    return None


def validate_price(price):
    if price < 0:
        return "O preço deve ser um valor positivo."
    return None


def validate_main_cover_image(main_cover_image, internal_images):
    if main_cover_image and main_cover_image not in internal_images:
        return "A imagem da capa deve ser uma das imagens internas."
    return None


def validate_space_type(space_type):
    valid_space_types = ["full_space", "limited_space"]
    if space_type not in valid_space_types:
        return f"O tipo de espaço deve ser um dos seguintes: {', '.join(valid_space_types)}."
    return None


def validate_address(address):
    if not address or len(address) < 5:
        return "O endereço deve ter pelo menos 5 caracteres."
    return None


def validate_city(city):
    if not city or len(city) < 2:
        return "A cidade deve ter pelo menos 2 caracteres."
    return None


def validate_neighborhood(neighborhood):
    if not neighborhood or len(neighborhood) < 2:
        return "O bairro deve ter pelo menos 2 caracteres."
    return None


def validate_postal_code(postal_code):
    if not re.match(r"^\d{5}-?\d{3}$", postal_code):
        return "O código postal deve estar no formato 12345-678 ou 12345678."
    return None


def validate_price_per_night(price_per_night):
    if price_per_night is None or price_per_night < 0:
        return "O preço por noite deve ser um valor positivo."
    return None


def validate_boolean_field(field_value, field_name):
    if not isinstance(field_value, bool):
        return f"O campo {field_name} deve ser True ou False."
    return None


def validate_wifi(wifi):
    return validate_boolean_field(wifi, "wifi")


def validate_tv(tv):
    return validate_boolean_field(tv, "tv")


def validate_kitchen(kitchen):
    return validate_boolean_field(kitchen, "kitchen")


def validate_washing_machine(washing_machine):
    return validate_boolean_field(washing_machine, "washing_machine")


def validate_parking_included(parking_included):
    return validate_boolean_field(parking_included, "parking_included")


def validate_air_conditioning(air_conditioning):
    return validate_boolean_field(air_conditioning, "air_conditioning")


def validate_pool(pool):
    return validate_boolean_field(pool, "pool")


def validate_jacuzzi(jacuzzi):
    return validate_boolean_field(jacuzzi, "jacuzzi")


def validate_grill(grill):
    return validate_boolean_field(grill, "grill")


def validate_private_gym(private_gym):
    return validate_boolean_field(private_gym, "private_gym")


def validate_beach_access(beach_access):
    return validate_boolean_field(beach_access, "beach_access")


def validate_smoke_detector(smoke_detector):
    return validate_boolean_field(smoke_detector, "smoke_detector")


def validate_fire_extinguisher(fire_extinguisher):
    return validate_boolean_field(fire_extinguisher, "fire_extinguisher")


def validate_first_aid_kit(first_aid_kit):
    return validate_boolean_field(first_aid_kit, "first_aid_kit")


def validate_outdoor_camera(outdoor_camera):
    return validate_boolean_field(outdoor_camera, "outdoor_camera")


def validate_rating(rating):
    """Verifica se o rating está dentro do intervalo permitido."""
    if rating < 1 or rating > 5:
        return "O rating deve estar entre 1 e 5."
    return None


def validate_comment(comment):
    """Verifica se o campo comment não está vazio, tem pelo menos 100 caracteres e não ultrapassa 500 caracteres."""
    if not comment or comment.strip() == "":
        return "O campo comment é obrigatório e não pode ser vazio."
    if len(comment) <= 100:
        return "O campo comment deve ter pelo menos 100 caracteres."
    if len(comment) >= 500:
        return "O campo comment não pode ter mais de 500 caracteres."
    return None


def validate_check_in_date(check_in_date):
    """
    Valida a data de check-in:
    - Deve ser uma data válida no formato YYYY-MM-DD.
    - Deve ser a partir de amanhã (não hoje ou no passado).
    """
    if isinstance(check_in_date, date):
        check_in_date = check_in_date.strftime("%Y-%m-%d")

    try:
        date_obj = datetime.strptime(check_in_date, "%Y-%m-%d").date()
    except ValueError:
        return "Data de check-in inválida. Use o formato YYYY-MM-DD."

    if date_obj <= date.today():
        logger.info(f"Datas: {date_obj, date.today}")
        return "A data de check-in deve ser a partir de amanhã."

    return None


def validate_check_out_date(check_out_date, check_in_date):
    """
    Valida a data de check-out:
    - Deve ser uma data válida no formato YYYY-MM-DD.
    - Deve ser pelo menos um dia após a data de check-in.
    """
    if isinstance(check_out_date, date):
        check_out_date = check_out_date.strftime("%Y-%m-%d")

    try:
        check_out_date_obj = datetime.strptime(check_out_date, "%Y-%m-%d").date()
    except ValueError:
        return "A data de check-out deve ser uma data válida no formato YYYY-MM-DD."

    if check_out_date_obj <= check_in_date:
        return "A data de check-out deve ser pelo menos um dia após a data de check-in."

    return None


def validate_total_price(price):
    if price <= 0:
        return "O preço total deve ser maior que zero."
    return None


def validate_is_active(is_active):
    if not isinstance(is_active, bool):
        return "O campo 'is_active' deve ser True ou False."
    return None


def validate_discount(discount):
    if not isinstance(discount, bool):
        return "O campo 'discount' deve ser True ou False."
    return None
