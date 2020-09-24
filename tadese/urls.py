# -*- coding: utf-8 -*-
from django.urls import re_path, path
from django.conf import settings
import os
from .views import *
from tasasweb.views import volverHome
from django.views.generic import RedirectView,TemplateView

# Uncomment the next two lines to enable the admin:
app_name = 'tadese'

urlpatterns = [    
    re_path(r'^$', volverHome,name="inicio"),
    re_path(r'^municipio/$', verDDJJDrei,name="municipio"),
    re_path(r'^estudios/$', EstudiosView.as_view(),name="padrones_estudio"),
    re_path(r'^padrones/$', PadronesView.as_view(),name="padrones_responsable"),
    
    re_path(r'^cuotas/(?P<idp>[^/]+)/$', BusquedaCuotasView.as_view(),name="ver_cuotas"),
    re_path(r'^cuotas/(?P<idp>[^/]+)/(?P<anio>\d+)/$', BusquedaCuotasView.as_view(),name="buscarCuotasAP"),

    re_path(r'^drei/(?P<idc>\d+)/$', DreiLiquidarCreateView.as_view(),name="drei_liquidarBoleta"),
    re_path(r'^drei2/(?P<idb>\d+)/$', DreiLiquidarUpdateView.as_view(),name="drei_reliquidarBoleta"),
    re_path(r'^drei3/(?P<idb>\d+)/$', DreiRectificar.as_view(),name="drei_rectificarBoleta"),
    re_path(r'^drei4/(?P<idc>\d+)/$', DreiRectificarNew.as_view(),name="drei_rectificarNewBoleta"),

    re_path(r'^drei/eliminar/(?P<idb>[^/]+)/$', EliminarBoleta,name="eliminar_boleta"),
    re_path(r'^drei/modif_bases/(?P<idb>\d+)/$', DreiModifBasesView.as_view(),name="drei_modif_bases"),
    
    re_path(r'^punitorios/(?P<idc>\d+)/(?P<valor>\d+\.\d+)/$',calcularPunitoriosForm,name="calcularPunitorios"),
    re_path(r'^punitoriosLiq/$',generarPunitoriosLiq,name="generarPunitoriosLiq"),

    re_path(r'^imprimir/(?P<idc>\d+)/$',imprimirPDF,name="imprimirPDF"),
    re_path(r'^imprimir/(?P<idc>\d+)/(?P<idb>\d+)/$',imprimirPDF,name="imprimirPDFBoleta"),
    re_path(r'^imprimirLiqWeb/(?P<id_liquidacion>\d+)/$',imprimirPDFLiqWeb,name="imprimirPDFLiqWeb"),
    
    re_path(r'^drei/ddjja/(?P<idp>\d+)/$', DreiDDJJAList.as_view(),name="drei_ddjja_list"),
    re_path(r'^drei/ddjja/(?P<idp>\d+)/(?P<anio>\d+)/$', DreiDDJJAList.as_view(),name="drei_ddjja_list"),

    re_path(r'^estudios/editar/(?P<pk>\d+)$', EstudiosUpdateView.as_view(), name='estudio_editar'),
    
    re_path(r'^liquidacion/(?P<idp>\d+)/$', generarLiquidacion,name="generarLiquidacion"),
    
    re_path(r'^estudios/passwd/(?P<usrEstudio>.+)$', mandarEmailEstudio, name='mandarEmailEstudio'),

    re_path(r'^suscripcion/alta/(?P<idp>\d+)/$', suscripcion_alta,name="suscripcion_alta"),
    re_path(r'^suscripcion/baja/(?P<idp>\d+)/$', suscripcion_baja,name="suscripcion_baja"),    

    re_path(r'^pago/$', generarPago,name="pago"),

    re_path(r'^pago/exito/$', generarPagoExito,name="pago_exito"),
    re_path(r'^pago/error/(?P<idp>\d+)/$', generarPagoError,name="pago_error"),

   
    ]