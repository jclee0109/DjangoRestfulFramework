import string
import random
from typing import Dict

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
from shortener.model_utlis import dict_slice, dict_filter


class TimeStampedModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PayPlan(TimeStampedModel):
    name = models.CharField(max_length=20)
    price = models.IntegerField()


class Organization(TimeStampedModel):
    class Industries(models.TextChoices):
        PERSONAL = "personal"
        RETAIL = "retail"
        MANUFACTURING = "manufacturing"
        IT = "it"
        OTHERS = "others"

    name = models.CharField(max_length=50)
    industry = models.CharField(max_length=15, choices=Industries.choices, default=Industries.OTHERS)
    pay_plan = models.ForeignKey(PayPlan, on_delete=models.DO_NOTHING, null=True)


class Users(AbstractUser):
    full_name = models.CharField(max_length=100, null=True)
    url_count = models.IntegerField(default=0)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True)


class EmailVerification(TimeStampedModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    key = models.CharField(max_length=100, null=True)
    verified = models.BooleanField(default=False)


class Categories(TimeStampedModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE)


class ShortenedUrls(TimeStampedModel):
    class UrlCreatedVia(models.TextChoices):
        WEBSITE = "web"
        TELEGRAM = "telegram"

    def rand_string():
        str_pool = string.digits + string.ascii_letters
        return ("".join([random.choice(str_pool) for _ in range(6)])).lower()

    def rand_letter():
        str_pool = string.ascii_letters
        return random.choice(str_pool).lower()

    nick_name = models.CharField(max_length=100)
    category = models.ForeignKey(Categories, on_delete=models.DO_NOTHING, null=True)
    prefix = models.CharField(max_length=50, default=rand_letter)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE)
    target_url = models.CharField(max_length=2000)
    click = models.BigIntegerField(default=0)
    shortened_url = models.CharField(max_length=6, default=rand_string)
    create_via = models.CharField(max_length=8, choices=UrlCreatedVia.choices, default=UrlCreatedVia.WEBSITE)
    expired_at = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "prefix",
                    "shortened_url",
                ]
            ),
        ]

    def clicked(self):
        self.click += 1
        self.save()


class Statistic(TimeStampedModel):
    class ApproachDevice(models.TextChoices):
        PC = "pc"
        MOBILE = "mobile"
        TABLET = "tablet"

    shortened_url = models.ForeignKey(ShortenedUrls, on_delete=models.CASCADE)
    ip = models.CharField(max_length=15)
    web_browser = models.CharField(max_length=50)
    device = models.CharField(max_length=6, choices=ApproachDevice.choices)
    device_os = models.CharField(max_length=30)
    custom_params = models.JSONField(null=True)

    def record(self, request, url: ShortenedUrls, params: Dict):
        self.shortened_url = url
        self.ip = request.META["REMOTE_ADDR"]
        self.web_browser = request.user_agent.browser.family
        self.device = self.ApproachDevice.MOBILE if request.user_agent.is_mobile else self.ApproachDevice.TABLET if request.user_agent.is_tablet else self.ApproachDevice.PC

        t = TrackingParams.get_tracking_params(url.id)
        self.custom_params = dict_slice(dict_filter(params, t), 5)
        self.device_os = request.user_agent.os.family
        url.clicked()
        self.save()


class TrackingParams(TimeStampedModel):
    shortened_url = models.ForeignKey(ShortenedUrls, on_delete=models.CASCADE)
    params = models.CharField(max_length=20)

    @classmethod
    def get_tracking_params(cls, shortened_url_id: int):
        #["email_id", "ref_by"] -> flat = True
        #[{"params" : "email_id"}, {"params":"ref_by"}] -> flat = False
        return TrackingParams.objects.filter(shortened_url_id=shortened_url_id).values_list("params", flat=True)
