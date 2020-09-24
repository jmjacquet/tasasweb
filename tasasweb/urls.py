# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.urls import re_path, path
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from .views import login,logout,handler404,handler500

urlpatterns = [    
    path('', include('tadese.urls')),    
    path('api/v1/', include('api.urls')),
    path('login/', login,name="login"),
    path('logout/', logout,name="logout"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:    
	import debug_toolbar
	urlpatterns += re_path(r'^__debug__/', include(debug_toolbar.urls)),
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler500 = handler500
handler404 = handler404