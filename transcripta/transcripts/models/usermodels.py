from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

# Extention of BaseUserManager to handle creation of Custom Users

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Bitte geben Sie eine E-Mail-Adresse an')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        
        #normalize passwords if created from form.cleaned_data
        if 'password1' in extra_fields and 'password2' in extra_fields:
            password = extra_fields.pop('password1')
            del extra_fields['password2']

        extra_fields.setdefault('email_confirmed', False)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Für Superuser muss is_staff=True gesetzt sein')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Für Superuser muss is_superuser=True gesetzt sein')

        return self._create_user(email, password, **extra_fields)


# Custom User model.

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('benutzername', unique=True, max_length=150, blank=False)
    first_name = models.CharField('vorname', max_length=150, blank=False)
    last_name = models.CharField('nachname', max_length=150, blank=False)
    email = models.EmailField(unique=True, max_length=255, blank=False)
    email_confirmed = models.BooleanField('email bestätigt', default=True, help_text='Hat der User die E-Mailadresse bestätigt?')
    is_staff = models.BooleanField('staff status', default=False, help_text='Kann sich der User in den Admin-Bereich einloggen?')
    is_active = models.BooleanField('active', default=True, help_text='Ist der User aktiv? False setzen, statt löschen.')
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    anonymous_publication = models.BooleanField('anonyme Publikation', default=False)


    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']