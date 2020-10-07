# -*- coding: utf-8 -*-
from datetime import datetime,date
from dateutil.relativedelta import *
from decimal import Decimal
import decimal
from django.http import Http404
from  django.conf import settings
from .utilidades import correr_vencimiento
from .models import Configuracion

def punitorios(c,fecha_punitorios,importe):
  # try:
    dias = 0
    cuota = c
    meses = Decimal(0).quantize(Decimal("1"),decimal.ROUND_FLOOR)
    vencimiento = cuota.vencimiento
    seg_vencimiento = cuota.segundo_vencimiento
    if not importe:
      importe = cuota.saldo

    if not seg_vencimiento:
      seg_vencimiento = vencimiento
    
    importe = Decimal(importe).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)      
    
    hoy=date.today()  
    coeficiente_acum = Decimal(0).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)
    coeficiente = Decimal(0).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)
    coef_calc = Decimal(0).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)
    interes_especial = False 
    fecha_ctrl_int = date(1900,1,1)
    saldo_cta=c.saldo
    #fecha_emision=c.emision  
   
    tributo = c.tributo
    
    sitio = Configuracion.objects.all().first()
    if not sitio:
      return 0
    
    #Si no tiene segundo vencimiento entonces le pongo el mismo que el primero

    # CORRE N DIAS SI TIENE CONFIGURADO EN TRIBUTO PARA CORRER LOS VENCIMIENTOS
    vencimiento=correr_vencimiento(cuota.vencimiento,seg_vencimiento,c.tributo)[0]
    seg_vencimiento=correr_vencimiento(cuota.vencimiento,seg_vencimiento,c.tributo)[1]
    
    #busco el tipo de interes para el tributo
    tipo_interes = cuota.tributo.tipo_interes
    interes = cuota.tributo.interes    
    interes_2 = cuota.tributo.interes_2   
    vence_dias2 = cuota.tributo.vence_dias2
    interes_2ven = cuota.tributo.interes_2ven    
    vence_dias = cuota.tributo.vence_dias

    if not vence_dias:
      vence_dias = 0
    
    #Si no tiene definido el interés, lo busco en la configuración
    if interes == None:           
      interes = sitio.punitorios      
       
    if tipo_interes == None:            
      tipo_interes = sitio.tipo_punitorios

    if tipo_interes == None:
      tipo_interes = 1 
        
    if interes == None:
      interes = 0

    interes = Decimal(interes).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR) 

    '''-------------------------------------------------------------------------

    ------------------------------------------------------------------------
    --  Si tipo_interes = 7
    ------------------------------------------------------------------------'''
    
    if tipo_interes == 7:              
      if interes_2:      
        interes_2 = Decimal(interes_2).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR)     
        #calculo el interes entre el primer y segundo vencimiento
        dv = (seg_vencimiento - vencimiento).days
        if (dv >= 0):
        #si la diferencia de dias es mayor o igual que 0 entonces calculo        
          aux_interes = interes_2 / 30 #Calculo el interes segun cantidad de dias entre el primer y seg vencimiento.
          coeficiente = dv * aux_interes
          coeficiente_acum = coeficiente

        #si los punitorios son despues de la fecha del seg vencimiento
        dv = (fecha_punitorios - seg_vencimiento).days
        if (dv > 0):
          #si la diferencia de dias es mayor que 0 entonces calculo        
          #interes punitorio
          aux_interes = interes_2 / 30 #interes punitorio a diario
          coeficiente = dv * aux_interes #interes punitorios por la cantidad de dias
          coeficiente_acum = coeficiente_acum + coeficiente

          #interes resarcitorio
          aux_interes = interes / 30 #interes resarcitorio a diario
          coeficiente = dv * aux_interes #interes resarcitorio por la cantidad de dias
          coeficiente_acum = coeficiente_acum + coeficiente        

        tipo_interes = 3      
      else:      
        tipo_interes = None          

    '''------------------------------------------------------------------------
    --  Si tipo_interes = 99
    --     inserto hasta dos intereses interes_2, interes_3 pasados por variables
    --     de la tabla tributo corro el vencimiento de la boleta hasta vence_dias2
    --     o vence_dias3 para calcular de ahi en adelante el interes que esta en
    --     la configuracion del sistema.
    ------------------------------------------------------------------------'''
    if tipo_interes == 99:    
      interes_2 = Decimal(interes_2).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR)
      
      dias = (fecha_punitorios - vencimiento).days   
      if cuota.tributo.id_tributo == 6:
          if vence_dias == None:
              vence_dias = 0
          
          seg_vencimiento = vencimiento + relativedelta(days=vence_dias)

      if ((fecha_punitorios > vencimiento) and (fecha_punitorios <= seg_vencimiento)):
            coeficiente_acum = coeficiente_acum + interes
            fecha_punitorios = seg_vencimiento
            vencimiento = seg_vencimiento

      if ((fecha_punitorios > seg_vencimiento) and (fecha_punitorios <= (vencimiento + relativedelta(days=vence_dias2)))):
            coeficiente_acum = coeficiente_acum + interes_2
            fecha_punitorios = vencimiento + relativedelta(days=vence_dias2)
            vencimiento = vencimiento + relativedelta(days=vence_dias2)

      if (fecha_punitorios > (vencimiento + relativedelta(days=vence_dias2))):
            coeficiente_acum = coeficiente_acum + interes_2
            vencimiento = vencimiento + relativedelta(days=vence_dias2)

      interes_especial= True
      tipo_interes = None    

    '''------------------------------------------------------------------------
    --  Si tipo_interes = 10
    --     buscar y calcula el interes por rango de fechas,
    --     luego pasa a tipo_interes = 3
    ------------------------------------------------------------------------'''
    if tipo_interes == 10:    
      if interes == None:           
         interes = sitio.punitorios      

      if ((fecha_punitorios > vencimiento) and (fecha_punitorios <= seg_vencimiento)):      
        dias = (seg_vencimiento - vencimiento).days
        coef_calc = dias * (interes / 30)
        coeficiente_acum += coef_calc
      else:      
        if (fecha_punitorios > seg_vencimiento):
          from .models import TributoInteres
            
          tributo_interes = TributoInteres.objects.filter(id_tributo=cuota.tributo.id_tributo,hasta__gte=vencimiento).order_by('desde')  
          # Por cada coeficiente que corresponda hago un calculo            
          for t in tributo_interes:            
            try:                
              try:                
                 interes = t.interes
                 tipo_interes = t.tipo_interes              
              except TributoInteres.DoesNotExist:                       
                 tipo_interes = None
                 interes = None                             

          
              if tipo_interes == None:
                 tipo_interes = 1 
              
              if interes == None:
                 interes = 0                   
              hf = t.hasta
              df = t.desde
              
              if hf > fecha_punitorios:
                hf = fecha_punitorios

              if (vencimiento >= df) and (vencimiento <= hf):
                dias = (hf - vencimiento).days
              else:
                dias = (hf - df).days + 1
            except:
              dias = 0
            if dias < 0:
              dias = 0 
            if interes == None:
              interes = 0   

            interes = Decimal(interes).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR) 

            coef_calc = dias * interes / 30
            coeficiente_acum += coef_calc            
            coeficiente_acum = Decimal(coeficiente_acum).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)             

      tipo_interes = 3
    

    '''------------------------------------------------------------------------
    --  Si tipo_interes = 11
    --     busca y calcula coeficiente para la fecha de vencimiento, luego
    --     pasa a tipo_interes = 3
    ------------------------------------------------------------------------'''
    if tipo_interes == 11:
      from .models import TributoInteres
            
      tributo_interes = TributoInteres.objects.filter(id_tributo=cuota.tributo.id_tributo,hasta__gte=vencimiento).order_by('desde')  
      # Por cada coeficiente que corresponda hago un calculo            
      for t in tributo_interes:            
        try:                
          interes = t.interes
          tipo_interes = t.tipo_interes              
          hf = t.hasta
          df = t.desde
          
          dias = (fecha_punitorios - vencimiento).days
          coeficiente_acum = dias * interes / 30
        except:
          dias = 0
          coeficiente_acum = 0

      tipo_interes = 3    

    '''------------------------------------------------------------------------
    --  Si tipo_interes = 2
    -- Es Diario, pero calculo a partir del segundo vencimiento
    -- Si esta entre el primer y seg_vencimiento, coloco el interes al seg_vencimiento que esta en la tabla tributo
    ------------------------------------------------------------------------'''
    if tipo_interes == 2:    
      if interes == None:           
         interes = sitio.punitorios                     
      try:
          dias = (seg_vencimiento - vencimiento).days
      except:
          dias = 0
      if dias < 0:
          dias = 0           
      interes = Decimal(interes).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR)       

      if not interes_2ven:
        coef_calc = dias * interes / 30
      else:
        coef_calc = dias * (interes_2ven / 100) / 30

      coeficiente_acum += coef_calc
      coeficiente_acum = Decimal(coeficiente_acum).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)      

      if ((fecha_punitorios > vencimiento) and (fecha_punitorios <= seg_vencimiento)):
        vencimiento = fecha_punitorios
      elif (fecha_punitorios > seg_vencimiento):
        vencimiento = seg_vencimiento
      
      interes_especial = True
      tipo_interes = 2
      
    '''------------------------------------------------------------------------
    --  si tipo_interes es null
    --     entonces me fijo en la tabla de configuracion
    ------------------------------------------------------------------------'''
    if not tipo_interes:
    
      interes = sitio.punitorios
      interes = Decimal(interes).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR)       
      tipo_interes = sitio.tipo_punitorios

      if tipo_interes == None:
        tipo_interes = 1 

    #tipo_interes = 1 MENSUAL se cobra interes si cambio el mes 
    if tipo_interes == 1:  
      #calculo la cantidad de meses que pasaron entre la fecha de punitorios y la de vencimiento
      try:
          meses = (fecha_punitorios - vencimiento).days / 30
      except:
          meses = 0
      if meses < 0:
          meses = 0 
      meses = Decimal(meses).quantize(Decimal("1"),decimal.ROUND_FLOOR)    
      coeficiente = interes * meses

      #Si se calculo un interes entre el primer y seg vencimiento y de ahi en adelante es tipo_interes 1 entonces viene con la marca interes_especial S
      if interes_especial:    
        coeficiente_acum += coeficiente
        tipo_interes = 3    

    #tipo_interes = 4 MENSUAL Si se paso 1 dia o mas del vencimiento se cobra un mes completo
    if tipo_interes == 4:  
      try:
          dias = (fecha_punitorios - vencimiento).days          
          meses = dias / 30
      except:
          dias = 0
          meses = 0
      if meses < 0:
          meses = 0 

      
      if (dias > 0):
        meses += 1    

      meses = Decimal(meses).quantize(Decimal("1"),decimal.ROUND_FLOOR)
      coeficiente = interes * meses
      if interes_especial:    
        coeficiente_acum += coeficiente
        tipo_interes = 3
      
    #tipo_interes = 2 DIARIO
    if tipo_interes == 2:  
      dv = (fecha_punitorios - vencimiento).days      
      interes = interes / 30 #paso el interes a diario
      interes = Decimal(interes).quantize(Decimal("0.000001"),decimal.ROUND_FLOOR) 

      coeficiente = dv * interes

      coeficiente = Decimal(coeficiente).quantize(Decimal("0.001"),decimal.ROUND_HALF_UP) 

      if interes_especial:        
        if coeficiente < 0:      
          coeficiente = 0
          coeficiente_acum = 0

        coeficiente_acum += coeficiente
        tipo_interes = 3      

      coeficiente_acum = Decimal(coeficiente_acum).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)      
        
      
    # Por si calcula los intereses en negativo que se da cuando la fecha punitorios es menor a vencimiento *
    if coeficiente < 0:
      coeficiente = 0

    #si el tipo es por rango de fechas
    if tipo_interes == 3:        
      coeficiente_acum = Decimal(coeficiente_acum).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)       
      intereses = importe * coeficiente_acum    
      coef = coeficiente_acum              
    else: #en cualquier otro caso  
      coeficiente = Decimal(coeficiente).quantize(Decimal("0.001"),decimal.ROUND_FLOOR) 
      intereses = importe * coeficiente    
      coef = coeficiente  

    coeficiente = Decimal(coeficiente).quantize(Decimal("0.001"),decimal.ROUND_HALF_UP)
    
    if intereses < 0:
      intereses = Decimal(0).quantize(Decimal("0.01"))
    else:
      intereses = Decimal(intereses).quantize(Decimal("0.01"),decimal.ROUND_HALF_UP) 


    if coef < 0:
      coef = Decimal(0).quantize(Decimal("0.001"),decimal.ROUND_FLOOR)
    
    if settings.DEBUG:
      print('importe:'+str(importe)+' coef:'+str(coef)+' interes:'+str(interes)+' dias:'+str(dias)+' total:'+str(intereses))

    return intereses
  # except Exception as e:
  #         print e.message    
  #         print 'importe:'+str(importe)+' coef:'+str(coef)+' interes:'+str(interes)+' dias:'+str(dias)+' total:'+str(intereses)
  #         return 0
