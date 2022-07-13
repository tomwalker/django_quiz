# Generated by Django 2.2.24 on 2022-01-06 10:45

from django.db import migrations
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def forwards_func(apps, schema_editor):
    Answer = apps.get_model("multichoice", "Answer")
    AnswerTranslation = apps.get_model("multichoice", "AnswerTranslation")

    for object in Answer.objects.all():
        AnswerTranslation.objects.create(
            master_id=object.pk,
            language_code=settings.LANGUAGE_CODE,
            content=object._content,
        )


def backwards_func(apps, schema_editor):
    Answer = apps.get_model("multichoice", "Answer")
    AnswerTranslation = apps.get_model("multichoice", "AnswerTranslation")

    for object in Answer.objects.all():
        translation = _get_translation(object, AnswerTranslation)
        object._content = translation.content
        object.save()  # Note this only calls Model.save()


def _get_translation(object, MyModelTranslation):
    translations = MyModelTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [("multichoice", "0002_add_translation_model")]

    operations = [migrations.RunPython(forwards_func, backwards_func)]
