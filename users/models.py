from email.policy import default
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.forms import CharField
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
"""
重要部分は 重要 と表記
"""



# ユーザー
# 
# UserManager, 役割, ターミナルでユーザーを作成（manage.py createsuperuserなど）する際に呼ばれる(https://office54.net/python/django/model-custom-user#:~:text=%E3%82%BF%E3%83%BC%E3%83%9F%E3%83%8A%E3%83%AB%E3%81%A7%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC%E3%82%92%E4%BD%9C%E6%88%90%EF%BC%88manage.py%20createsuperuser%E3%81%AA%E3%81%A9%EF%BC%89%E3%81%99%E3%82%8B%E9%9A%9B%E3%81%AB%E5%91%BC%E3%81%B0%E3%82%8C%E3%82%8B)
# django.contrib.auth.modelsにあるUsrManagerを継承
# なぜUserManagerを再度記述しているのか? → class継承の基本なのでは。オーバーライドのために全定義ごと〜。
class UserManager(BaseUserManager):
    # 原文
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        # username → email の書き換え
        if not email:
            # 入力エラーの設定
            raise ValueError('Emailを入力して下さい')
        # メールアドレスの表記の揺れを修正する(https://stackoverflow.com/questions/27936705/what-does-it-mean-to-normalize-an-email-address)
        email = self.normalize_email(email)
        # GlobalUserModel ＝ app_labelとobject_labelの取得
        # GlobalUserModel → self.model の書き換え
        # modelを直接参照?
        username = self.model.normalize_username(username)
        # 原文
        user = self.model(username=username, email=email, **extra_fields)
        # 違い , ?
        user.set_password(password)
        # 原文
        user.save(using=self.db)
        return user

    # 入力必須にするためか、 引数emailのデフォルト値 → なし に書き換え, ?
    def create_user(self, username, email, password=None, **extra_fields):
        # 原文
        extra_fields.setdefault('is_staff', False)
        # 原文
        extra_fields.setdefault('is_superuser', False)
        # 引数username の削除 , 理由(_create_user()でusernameなしではエラー表示になるため)?
        return self._create_user(email, password, **extra_fields)

    # email=None, password=None, のデフォルト値の設定をなくしている → 入力必須にするため ?
    def create_superuser(self, username, email, password, **extra_fields):
        # 原文
        extra_fields.setdefault('is_staff', True)
        # 原文
        extra_fields.setdefault('is_superuser', True)

        # エラー文の書き換え
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=Trueである必要があります。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=Trueである必要があります。')
        return self._create_user(username, email, password, **extra_fields)

# カスタムユーザーモデルの定義
class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    #(https://self-methods.com/django-model-uuid-id/)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_("username"), max_length=50, validators=[username_validator], blank=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    # 原文
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    # 原文
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    # 原文
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # 原文
    # objects.get()など、views.pyで取得するための設定
    objects = UserManager()

    # フォロー機能
    # 外部制約
    following = models.ManyToManyField("self",related_name="followed_by",symmetrical=False,blank=True)
    follow_state = models.BooleanField(default=False)


    # 原文
    # ターミナルでユーザー作成（manage.py createsuperuser）するときに表示。入力必須。
    EMAIL_FIELD = "email"
    # 重要 ログイン認証などで使用するfield。ここをemailにすることでメールアドレスでのログインが可能になる。(https://office54.net/python/django/model-custom-user#:~:text=%E3%81%93%E3%81%93%E3%82%92email%E3%81%AB%E3%81%99%E3%82%8B%E3%81%93%E3%81%A8%E3%81%A7%E3%83%A1%E3%83%BC%E3%83%AB%E3%82%A2%E3%83%89%E3%83%AC%E3%82%B9%E3%81%A7%E3%81%AE%E3%83%AD%E3%82%B0%E3%82%A4%E3%83%B3%E3%81%8C%E5%8F%AF%E8%83%BD%E3%81%AB%E3%81%AA%E3%82%8A%E3%81%BE%E3%81%99%E3%80%82)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Email & Password are required by default.

    # 原文
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        # abstract = True → 削除
        # DBテーブルが作成されない、Abstract base class としての設定を削除
        # (https://docs.djangoproject.com/en/4.0/topics/db/models/#:~:text=This%20model%20will%20then%20not%20be%20used%20to%20create%20any%20database%20table.)
        # (https://qiita.com/xKxAxKx/items/99a5060c5ab8bb2fc297#:~:text=abstract%20%3D%20True%E3%81%AB%E3%81%97%E3%81%A6%E3%81%8A%E3%81%8F%E3%81%A8%E3%80%81%E3%83%9E%E3%82%A4%E3%82%B0%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%97%E3%81%A6%E3%82%82%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%81%8C%E4%BD%9C%E3%82%89%E3%82%8C%E3%82%8B%E3%81%93%E3%81%A8%E3%81%AF%E3%81%AA%E3%81%84%E3%80%82)

    # 原文
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    # get_full_name()とget_short_name()の削除
    # → カスタムユーザーモデルではfull_name, short_nameフィールドを使用しないため。

    # 原文
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # 管理画面の表示
    def __str__(self):
        return self.username