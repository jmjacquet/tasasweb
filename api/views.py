# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import *
from rest_framework import generics
from .serializers import CuotasSerializer,CustomCuotasSerializer,BoletasSerializer
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from tadese.models import Cuotas,Tributo,Configuracion,DriBoleta
from django.db.models import Count,Sum,F
import json
from decimal import Decimal
import decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import filters
from django.db import connection

# class APICuotasViewSet(viewsets.ModelViewSet):
# 	search_fields = ['padron','id_padron']
# 	filter_backends = (filters.SearchFilter,)
# 	serializer_class = CuotasSerializer
# 	queryset = Cuotas.objects.all().select_related('tributo')
# 	permission_classes = (AllowAny,)


# 	def dispatch(self, *args, **kwargs):
# 		response = super(APICuotasViewSet, self).dispatch(*args, **kwargs)
# 		print("Cantidad de Queries:%s" % len(connection.queries))
# 		return response

# 	@action(detail=False)
# 	def ultimas_cuotas(self, request):
# 		cuotas = self.get_queryset()
# 		if request.user.is_authenticated():     
# 			idResp= int(request.user.userprofile.id_responsable)	
# 			cuotas = cuotas.filter(id_responsable=idResp)[:1000]
# 		else:
# 			cuotas = cuotas[:1000]
# 		cant=len(cuotas)		
# 		serializer = CuotasSerializer(cuotas, many=True)
# 		return Response({'data':serializer.data,'cantidad':cant})

# 	@action(detail=False)
# 	def ultimas_cuotas_puras(self, request):		
# 		cuotas = self.get_queryset()[:1000]
# 		cant=len(cuotas)		
# 		serializer = CuotasSerializer(cuotas, many=True)
# 		return Response(serializer.data)

# 	def list(self, request ):
# 		id_padron =request.query_params.get('id_padron', None)
# 		if id_padron:
# 			cuotas = self.get_queryset().filter(id_padron=id_padron)
# 		else:
# 			cuotas = self.get_queryset()
		
# 		cant=len(cuotas)
# 		serializer = CuotasSerializer(cuotas, many=True)
# 		return Response({'data':serializer.data,'cantidad':cant})

# 	@action(detail=False)
# 	def cuotas_puras(self,request):
# 		cuotas = self.get_queryset().annotate(tributo_abreviatura=F('tributo__abreviatura'),tributo_nombre=F('tributo__descripcion'),estado_nombre=F('get_estado')).values()[:1000]				
# 		cant=len(cuotas)
# 		# cuotas = Cuotas.objects.all()[:100]
# 		# serializer = CuotasSerializer(cuotas, many=True)
# 		return Response({'data':cuotas,'cantidad':cant})
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = 60 * 5


#@method_decorator(cache_page(CACHE_TTL), name='dispatch') # NEW
class CuotasListView(generics.ListAPIView):    
    serializer_class = CuotasSerializer    
    queryset = Cuotas.objects.all().select_related('tributo')
        
    def dispatch(self, *args, **kwargs):
        response = super(CuotasListView, self).dispatch(*args, **kwargs)
        # print "Cantidad de Queries:%s" % len(connection.queries) 
        print(connection.queries)
        return response
    

    def list(self,*args, **kwargs):
        cuotas = self.get_queryset()        
        # try:
        #     cantidad =self.request.query_params.get('cantidad', None) 
        #     inicio =self.request.query_params.get('inicio', None) 
        #     if not inicio:
        #         inicio = 0    
        #     if not cantidad:
        #         cantidad = 0          
        #     cuotas = cuotas[int(inicio):int(cantidad)]
        # except:
        #     cuotas = cuotas[:0]                 
        try:
            tributo =self.request.query_params.get('tributo', None) 
            if tributo:
                    cuotas = cuotas.filter(tributo__pk=tributo)
        except:
            pass
        try:
            id_unidad =self.request.query_params.get('id_unidad', None) 
            if id_unidad:
                    cuotas = cuotas.filter(id_unidad=id_unidad)
        except:
            pass
        try:
            anio_desde =self.request.query_params.get('anio_desde', None) 
            if anio_desde:
                    cuotas = cuotas.filter(anio__gte=anio_desde)
        except:
            pass
        try:
            anio_hasta =self.request.query_params.get('anio_hasta', None) 
            if anio_hasta:
                    cuotas = cuotas.filter(anio__lte=anio_hasta)
        except:
            pass
        try:
            id_padron =self.request.query_params.get('id_padron', None) 
            if id_padron:
                    cuotas = cuotas.filter(id_padron=id_padron)
        except:
        	pass
        cant=len(cuotas)
        serializer = CuotasSerializer(cuotas, many=True)
        return Response({'data':serializer.data,'cantidad':cant})
        #return Response({'data':cuotas.values(),'cantidad':cant})


class BoletasListView(generics.ListAPIView):    
	serializer_class = BoletasSerializer
	queryset = DriBoleta.objects.all().prefetch_related('boleta_actividades__id_boleta',)		

	def dispatch(self, *args, **kwargs):
		response = super(BoletasListView, self).dispatch(*args, **kwargs)
		# print "Cantidad de Queries:%s" % len(connection.queries) 
		# print connection.queries          
		return response

	def list(self, request ):
		id_padron =request.query_params.get('id_padron', None)
		if id_padron:
			boletas = self.get_queryset().filter(id_padron=id_padron)
		else:
			boletas = self.get_queryset()
		cant=len(boletas) 
		serializer = BoletasSerializer(boletas, many=True)
		return Response({'data':serializer.data,'cantidad':cant})

# class APIBoletasViewSet(viewsets.ModelViewSet):
# 	serializer_class = BoletasSerializer
# 	queryset = DriBoleta.objects.all().prefetch_related('boleta_actividades__id_boleta',)		
# 	permission_classes = (AllowAny,)


# 	def dispatch(self, *args, **kwargs):
# 		response = super(APIBoletasViewSet, self).dispatch(*args, **kwargs)
# 		# print "Cantidad de Queries:%s" % len(connection.queries)
# 		# for query in connection.queries:
# 			# print query['sql']
# 		return response

# 	def list(self, request ):
# 		id_padron =request.query_params.get('id_padron', None)
# 		if id_padron:
# 			boletas = self.get_queryset().filter(id_padron=id_padron)
# 		else:
# 			boletas = self.get_queryset()
# 		cant=len(boletas)
# 		serializer = BoletasSerializer(boletas, many=True)
# 		return Response({'data':serializer.data,'cantidad':cant})
# 		# return Response({'data':boletas,'cantidad':cant})

