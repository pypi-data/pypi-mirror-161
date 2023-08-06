import pytest
from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from pytest_factoryboy import register
from rest_framework.fields import DateTimeField
from rest_framework.test import APIClient

from {{path_to_app}}.models import {{MainClass}}

fake = Faker()


