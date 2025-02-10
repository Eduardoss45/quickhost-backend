from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import serializers
from django.db import transaction
from urllib.parse import urlparse
from django.urls import reverse
from django.conf import settings
from datetime import datetime, date
from decimal import Decimal
from data import models
import os
import uuid
import logging


from .validation import (
    validate_birth_date,
    validate_phone_number,
    validate_username,
    validate_email,
    validate_social_name,
    validate_profile_picture,
    validate_cpf,
    validate_password,
    validate_room_count,
    validate_bed_count,
    validate_bathroom_count,
    validate_guest_capacity,
    validate_price_per_night,
    validate_price,
    validate_main_cover_image,
    validate_space_type,
    validate_address,
    validate_city,
    validate_category,
    validate_neighborhood,
    validate_postal_code,
    validate_wifi,
    validate_tv,
    validate_kitchen,
    validate_washing_machine,
    validate_parking_included,
    validate_air_conditioning,
    validate_pool,
    validate_jacuzzi,
    validate_grill,
    validate_private_gym,
    validate_beach_access,
    validate_smoke_detector,
    validate_fire_extinguisher,
    validate_first_aid_kit,
    validate_outdoor_camera,
    validate_rating,
    validate_comment,
    validate_check_in_date,
    validate_check_out_date,
    validate_total_price,
    validate_is_active,
    validate_discount,
)


User = get_user_model()
logger = logging.getLogger("my_logger")


def generate_new_filename(original_filename):
    """Gera um novo nome de arquivo para a imagem de perfil."""
    import uuid
    import os

    extension = os.path.splitext(original_filename)[1]
    new_filename = f"{uuid.uuid4().hex}{extension}"
    return new_filename


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de novos usuários."""

    class Meta:
        model = models.UserAccount
        fields = [
            "username",
            "email",
            "cpf",
            "birth_date",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        """Valida os campos do usuário."""
        errors = {}

        birth_date_error = validate_birth_date(attrs.get("birth_date"))
        if birth_date_error:
            errors["birth_date"] = birth_date_error

        username_error = validate_username(attrs.get("username"))
        if username_error:
            errors["username"] = username_error

        email_error = validate_email(attrs.get("email"))
        if email_error:
            errors["email"] = email_error

        cpf_error = validate_cpf(attrs.get("cpf"))
        if cpf_error:
            errors["cpf"] = cpf_error

        password_error = validate_password(attrs.get("password"))
        if password_error:
            errors["password"] = password_error

        if errors:
            logger.error(f"Erros de validação encontrados: {errors}")
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        """Cria e salva um novo usuário no banco de dados."""
        logger.debug("Iniciando a criação do usuário.")

        password = validated_data.pop("password", None)
        profile_picture = validated_data.pop("profile_picture", None)

        user = User.objects.create_user(**validated_data)
        user.is_active = True
        logger.info(
            f"Usuário '{user.username}' criado com sucesso. UUID: {user.id_user}"
        )

        if profile_picture:
            new_filename = generate_new_filename(profile_picture.name)
            user.profile_picture.save(
                os.path.join(str(user.id_user), new_filename),
                profile_picture,
                save=True,
            )

        if password:
            user.set_password(password)
            user.save()

        logger.debug(f"Usuário criado: {user}")
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de dados do usuário."""

    class Meta:
        model = models.UserAccount
        fields = [
            "id_user",
            "birth_date",
            "phone_number",
            "username",
            "email",
            "social_name",
            "profile_picture",
            "cpf",
            "registered_accommodations",
            "registered_accommodation_bookings",
            "password",
            "created_at",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}

    def validate(self, attrs):
        """Valida os campos do usuário para atualização."""
        errors = {}

        if "username" in attrs:
            username_error = validate_username(attrs.get("username"))
            if username_error:
                errors["username"] = username_error

        if "phone_number" in attrs:
            phone_number_error = validate_phone_number(attrs.get("phone_number"))
            if phone_number_error:
                errors["phone_number"] = phone_number_error

        if "social_name" in attrs:
            social_name_error = validate_social_name(attrs.get("social_name"))
            if social_name_error:
                errors["social_name"] = social_name_error

        if "profile_picture" in attrs:
            profile_picture_error = validate_profile_picture(
                attrs.get("profile_picture")
            )
            if profile_picture_error:
                errors["profile_picture"] = profile_picture_error

        if "cpf" in attrs:
            cpf_error = validate_cpf(attrs.get("cpf"))
            if cpf_error:
                errors["cpf"] = cpf_error

        if errors:
            logger.error(f"Erros de validação na atualização: {errors}")
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        """Atualiza os dados do usuário e retorna mensagem apropriada."""
        logger.debug(f"Iniciando a atualização do usuário: {instance.username}")

        fields_to_update = [
            "username",
            "cpf",
            "phone_number",
            "social_name",
            "password",
            "profile_picture",
        ]
        for field in fields_to_update:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if "profile_picture" in validated_data:
            profile_picture = validated_data["profile_picture"]

            if isinstance(profile_picture, str) and urlparse(profile_picture).scheme:
                instance.profile_picture = profile_picture
            elif isinstance(profile_picture, TemporaryUploadedFile):
                new_filename = generate_new_filename(profile_picture.name)
                instance.profile_picture.save(
                    os.path.join(str(instance.id_user), new_filename),
                    profile_picture,
                    save=True,
                )

        if "cpf" in validated_data:
            cpf = validated_data["cpf"]

        if "password" in validated_data:
            new_password = validated_data["password"]
            instance.set_password(new_password)

        try:
            instance.save()
        except serializers.ValidationError as e:
            logger.error(f"Erro de validação: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro ao salvar usuário: {e}")
            raise serializers.ValidationError("Erro ao atualizar os dados do usuário.")

        logger.info(f"Usuário '{instance.username}' atualizado com sucesso.")

        return {
            "message": "Os dados do usuário foram alterados com sucesso.",
            "data": {
                "username": instance.username,
                "phone_number": instance.phone_number,
                "social_name": instance.social_name,
                "cpf": instance.cpf,
                "profile_picture": (
                    instance.profile_picture.url if instance.profile_picture else None
                ),
                "password": instance.password,
            },
        }

    def handle_exception(self, exc):
        """Tratamento de exceções para retornar feedback adequado."""
        if isinstance(exc, serializers.ValidationError):
            return {"message": "Erro de validação", "errors": exc.detail}
        else:
            return {"message": "Erro desconhecido", "errors": str(exc)}


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer para obtenção de token JWT."""

    def validate(self, attrs):
        """Valida as credenciais e retorna tokens e dados do usuário."""
        logger.debug("Iniciando a validação do TokenObtainPairSerializer.")
        data = super().validate(attrs)
        user = self.user

        user.authenticated = True
        user.save()

        data["user"] = {
            "email": user.email,
            "id_user": user.id_user,
            "authenticated": user.authenticated,
        }

        logger.info(f"Validação bem-sucedida para o usuário: {user.email}.")
        return data

    def handle_error(self, error):
        """Método para lidar com erros e definir authenticated como false."""
        logger.error(f"Erro na validação do token: {error}.")
        user = self.user
        user.authenticated = False
        user.save()


class AccommodationSerializer(serializers.ModelSerializer):
    """Serializer para gerenciar dados de acomodações."""

    internal_images = serializers.ListField(
        child=serializers.ImageField(), allow_empty=True
    )

    class Meta:
        model = models.PropertyListing
        fields = [
            "id_accommodation",
            "creator",
            "discount",
            "final_price",
            "registered_user_bookings",
            "cleaning_fee",
            "consecutive_days_limit",
            "main_cover_image",
            "internal_images",
            "category",
            "room_count",
            "bed_count",
            "bathroom_count",
            "guest_capacity",
            "space_type",
            "address",
            "city",
            "neighborhood",
            "postal_code",
            "uf",
            "wifi",
            "tv",
            "kitchen",
            "washing_machine",
            "parking_included",
            "air_conditioning",
            "pool",
            "jacuzzi",
            "grill",
            "private_gym",
            "beach_access",
            "smoke_detector",
            "fire_extinguisher",
            "first_aid_kit",
            "outdoor_camera",
            "title",
            "description",
            "price_per_night",
            "price",
            "average_rating",
            "created_at",
            "is_active",
        ]

    def get_fields(self):
        """
        Modifica dinamicamente os campos obrigatórios dependendo do contexto.
        """
        fields = super().get_fields()

        if self.instance:
            fields["internal_images"].required = False
            fields["main_cover_image"].required = False
            fields["creator"].required = False
            fields["registered_user_bookings"].required = False
            fields["created_at"].required = False
            fields["id_accommodation"].required = False
            fields["average_rating"].required = False
            fields["final_price"].required = False
            fields["price"].required = False
            fields["title"].required = False
            fields["description"].required = False
        else:
            fields["id_accommodation"].required = False
            fields["creator"].required = True
            fields["discount"].required = False
            fields["final_price"].required = False
            fields["registered_user_bookings"].required = False
            fields["cleaning_fee"].required = True
            fields["consecutive_days_limit"].required = True
            fields["main_cover_image"].required = True
            fields["internal_images"].required = True
            fields["category"].required = True
            fields["room_count"].required = True
            fields["bed_count"].required = True
            fields["bathroom_count"].required = True
            fields["guest_capacity"].required = True
            fields["space_type"].required = True
            fields["address"].required = True
            fields["city"].required = True
            fields["neighborhood"].required = True
            fields["postal_code"].required = True
            fields["uf"].required = True
            fields["wifi"].required = True
            fields["tv"].required = True
            fields["kitchen"].required = True
            fields["washing_machine"].required = True
            fields["parking_included"].required = True
            fields["air_conditioning"].required = True
            fields["pool"].required = True
            fields["jacuzzi"].required = True
            fields["grill"].required = True
            fields["private_gym"].required = True
            fields["beach_access"].required = True
            fields["smoke_detector"].required = True
            fields["fire_extinguisher"].required = True
            fields["first_aid_kit"].required = True
            fields["outdoor_camera"].required = True
            fields["title"].required = True
            fields["description"].required = True
            fields["price_per_night"].required = True
            fields["price"].required = False
            fields["average_rating"].required = False
            fields["created_at"].required = False
            fields["is_active"].required = False

        return fields

    def validate(self, data):
        """
        Validações adicionais para garantir a consistência dos dados.
        """
        if self.instance is None:
            if "creator" not in data:
                raise serializers.ValidationError(
                    {"creator": "O campo 'creator' é obrigatório na criação."}
                )

        return data

    def create(self, validated_data):
        """Cria e salva uma nova acomodação no banco de dados."""
        logger.info("Iniciando a criação da acomodação.")
        try:
            internal_images = validated_data.pop("internal_images", [])
            main_cover_image = validated_data.pop("main_cover_image", None)
            user = validated_data.get("creator")

            consecutive_days_limit = validated_data.get("consecutive_days_limit", 0)
            if consecutive_days_limit <= 0:
                validated_data["consecutive_days_limit"] = -1

            price = validated_data.get("price_per_night", 0)
            validated_data["price"] = round(price, 2)
            price_per_night = validated_data.get("price_per_night", 0)
            price_per_night = Decimal(price_per_night)
            if price_per_night > 0:
                min_rate = Decimal("0.03")
                max_rate = Decimal("0.15")
                max_price_for_max_rate = Decimal("1000")
                if price_per_night <= max_price_for_max_rate:
                    rate = min_rate + (max_rate - min_rate) * (
                        price_per_night / max_price_for_max_rate
                    )
                else:
                    rate = max_rate
                price_per_night *= 1 - rate
            validated_data["price_per_night"] = round(price_per_night, 2)

            with transaction.atomic():

                registered_user_bookings_data = validated_data.pop(
                    "registered_user_bookings", None
                )

                accommodation = models.PropertyListing.objects.create(**validated_data)
                accommodation_uuid = accommodation.id_accommodation
                logger.info(f"Acomodação criada: {accommodation_uuid}")

                if registered_user_bookings_data:
                    accommodation.registered_user_bookings.set(
                        registered_user_bookings_data
                    )

                logger.info(
                    f"Usuários relacionados adicionados à acomodação {accommodation.id_accommodation}."
                )

                image_paths = []
                for image in internal_images:
                    if isinstance(image, TemporaryUploadedFile):
                        new_filename = f"{uuid.uuid4()}.jpg"
                        image_folder = f"property_images/{accommodation_uuid}/"
                        file_path = os.path.join(image_folder, new_filename)

                        logger.info(f"Salvando imagem {image.name} em {file_path}")
                        if default_storage.save(file_path, image):
                            image_paths.append("media/" + file_path)

                def set_main_cover_image(main_cover_image, image_paths, accommodation):
                    try:
                        main_cover_image = int(main_cover_image)
                    except (ValueError, TypeError):
                        logger.info("main_cover_image não definido ou inválido.")
                        return
                    if 0 <= main_cover_image < len(image_paths):
                        accommodation.main_cover_image = image_paths[main_cover_image]
                        logger.info(
                            f"Imagem de capa principal definida: {image_paths[main_cover_image]}"
                        )
                    else:
                        logger.info(
                            f"Índice inválido ({main_cover_image}) para main_cover_image. Deixando vazio."
                        )

                set_main_cover_image(main_cover_image, image_paths, accommodation)

                accommodation.internal_images = list(map(str, image_paths))
                accommodation.is_active = True
                accommodation.save()
                logger.info(f"URLs das imagens armazenadas: {image_paths}.")

                user.registered_accommodations.add(accommodation_uuid)
                user.save()
                logger.info(
                    f"Acomodação {accommodation_uuid} adicionada ao usuário {user.id_user}."
                )
                return accommodation
        except Exception as e:
            logger.error(f"Erro ao criar acomodação: {e}")
            raise

    def update(self, instance, validated_data):
        """
        Atualiza uma acomodação existente no banco de dados.
        Campos não fornecidos explicitamente no `validated_data` mantêm seus valores originais.
        """
        logger.info(
            f"Iniciando a atualização da acomodação {instance.id_accommodation}."
        )
        logger.info(validated_data)
        try:
            # Verificar se foi fornecida nova lista de imagens
            if "internal_images" in validated_data:
                internal_images = validated_data.get("internal_images", [])

                # Se nenhuma imagem for fornecida, remova as imagens existentes
                if not internal_images:
                    logger.info("Nenhuma imagem fornecida. Removendo imagens antigas.")
                    # Excluir as imagens anteriores
                    if instance.internal_images:
                        for image_path in instance.internal_images:
                            image_path = image_path.replace(
                                "media/", ""
                            )  # Remover prefixo 'media/'
                            if default_storage.exists(image_path):
                                default_storage.delete(image_path)
                                logger.info(f"Imagem {image_path} deletada.")

                    # Remover a pasta se estiver vazia
                    image_folder = os.path.join(
                        settings.MEDIA_ROOT,
                        f"property_images/{instance.id_accommodation}/",
                    )
                    if os.path.isdir(image_folder) and not os.listdir(image_folder):
                        os.rmdir(image_folder)
                        logger.info(f"Pasta {image_folder} deletada, pois está vazia.")

                    instance.internal_images.clear()  # Limpar a lista de imagens
                    validated_data["internal_images"] = []

                else:
                    # Caso contrário, processar as novas imagens
                    valid_images = [
                        img
                        for img in internal_images
                        if isinstance(
                            img, (TemporaryUploadedFile, InMemoryUploadedFile)
                        )
                    ]
                    if not valid_images:
                        logger.warning(
                            "Nenhuma imagem válida fornecida. Mantendo valores atuais."
                        )
                        validated_data["internal_images"] = instance.internal_images
                    else:
                        image_paths = list(instance.internal_images or [])
                        for image in valid_images:
                            new_filename = f"{uuid.uuid4()}.jpg"
                            image_folder = (
                                f"property_images/{instance.id_accommodation}/"
                            )
                            file_path = os.path.join(image_folder, new_filename)

                            logger.info(f"Salvando imagem {image.name} em {file_path}")
                            if default_storage.save(file_path, image):
                                image_paths.append("media/" + file_path)

                        validated_data["internal_images"] = image_paths

            # Atualização do campo 'main_cover_image'
            main_cover_image = validated_data.pop("main_cover_image", None)
            if main_cover_image is not None:
                try:
                    main_cover_image_index = int(main_cover_image)
                    if (
                        0
                        <= main_cover_image_index
                        < len(instance.internal_images or [])
                    ):
                        instance.main_cover_image = instance.internal_images[
                            main_cover_image_index
                        ]
                        logger.info(
                            f"Imagem de capa atualizada: {instance.main_cover_image}"
                        )
                    else:
                        logger.warning(
                            f"Índice inválido ({main_cover_image_index}) para imagem de capa. Mantendo existente."
                        )
                except (ValueError, TypeError):
                    logger.warning(
                        "main_cover_image não é um índice válido. Mantendo existente."
                    )

            # Processamento de preço
            if "price" in validated_data:
                price = validated_data.get("price", 0)
                if price > 0:
                    validated_data["price"] = round(price, 2)

            if "price_per_night" in validated_data:
                price_per_night = Decimal(validated_data["price_per_night"])
                if price_per_night > 0:
                    min_rate = Decimal("0.03")
                    max_rate = Decimal("0.15")
                    max_price_for_max_rate = Decimal("1000")
                    if price_per_night <= max_price_for_max_rate:
                        rate = min_rate + (max_rate - min_rate) * (
                            price_per_night / max_price_for_max_rate
                        )
                    else:
                        rate = max_rate
                    validated_data["price_per_night"] = round(
                        price_per_night * (1 - rate), 2
                    )

            # Preservação de outros campos
            fields_to_preserve = [
                "wifi",
                "tv",
                "price",
                "price_per_night",
                "kitchen",
                "washing_machine",
                "parking_included",
                "air_conditioning",
                "pool",
                "jacuzzi",
                "grill",
                "private_gym",
                "beach_access",
                "smoke_detector",
                "fire_extinguisher",
                "first_aid_kit",
                "outdoor_camera",
                "discount",
                "category",
                "space_type",
            ]
            for field in fields_to_preserve:
                if field not in validated_data:
                    validated_data[field] = getattr(instance, field)

            # Atualiza os outros campos
            for attr, value in validated_data.items():
                if getattr(instance, attr) != value:
                    setattr(instance, attr, value)

            instance.save()
            logger.info(
                f"Acomodação {instance.id_accommodation} atualizada com sucesso."
            )
            return instance

        except Exception as e:
            logger.error(
                f"Erro ao atualizar acomodação {instance.id_accommodation}: {e}"
            )
            raise


class ReviewSerializer(serializers.ModelSerializer):
    user_comment = serializers.UUIDField()
    accommodation = serializers.PrimaryKeyRelatedField(
        queryset=models.PropertyListing.objects.all()
    )
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    comment = serializers.CharField(validators=[validate_comment])

    class Meta:
        model = models.Review
        fields = [
            "id_review",
            "user_comment",
            "accommodation",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        """Valida os dados da review antes de salvar."""

        rating = attrs.get("rating")
        if rating is not None:
            rating_error = validate_rating(rating)
            if rating_error:
                raise serializers.ValidationError({"rating": rating_error})

        comment = attrs.get("comment")
        if comment:
            comment_error = validate_comment(comment)
            if comment_error:
                raise serializers.ValidationError({"comment": comment_error})

        user_uuid = attrs.get("user_comment")
        if user_uuid:
            try:
                user_comment = models.UserAccount.objects.get(id_user=user_uuid)
                attrs["user_comment"] = user_comment.id_user
            except models.UserAccount.DoesNotExist:
                raise serializers.ValidationError(
                    {"user_comment": "Usuário não encontrado."}
                )

        accommodation = attrs.get("accommodation")
        if accommodation:
            try:
                accommodation_obj = models.PropertyListing.objects.get(
                    id_accommodation=accommodation.id_accommodation
                )
                attrs["accommodation"] = accommodation_obj
            except models.PropertyListing.DoesNotExist:
                raise serializers.ValidationError(
                    {"accommodation": "Acomodação não encontrada."}
                )
        return attrs

    def create(self, validated_data):
        """Cria e salva uma nova review no banco de dados."""
        user = validated_data.get("user_comment")
        try:
            review = super().create(validated_data)
            return review
        except ValueError as ve:
            raise serializers.ValidationError(f"Erro de validação: {str(ve)}")
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar review: {str(e)}")

    def update(self, instance, validated_data):
        """Atualiza os dados de uma review existente."""
        try:
            review = super().update(instance, validated_data)
            return review
        except Exception as e:
            raise serializers.ValidationError("Erro ao atualizar review.")


class BookingSerializer(serializers.ModelSerializer):
    user_booking = serializers.PrimaryKeyRelatedField(
        queryset=models.UserAccount.objects.all()
    )
    accommodation = serializers.PrimaryKeyRelatedField(
        queryset=models.PropertyListing.objects.all()
    )

    class Meta:
        model = models.Booking
        fields = [
            "id_booking",
            "user_booking",
            "accommodation",
            "check_in_date",
            "check_out_date",
            "price",
            "is_active",
            "created_at",
        ]

    def calculate_total_price(self, check_in_date, check_out_date, price):
        if isinstance(check_in_date, str):
            check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        if isinstance(check_out_date, str):
            check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        if check_out_date <= check_in_date:
            raise serializers.ValidationError(
                "A data de check-out deve ser após a data de check-in."
            )
        days_difference = (check_out_date - check_in_date).days
        if days_difference < 1:
            raise serializers.ValidationError(
                "A quantidade de dias deve ser pelo menos 1."
            )
        if days_difference <= 3:
            tax_rate = Decimal("1.05")
        elif 4 <= days_difference <= 7:
            tax_rate = Decimal("1.10")
        else:
            tax_rate = Decimal("1.15")
        total_price = Decimal(price) * days_difference * tax_rate
        return total_price

    def create(self, validated_data):
        try:
            with transaction.atomic():

                user_booking = validated_data["user_booking"]
                accommodation = validated_data["accommodation"]
                check_in_date = validated_data["check_in_date"]
                check_out_date = validated_data["check_out_date"]
                price = validated_data["price"]

                total_price = self.calculate_total_price(
                    check_in_date, check_out_date, price
                )

                booking = models.Booking.objects.create(
                    user_booking=user_booking,
                    accommodation=accommodation,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    price=total_price,
                    is_active=validated_data.get("is_active", True),
                )

                accommodation.registered_user_bookings.add(booking)

                user_booking.registered_accommodation_bookings.add(booking)

                user_booking.registered_accommodations.add(accommodation)

                return booking

        except Exception as e:
            logger.error(f"Erro ao criar reserva: {e}")
            raise serializers.ValidationError(
                {"detail": f"Erro ao criar reserva: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():

                instance.check_in_date = validated_data.get(
                    "check_in_date", instance.check_in_date
                )
                instance.check_out_date = validated_data.get(
                    "check_out_date", instance.check_out_date
                )
                instance.price = validated_data.get("price", instance.price)
                instance.is_active = validated_data.get("is_active", instance.is_active)

                new_accommodation = validated_data.get(
                    "accommodation", instance.accommodation
                )
                new_user_booking = validated_data.get(
                    "user_booking", instance.user_booking
                )

                if new_accommodation != instance.accommodation:

                    instance.accommodation.registered_bookings.remove(instance)
                    instance.accommodation.registered_user_bookings.remove(instance)

                    new_accommodation.registered_bookings.add(instance)
                    new_accommodation.registered_user_bookings.add(instance)

                    instance.accommodation = new_accommodation

                if new_user_booking != instance.user_booking:

                    instance.user_booking.registered_accommodation_bookings.remove(
                        instance
                    )

                    new_user_booking.registered_accommodation_bookings.add(instance)

                    instance.user_booking = new_user_booking

                instance.save()

                new_accommodation.save()
                new_user_booking.save()

                return instance

        except Exception as e:
            logger.error(f"Erro ao atualizar reserva: {e}")
            raise serializers.ValidationError(
                {"detail": f"Erro ao atualizar reserva: {str(e)}"}
            )


class FavoritePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FavoriteProperty
        fields = [
            "id_favorite_property",
            "user_favorite_property",
            "accommodation",
            "created_at",
        ]
        read_only_fields = ["id_favorite_property", "created_at"]
