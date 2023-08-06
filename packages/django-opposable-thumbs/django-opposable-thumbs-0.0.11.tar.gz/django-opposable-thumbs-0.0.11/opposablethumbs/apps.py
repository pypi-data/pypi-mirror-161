import os

from django.apps import AppConfig
from django.conf import settings


class OpposableThumbsConfig(AppConfig):
    name = "opposablethumbs"

    def create_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def ready(self):
        if settings.OPPOSABLE_THUMBS:
            if settings.OPPOSABLE_THUMBS["INPUT_CACHE_DIR"]:
                self.create_folder(settings.OPPOSABLE_THUMBS["INPUT_CACHE_DIR"])
            if settings.OPPOSABLE_THUMBS["OUTPUT_CACHE_DIR"]:
                self.create_folder(settings.OPPOSABLE_THUMBS["OUTPUT_CACHE_DIR"])
