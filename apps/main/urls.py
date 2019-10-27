from django.urls import path

from apps.main.views import (
    get_marks,
    get_models,

    HomePage,
    AllCarView,
    SellerView,
    CarsCommentView,
    CarsCommentDeleteView,
    FavouriteCarView,
    SearchByNumber,
    CheckCarView
)


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('all-car/', AllCarView.as_view(), name='all-car'),
    path('favourite/', FavouriteCarView.as_view(), name='favourite'),
    path('check_car/', CheckCarView.as_view(), name='check_car'),

    path('by_number/', SearchByNumber.as_view(), name='search-by-number'),

    path('seller/<int:pk>/', SellerView.as_view(), name='seller'),

    path('api/comment/', CarsCommentView.as_view(), name='add-comment'),
    path('api/comment/<pk>/', CarsCommentDeleteView.as_view(), name='del-comment'),


    path('api/marks', get_marks, name='get-marks'),
    path('api/models/<int:mark_id>', get_models, name='api-models'),

]
