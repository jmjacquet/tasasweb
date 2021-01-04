# -*- coding: utf-8 -*-
from django.urls import re_path, path
from django.conf.urls import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from api.views import APICuotasViewSet,APIBoletasViewSet
from api.views import CuotasListView,BoletasListView
# from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token,verify_jwt_token
from rest_framework import routers
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title=u'Documentación de la Web API.')

router = routers.DefaultRouter()
# router.register(r'cuotas', APICuotasViewSet)
#router.register(r'boletas', APIBoletasViewSet)

app_name = 'api'
urlpatterns = [       
   path('', include(router.urls)),
   # url(r'^token/', obtain_jwt_token, name='token_create'),    
   # url(r'^token-refresh/', refresh_jwt_token,name='token_refresh'),
   # url(r'^token-verify/', verify_jwt_token,name='token_verify'),

   path('cuotas/', CuotasListView.as_view(),name="api_cuotas"),
   path('boletas/',BoletasListView.as_view(),name="api_boletas"),
   #url(r'^padrones/(?P<idResp>[^/]+)/$', APIPadronesList.as_view(),name="api_padrones"),    

   

   # url(r'^cuota/(?P<idc>[^/]+)/$', APICuota.as_view(),name="api_cuota_ver"),

   path('', schema_view),
   path('auth/', include('rest_framework.urls')),   

]