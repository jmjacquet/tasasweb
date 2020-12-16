# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
# Python
import json
from datetime import datetime,date
from dateutil.relativedelta import *
from model_mommy import mommy

# Django Rest Framework
from rest_framework.test import APIClient
from rest_framework import status

# Models
from tadese.models import Cuotas,Tributo,DriBoleta,DriBoleta_actividades

from tadese.utilidades import ESTADOS,hoy

vencido = date(1900,1,1)
no_vencido = date(3000,1,1)

class APICuotasTest(TestCase):        
	
	def setUp(self):
		self.vencido=vencido
		self.hoy = hoy()
		self.urbano = mommy.make(Tributo,id_tributo=1,tipo_interes=None,interes=None,descripcion='TGIs',abreviatura='TGIU',correr_venc_fdesde=date(2020,1,1),correr_venc_fhasta=date(2020,2,15),correr_venc_dias=0)      
		self.rural = mommy.make(Tributo,id_tributo=2,tipo_interes=None,interes=None,descripcion='TGIs',abreviatura='TGIR',correr_venc_fdesde=date(2020,1,1),correr_venc_fhasta=date(2020,2,15),correr_venc_dias=0)      		
		self.drei = mommy.make(Tributo,id_tributo=6,tipo_interes=None,interes=None,descripcion='DReI',abreviatura='DRI',correr_venc_fdesde=date(2020,1,1),correr_venc_fhasta=date(2020,2,15),correr_venc_dias=0)      		
		self.cuota_urbano = mommy.make(Cuotas,id_cuota=1,id_unidad=1,tributo=self.urbano,cuota='1',anio=2020,saldo=100,vencimiento=date(2020,1,15),segundo_vencimiento=date(2020,2,15),id_padron=1,padron='001',id_responsable=1) 						
		self.cuota_rural = mommy.make(Cuotas,id_cuota=2,id_unidad=2,tributo=self.rural,cuota='1',anio=2020,saldo=100,vencimiento=date(2020,1,15),segundo_vencimiento=date(2020,2,15),id_padron=1,padron='001',id_responsable=1) 
		self.cuota_drei = mommy.make(Cuotas,id_cuota=3,id_unidad=2,tributo=self.drei,cuota='1',anio=2020,saldo=100,vencimiento=date(2020,1,15),segundo_vencimiento=date(2020,1,15),id_padron=3,padron='001',id_responsable=1) 
		self.client = APIClient()

	def test_cuotas_list(self):
		response = self.client.get(reverse('api:api_cuotas'))				
		result = json.loads(response.content)
		cantidad= result.get('cantidad')		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad, 3)
		
	def test_cuotas_padron_list(self):		
		#client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)			
		response = self.client.get('/api/v1/cuotas/?id_padron=1')		
		result = json.loads(response.content)
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,2)

	def test_cuotas_tributo_list(self):		
		#client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)			
		response = self.client.get('/api/v1/cuotas/?tributo=1')		
		result = json.loads(response.content)		
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,1)
		cuota=result.get('data')[0]
		self.assertEqual(cuota.get('tributo'),self.urbano.pk)

	def test_cuotas_unidad_list(self):		
		#client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)			
		response = self.client.get('/api/v1/cuotas/?id_unidad=2')		
		result = json.loads(response.content)
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,2)

	def test_cuotas_anios_list(self):		
		#client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)			
		response = self.client.get('/api/v1/cuotas/?anio_desde=2020')		
		result = json.loads(response.content)
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,3)

		response = self.client.get('/api/v1/cuotas/?anio_hasta=2019')		
		result = json.loads(response.content)
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,0)


class APIBoletasTest(TestCase):        
	
	def setUp(self):
		self.vencido=vencido
		self.hoy = hoy()
		self.drei = mommy.make(Tributo,id_tributo=6,tipo_interes=None,interes=None,descripcion='DReI',abreviatura='DRI',correr_venc_fdesde=date(2020,1,1),correr_venc_fhasta=date(2020,2,15),correr_venc_dias=0)      		
		self.cuota1 = mommy.make(Cuotas,id_cuota=3,id_unidad=2,tributo=self.drei,cuota='1',anio=2020,saldo=100,vencimiento=date(2020,1,15),segundo_vencimiento=date(2020,1,15),id_padron=3,padron='001',id_responsable=1) 
		self.cuota2 = mommy.make(Cuotas,id_cuota=3,id_unidad=2,tributo=self.drei,cuota='2',anio=2020,saldo=100,vencimiento=date(2020,2,15),segundo_vencimiento=date(2020,2,15),id_padron=2,padron='001',id_responsable=1) 
		self.boleta = mommy.make(DriBoleta,id_cuota=self.cuota1,id_padron=3,anio=self.cuota1.anio,mes=self.cuota1.cuota)
		self.boleta2 = mommy.make(DriBoleta,id_cuota=self.cuota2,id_padron=2,anio=self.cuota2.anio,mes=self.cuota2.cuota)
		self.client = APIClient()

	def test_boletas_list(self):
		response = self.client.get(reverse('api:api_boletas'))				
		result = json.loads(response.content)
		cantidad= result.get('cantidad')		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad, 2)
		
	def test_boletas_padron_list(self):		
		#client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)			
		response = self.client.get('/api/v1/boletas/?id_padron=2')		
		result = json.loads(response.content)
		cantidad= result.get('cantidad')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(cantidad,1)

	