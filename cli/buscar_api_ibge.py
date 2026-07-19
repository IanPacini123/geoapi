from callers.uf_caller import UFCaller
from callers.regiao_caller import RegiaoCaller
from callers.mesorregiao_caller import MesorregiaoCaller
from callers.microrregiao_caller import MicrorregiaoCaller
from callers.regiao_intermediaria_caller import RegiaoIntermediariaCaller
from callers.regiao_imediata_caller import RegiaoImediataCaller
from callers.municipio_caller import MunicipioCaller
from callers.pais_caller import PaisCaller

def main():
    print("Iniciando a busca de dados no IBGE...")
    
    RegiaoCaller().coletar()
    UFCaller().coletar()
    MesorregiaoCaller().coletar()
    MicrorregiaoCaller().coletar()
    RegiaoIntermediariaCaller().coletar()
    RegiaoImediataCaller().coletar()
    MunicipioCaller().coletar()
    PaisCaller().coletar()

if __name__ == "__main__":
    main()
