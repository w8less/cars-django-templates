from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, RedirectView, CreateView, DeleteView
from django.views.generic.base import TemplateView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from apps.main.models import Car, Seller, Model, Mark, CarsComment, FavouriteCar
from apps.users.forms import PhoneRequiredMixin
from apps.users.models import NewFilter


class CheckCarView(ListView):
    template_name = 'main/check_car.html'
    model = Car
    context_object_name = "car_list"


def get_pagination_data(request, car_qs, page, item_on_page=10):
    current_path = request.get_full_path()
    paginator = Paginator(car_qs, item_on_page)
    try:
        car_list = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        car_list = paginator.page(page)
    except EmptyPage:
        car_list = paginator.page(paginator.num_pages)

    page = int(page)
    next_page = page + 1
    if next_page > paginator.num_pages:
        next_page = False

    prev_url = current_path.replace('page={}'.format(page), 'page={}'.format(page-1)) \
        if 'page=' in current_path and page != 1 else None
    next_url = (current_path.replace('page={}'.format(page), 'page={}'.format(next_page)) \
        if 'page=' in current_path else current_path + '&page={}'.format(next_page) \
        if '?' in current_path else '?page={}'.format(next_page)) if next_page else None

    return car_list, page, prev_url, next_url


def get_filtered_car_qs(params, qs):
    data = {key: value for key, value in params.items() if value and key not in ['page', 'model__mark', 'model']}
    query = Q()
    marks_models = list(map(lambda x, y: {'model__mark': int(x), 'model': int(y)} if y else {'model__mark': int(x)}, params.getlist('model__mark'), params.getlist('model')))
    for item in marks_models:
        query |= Q(**item)
    return qs.filter(query, **data), marks_models


def get_models(request, mark_id):
    models = [{'id': model.id, 'name': model.name} for model in Model.objects.filter(mark__id=mark_id)]
    return JsonResponse({'models': models})


def get_marks(request):
    marks = [{'id': mark.id, 'name': mark.name} for mark in Mark.objects.all()]
    return JsonResponse({'marks': marks})


class HomePage(ListView):
    template_name = 'main/home.html'
    context_object_name = 'car_list'

    def get_queryset(self):
        return Car.objects.filter(sold=False).order_by('-created')[:5]


class AllCarView(ListView):
    template_name = 'main/all_car.html'

    def get(self, request, *args, **kwargs):
        params = request.GET
        data = {key:value for key, value in params.items() if value}
        if params and not any([param for param in params.values()]):
            return HttpResponseRedirect(redirect_to='/all-car/')
        page = params.get('page')

        car_qs, marks_models = get_filtered_car_qs(params, Car.objects)

        car_list, page, prev_url, next_url = get_pagination_data(request, car_qs, page)

        for item in marks_models:
            item['model_list'] = [{'id': model.id, 'name': model.name} for model in Model.objects.filter(mark__id=item['model__mark'])]

        context = {
            'car_list': car_list,
            'marks_models': marks_models,
            'page': page,
            'prev_url': prev_url,
            'next_url': next_url
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        params = {
            'user': request.user,
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'data': request.POST.get('data'),
        }
        if params['user'] and params['data']:
            NewFilter.objects.create(**params)
        return HttpResponseRedirect(reverse('all-car'))


class SearchByNumber(TemplateView):
    template_name = 'main/search_by_number.html'

    def get(self, request, *args):
        params = request.GET
        page = params.get('page')
        form = PhoneRequiredMixin(params)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            car_qs = Car.objects.filter(seller__phone__contains=phone)

            car_list, page, prev_url, next_url = get_pagination_data(request, car_qs, page)

            context = {
                'car_list': car_list,
                'page': page,
                'prev_url': prev_url,
                'next_url': next_url
            }

            return render(request, self.template_name, context)
        return render(request, self.template_name, {})


class SellerView(DetailView):
    template_name = 'main/seller.html'
    model = Seller
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = context['seller']
        params = self.request.GET
        page = params.get('page')

        car_qs, marks_models = get_filtered_car_qs(params, seller.car_set)

        car_list, page, prev_url, next_url = get_pagination_data(self.request, car_qs, page)

        context['car_list'] = car_list
        context['page'] = page
        context['prev_url'] = prev_url
        context['next_url'] = next_url
        context['seller_page'] = True
        return context


class CarsCommentView(CreateView):
    model = CarsComment
    fields = ['car', 'author', 'comment']
    success_url = '/'


class CarsCommentDeleteView(DeleteView):
    model = CarsComment
    success_url = '/'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class FavouriteCarView(TemplateView):
    template_name = 'users/favourite_list.html'
    context_object_name = 'car_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_list = list()
        for item in FavouriteCar.objects.filter(user=self.request.user).order_by('-id'):
            car_list.append(item.car)
        context['car_list'] = car_list
        return context

    def post(self, request, *args, **kwargs):
        car_id = request.POST.get('car_id', None)
        fav_car = FavouriteCar.objects.filter(car_id=car_id, user=request.user)
        if fav_car:
            fav_car.delete()
            return JsonResponse({'message':'deleted'})
        else:
            FavouriteCar.objects.create(car_id=car_id, user=request.user)
            return JsonResponse({'message':'created'})
