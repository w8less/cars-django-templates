from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required, user_passes_test

from django.views.generic import View, TemplateView, FormView, RedirectView, ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView

from django.core.cache import cache

from apps.users.models import Profile, InfoMessage, UserFilter
from apps.main.models import CarsComment
from apps.orders.models import Plan

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from apps.users.forms import RegistrationForm, PhoneRequiredMixin, ProfileUpdateForm, UserFilterForm
from apps.users.utils import _get_code, _verify_code, single_message


class LoginView(FormView):
    form_class = AuthenticationForm
    http_method_names = ['post']
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def form_invalid(self, form):
        return JsonResponse(form.errors)

    def get_success_url(self):
        next_url = self.request.POST.get('next', None)
        print(next_url)
        return f'{next_url}' if next_url else reverse('home')


class LogoutView(RedirectView):
    url = reverse_lazy('home')

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class SendCodeView(View):

    def post(self, request):
        form = PhoneRequiredMixin(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            if not Profile.objects.filter(phone=phone).exists():
                code = _get_code()
                cache.set(phone, code, 24*3600)
                message = f'Код для регистрации: {code}'
                single_message(phone, message)
                return JsonResponse({'message': 'ok'}, status=200)
            else:
                return JsonResponse({'message': 'Этот телефон уже зарегестрирован.'}, status=400)
        else:
            return JsonResponse(form.errors, status=400)


class RegistrationView(FormView):
    form_class = RegistrationForm
    http_method_names = ['post']
    success_url = reverse_lazy('home')

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = int(self.request.POST.get('code', ''))
        phone = form.cleaned_data.get('phone')
        if _verify_code(phone, code):
            form.save()
            user = Profile.objects.filter(email=form.cleaned_data['email']).first()
            if user:
                login(self.request, user)
            return super().form_valid(form)
        else:
            return JsonResponse({'message':'code incorrect'}, status=400)

    def form_invalid(self, form):
        return JsonResponse(form.errors)


class ProfileView(TemplateView):
    template_name = 'users/profile_page.html'

    @method_decorator(login_required, csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['comments'] = CarsComment.objects.filter(author=self.request.user)
        context['filter_list'] = UserFilter.objects.filter(user=self.request.user).order_by('-id')
        plan_qs = Plan.objects.all()
        context['plan_list'] = plan_qs.all()
        context['premium'] = plan_qs.filter(plan_type=1)
        context['pro'] = plan_qs.filter(plan_type=2)
        return context

    def post(self, request):
        name = request.POST.get('name', None)
        if name:
            request.user.name = name
            request.user.save()
        return HttpResponseRedirect(reverse('auth:profile'))


class ProfileListView(ListView):
    queryset = Profile.objects.order_by('-id')
    template_name = 'users/profile_list.html'
    context_object_name = 'profiles'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        return JsonResponse(form.errors)

    def get_success_url(self):
        return reverse_lazy('auth:profile-detail', kwargs=self.kwargs)


class ProfileDeleteView(DeleteView):
    model = Profile
    success_url = reverse_lazy('auth:profile-list')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TelegramConnectView(View):

    @method_decorator(login_required)
    def post(self, request):
        text = f'https://telegram.me/carstest_bot?start={request.user.id}'
        request.user.send_message(text)
        return JsonResponse({'status': 'ok'})


class UserFilterCreateView(CreateView):
    model = UserFilter
    form_class = UserFilterForm


class UserFilterChangeView(View):

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        filter_id = request.POST.get('filter_id')
        filter_obj = UserFilter.objects.filter(id=filter_id, user=request.user).first()
        if filter_obj:
            filter_obj.is_active = not filter_obj.is_active
            filter_obj.save()
        return HttpResponseRedirect(reverse('auth:profile'))


class UserFilterUpdateView(UpdateView):
    model = UserFilter
    fields = ['name', 'description', 'model', 'mark', 'gearbox', 'location',
            'year_start', 'year_end', 'price_start', 'price_end', 'cleared',
            'dtp', 'blocked', 'dealer']
    template_name = 'users/user_filter_update.html'
    context_object_name = 'filter_item'

    def form_invalid(self, form):
        return JsonResponse(form.errors)

    def get_success_url(self):
        return reverse_lazy('auth:profile-page', kwargs=self.kwargs)


class InfoMessageView(TemplateView):
    template_name = 'main/info_message.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        message = request.POST.get('message', None)
        InfoMessage.objects.update_or_create(pk=1, defaults={'message': message})
        return HttpResponseRedirect(reverse('auth:info-message'))
