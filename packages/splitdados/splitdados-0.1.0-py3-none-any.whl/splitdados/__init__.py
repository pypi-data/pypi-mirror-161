__version__ = '0.1.0'
def puxaDados(string,valor1,valor2):

    puxa1 = string.split(valor1)[1][0:]
    resultado = puxa1.split(valor2)[0][0:]
    return resultado