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

class APICuotasViewSet(viewsets.ModelViewSet):
	search_fields = ['padron','id_padron']
	filter_backends = (filters.SearchFilter,)
	serializer_class = CuotasSerializer
	queryset = Cuotas.objects.all().select_related('tributo')
	permission_classes = (AllowAny,)


	def dispatch(self, *args, **kwargs):
		response = super(APICuotasViewSet, self).dispatch(*args, **kwargs)
		print("Cantidad de Queries:%s" % len(connection.queries))
		return response

	@action(detail=False)
	def ultimas_cuotas(self, request):
		cuotas = self.get_queryset()
		if request.user.is_authenticated():     
			idResp= int(request.user.userprofile.id_responsable)	
			cuotas = cuotas.filter(id_responsable=idResp)[:1000]
		else:
			cuotas = cuotas[:1000]
		cant=len(cuotas)		
		serializer = CuotasSerializer(cuotas, many=True)
		return Response({'data':serializer.data,'cantidad':cant})

	@action(detail=False)
	def ultimas_cuotas_puras(self, request):		
		cuotas = self.get_queryset()[:1000]
		cant=len(cuotas)		
		serializer = CuotasSerializer(cuotas, many=True)
		return Response(serializer.data)

	def list(self, request ):
		id_padron =request.query_params.get('id_padron', None)
		if id_padron:
			cuotas = self.get_queryset().filter(id_padron=id_padron)
		else:
			cuotas = self.get_queryset()
		
		cant=len(cuotas)
		serializer = CuotasSerializer(cuotas, many=True)
		return Response({'data':serializer.data,'cantidad':cant})

	@action(detail=False)
	def cuotas_puras(self,request):
		cuotas = self.get_queryset().annotate(tributo_abreviatura=F('tributo__abreviatura'),tributo_nombre=F('tributo__descripcion'),estado_nombre=F('get_estado')).values()[:1000]				
		cant=len(cuotas)
		# cuotas = Cuotas.objects.all()[:100]
		# serializer = CuotasSerializer(cuotas, many=True)
		return Response({'data':cuotas,'cantidad':cant})


class APIBoletasViewSet(viewsets.ModelViewSet):
	serializer_class = BoletasSerializer
	queryset = DriBoleta.objects.all().prefetch_related('boleta_actividades__id_boleta',)		
	permission_classes = (AllowAny,)


	def dispatch(self, *args, **kwargs):
		response = super(APIBoletasViewSet, self).dispatch(*args, **kwargs)
		# print "Cantidad de Queries:%s" % len(connection.queries)
		# for query in connection.queries:
			# print query['sql']
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
		# return Response({'data':boletas,'cantidad':cant})

