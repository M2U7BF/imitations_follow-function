from django.views.generic import DetailView, TemplateView, CreateView, View
from .models import *
from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _
from django.urls import reverse_lazy,reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms
from django.contrib.auth import get_user_model 
from django.http.response import JsonResponse
from django.http import HttpResponse

User = get_user_model()

class MyPageView(DetailView):
    template_name = 'my_home.html'
    model = ArticleModel

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        ctxt["object_list"] = ArticleModel.objects.all()
        ownerPk = self.kwargs['userid']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        return ctxt
    
    # オーバーライド
    # get_object()は何をしているのか? → 
    # urlに値する1つのデータを取得
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        # request に 合致するデータを取得
        # return get_object_or_404(User, pk=self.request.session['user_id'])
        # pk = self.kwargs.get(self.request)
        # 原文
        pk = self.kwargs['userid']
        # pk = self.kwargs.get(self.pk_url_kwarg)
        # pk
        if pk is not None:
            # この時点で単数にする(?)
            queryset = queryset.filter(posted_by=pk)
        
        try:
            # Get the single item from the filtered queryset
            objs = queryset.filter()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return objs

class HomePageView(DetailView):
    template_name = '_main.html'
    model = ArticleModel

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        # ctxt["following_num"] = None
        ctxt["object_list"] = ArticleModel.objects.all()
        ownerPk = self.kwargs['userid']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        ctxt["following_num"] = User.objects.get(pk=ownerPk).following.all().count()
        ctxt["followed_num"] = User.objects.get(pk=ownerPk).followed_by.all().count()
        return ctxt
    
    # オーバーライド
    # get_object()は何をしているのか? → 
    # urlに値する1つのデータを取得
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        # request に 合致するデータを取得
        # return get_object_or_404(User, pk=self.request.session['user_id'])
        # pk = self.kwargs.get(self.request)
        # 原文
        pk = self.kwargs['userid']
        # pk = self.kwargs.get(self.pk_url_kwarg)
        # pk
        if pk is not None:
            # この時点で単数にする(?)
            queryset = queryset.filter(posted_by=pk)
        
        try:
            # Get the single item from the filtered queryset
            objs = queryset.filter()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return objs

class index_view(TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        ctxt["user_list"] = User.objects.all()
        return ctxt

class ArticleCreateView(CreateView):
    template_name = 'create_article.html'
    model = ArticleModel
    fields = ('posted_text','posted_by')

    # オーバーライド
    # (https://torajirousan.hatenadiary.jp/entry/2018/08/31/023519)
    def get_success_url(self):
        return reverse_lazy("my_page",kwargs={"userid":self.kwargs["userid"]} )
    
    def get_form(self):
        form = super(ArticleCreateView, self).get_form()
        form.fields['posted_by'].label = '投稿者'
        form.initial['posted_by'] = self.kwargs['userid'] # フィールドの初期値の設定(https://k-mawa.hateblo.jp/entry/2017/10/31/235640)
        form.fields['posted_text'].required = True
        return form

class UserCreateView(CreateView):
    template_name = 'create_user.html'
    form_class = forms.SignUpForm

    # ! 本来ならばログイン画面に遷移
    success_url = reverse_lazy('index') # 投稿完了時の遷移先

class MyLoginView(LoginView):
    form_class = forms.LoginForm
    template_name = "login.html"

class MyLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "logout.html"


class FollowView(View):
    #実行されるときの処理
    # def get(self, request, *args, **kwargs):
    # obj = User.objects.get(自分)
    def get(self, request, *args, **kwargs):
        path = request.path
        return HttpResponse(path)
    
    # if 対象.follow_state == False :
    #     自分.following.add(対象)
    #     対象.follow_state = True
    #     obj.save()
    # elif 対象.follow_state == True :
    #     自分.following.remove(対象)
    #     対象.follow_state = False
    #     obj.save()

    # return JsonResponse({"follow_num,":obj.follow_num})
    
    # M:M を設定するクエリ実行(viewにて)。
        # A.following.remove(B) 
        # A.following.add(B)
    # all().count()で数え直す
    # 結果をレスポンス

    # .get()とかはクエリ文?、django shell文?
    # button からDB操作はformがよいか
    # if~ True だと押した時 ~をFalseにする


    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        # ctxt["following_num"] = None
        ctxt["object_list"] = ArticleModel.objects.all()
        ownerPk = self.kwargs['userid']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        ctxt["following_num"] = User.objects.get(pk=ownerPk).following.all().count()
        ctxt["followed_num"] = User.objects.get(pk=ownerPk).followed_by.all().count()
        return ctxt

    def get_object(self, queryset=None):
        pk = self.kwargs['userid']

        if queryset is None:
            queryset = self.get_queryset()

        if pk is not None:
            queryset = queryset.filter(posted_by=pk)
        
        try:
            # Get the single item from the filtered queryset
            objs = queryset.filter()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return objs


def UnfollowView(request,pk):
    try:
        obj = User.objects.get(pk=pk) # pkを元にUserテーブルの対象モデルを取得する
    except User.DoesNotExist:
        raise Http404
    obj.unfollow_num += 1  # ここでいいねの数を増やす
    obj.save()  # 保存をする
    

    return JsonResponse({"follow_num,":obj.follow_num}) # いいねの数をJavaScriptに渡す