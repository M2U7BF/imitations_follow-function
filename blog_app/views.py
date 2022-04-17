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
from django.shortcuts import get_object_or_404


User = get_user_model()

class MyPageView(LoginRequiredMixin, DetailView):
    template_name = 'my_home.html'
    model = ArticleModel

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        ctxt['object_list'] = ArticleModel.objects.all()
        ownerPk = self.kwargs['pk']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        return ctxt
    
    # オーバーライド
    # get_object()は何をしているのか? → 
    # urlに値する1つのデータを取得
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        pk = self.kwargs['pk']
        if pk is not None:
            queryset = queryset.filter(posted_by=pk)
        
        try:
            objs = queryset.filter()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return objs

class HomePageView(LoginRequiredMixin, DetailView):
    template_name = '_main.html'
    model = ArticleModel

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        # ctxt["following_num"] = None
        ctxt["object_list"] = ArticleModel.objects.all()
        ownerPk = self.kwargs['pk']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        ctxt["following_num"] = User.objects.get(pk=ownerPk).following.all().count()
        ctxt["followed_num"] = User.objects.get(pk=ownerPk).followed_by.all().count()
        return ctxt
    
    # オーバーライド
    # urlパラメータを基に当Viewの設定modelから値を取得(この場合Articlemodelの複数値)
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        # request に 合致するデータを取得
        # return get_object_or_404(User, pk=self.request.session['user_id'])
        # pk = self.kwargs.get(self.request)
        # 原文
        pk = self.kwargs['pk']
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

class index_view(LoginRequiredMixin, TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        ctxt["user_list"] = User.objects.all()
        return ctxt

class ArticleCreateView(LoginRequiredMixin, CreateView):
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
        form.initial['posted_by'] = self.kwargs['pk'] # フィールドの初期値の設定(https://k-mawa.hateblo.jp/entry/2017/10/31/235640)
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

class FollowView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        my_userid = request.GET.get("follow")
        # #(https://teratail.com/questions/270742?link=qa_related_sp)
        # my_userid = self.kwargs.get('mypk')
        other_userid = self.kwargs['pk']

        other = User.objects.get(pk=other_userid)
        ## ここで取得できない → my_useridは中身どうなっているか
        # me = User.objects.get(pk=my_userid)
        me = get_object_or_404(User, pk=my_userid)
        
        if other.follow_state == False :
            me.following.add(other)
            other.follow_state = True
        elif other.follow_state == True :
            me.following.remove(other)
            other.follow_state = False

        me.save()
        other.save()

        followed_num = User.objects.get(pk=other_userid).followed_by.all().count()

        return JsonResponse(followed_num) # いいねの数をJavaScriptに渡す

    # return JsonResponse({"follow_num,":obj.follow_num})
    
    # M:M を設定するクエリ実行(viewにて)。
        # A.following.remove(B) 
        # A.following.add(B)
    # all().count()で数え直す
    # 結果をレスポンス


    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data()
        ctxt["object_list"] = ArticleModel.objects.all()
        ownerPk = self.kwargs['pk']
        ctxt['page_owner'] = User.objects.get(pk=ownerPk)
        ctxt["following_num"] = User.objects.get(pk=ownerPk).following.all().count()
        ctxt["followed_num"] = User.objects.get(pk=ownerPk).followed_by.all().count()
        return ctxt

def UnfollowView(request,pk):
    try:
        obj = User.objects.get(pk=pk) # pkを元にUserテーブルの対象モデルを取得する
    except User.DoesNotExist:
        raise Http404
    obj.unfollow_num += 1  # ここでいいねの数を増やす
    obj.save()  # 保存をする


    return JsonResponse({"follow_num,":obj.follow_num}) # いいねの数をJavaScriptに渡す