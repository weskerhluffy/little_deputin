'''
Created on 14/12/2016

@author:
'''

import logging
import sys
nivel_log = logging.ERROR
#nivel_log = logging.DEBUG
logger_cagada = None

# http://stackoverflow.com/questions/280243/python-linked-list
def ordenamiento_mezcla_merge(numeros, idx_a, idx_b, tam_a, tam_b):
    numeros_mergeados = []
    idx_a_tmp = idx_a
    idx_b_tmp = idx_b
    logger_cagada.debug("el lado a %u-%u %s lado b %u-%u %s" % (idx_a, tam_a, numeros[idx_a:idx_a + tam_a], idx_b, tam_b, numeros[idx_b:idx_b + tam_b]))
    while(idx_a_tmp < (idx_a + tam_a) or idx_b_tmp < (idx_b + tam_b)):
        logger_cagada.debug("idx a %u idx b %u de %s" % (idx_a_tmp, idx_b_tmp, numeros[idx_a:idx_b + tam_b]))
#        assert idx_a_tmp < len(numeros), "el idx a se sobrepaso %u" % idx_a_tmp
#        assert idx_b_tmp < len(numeros), "el idx b se sobrepaso %u" % idx_b_tmp
        num_a = None
        num_b = None
        
        if(idx_a_tmp < (idx_a + tam_a)):
            num_a = numeros[idx_a_tmp]
        if(idx_b_tmp < (idx_b + tam_b)):
            num_b = numeros[idx_b_tmp]
            
        logger_cagada.debug("num a %s num b %s" % (num_a, num_b))
        if(num_a is not None and num_b is not None):
            if(num_a <= num_b):
                numeros_mergeados.append(num_a)
                idx_a_tmp += 1
            else:
                numeros_mergeados.append(num_b)
                idx_b_tmp += 1
        else:
            if(num_a is None and num_b is None):
                break
            
            if(num_a is not None):
                numeros_mergeados.append(num_a)
                idx_a_tmp += 1
            
            if(num_b is not None):
                numeros_mergeados.append(num_b)
                idx_b_tmp += 1
            

    logger_cagada.debug("los nums mergeados %s" % numeros_mergeados)
    idx_a_tmp = idx_a
    for nume in numeros_mergeados:
        numeros[idx_a_tmp] = nume
        idx_a_tmp += 1

def ordenamiento_mezcla(numeros, idx_ini, idx_fin):
    if(idx_ini == idx_fin):
        return numeros
    idx_med = (idx_fin - idx_ini) // 2
    logger_cagada.debug("idx_med %s" % idx_med)
    logger_cagada.debug("ordenando lado a %u:%u %s" % (idx_ini, idx_ini + idx_med, numeros[idx_ini: idx_ini + idx_med]))
    ordenamiento_mezcla(numeros, idx_ini, idx_ini + idx_med)
    logger_cagada.debug("ordenando lado b %u:%u %s" % (idx_ini + idx_med + 1, idx_fin, numeros[idx_ini + idx_med + 1: idx_fin]))
    ordenamiento_mezcla(numeros, idx_ini + idx_med + 1, idx_fin)
    ordenamiento_mezcla_merge(numeros, idx_ini, idx_ini + idx_med + 1, idx_med + 1, (idx_fin - idx_ini) - idx_med)
    return numeros

def pekeno_deputo_core(numeros):
    conta_cacas = 0
    tam_nums = len(numeros)
#    numeros_ord = sorted(numeros)
    numeros_ord = ordenamiento_mezcla(numeros, 0, len(numeros) - 1)
 
    logger_cagada.debug("numeros ord %s" % numeros_ord)
 
    conta_cacas = 1
    max_conta_cacas = 0
 
    num_ant = numeros_ord[0]
 
    for nume in numeros_ord[1:]:
        if(nume > num_ant):
            conta_cacas = 1
        else:
            conta_cacas += 1
 
        logger_cagada.debug("el num %u tiene cont %u" % (nume, conta_cacas))
 
        if(max_conta_cacas < conta_cacas):
            logger_cagada.debug("el max cont de %u a %u" % (max_conta_cacas, conta_cacas))
            max_conta_cacas = conta_cacas
          
        num_ant = nume
 
    if(not max_conta_cacas):
        max_conta_cacas = 1
 
    return max_conta_cacas


def pekeno_deputo_main():
    
    num_casos = int(sys.stdin.readline())
    logger_cagada.debug("el num de cacasos %u" % num_casos)
    
    for _ in range(num_casos):
        numeros = []
        
        num_numeros = int(sys.stdin.readline())
        logger_cagada.debug("num de nums %u" % num_numeros)
        
        for num_num in range(num_numeros):
            num_act = int(sys.stdin.readline())
            numeros.append(num_act)
        
        logger_cagada.debug("los nums del caso actual %s" % numeros)
        
        pinche = pekeno_deputo_core(numeros)
        
        logger_cagada.debug("las cacas necesarias %u" % pinche)
        print("%u" % pinche)

if __name__ == '__main__':
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(level=nivel_log, format=FORMAT)
        logger_cagada = logging.getLogger("asa")
        logger_cagada.setLevel(nivel_log)   
        pekeno_deputo_main()
