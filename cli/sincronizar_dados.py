import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "cli"))

import shutil
import pandas as pd
from sqlalchemy.orm import Session
from core.banco_dados import SessionLocal

from core.models.ibge_models import (
    Pais, Regiao, Uf, Mesorregiao, Microrregiao, 
    RegiaoIntermediaria, RegiaoImediata, Municipio
)
from cli.buscar_api_ibge import main as coletar_ibge

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "cli", "exports")
VIGENCIA_DIR = os.path.join(BASE_DIR, "data", "vigencia")

ORDEM_ARQUIVOS = [
    ("paises_ibge.csv", Pais, None),
    ("regioes_ibge.csv", Regiao, {"sigla": "SIGLA"}),
    ("estados_ibge.csv", Uf, {"sigla": "SIGLA", "fk": ("regiao_id", Regiao, "ID_REGIAO")}),
    ("mesorregioes_ibge.csv", Mesorregiao, {"fk": ("uf_id", Uf, "ID_UF")}),
    ("microrregioes_ibge.csv", Microrregiao, {"fk": ("mesorregiao_id", Mesorregiao, "ID_MESORREGIAO")}),
    ("regioes_intermediarias_ibge.csv", RegiaoIntermediaria, {"fk": ("uf_id", Uf, "ID_UF")}),
    ("regioes_imediatas_ibge.csv", RegiaoImediata, {"fk": ("regiao_intermediaria_id", RegiaoIntermediaria, "ID_REGIAO_INTERMEDIARIA")}),
    ("municipios_ibge.csv", Municipio, {"fk1": ("microrregiao_id", Microrregiao, "ID_MICRORREGIAO"), 
                                        "fk2": ("regiao_imediata_id", RegiaoImediata, "ID_REGIAO_IMEDIATA")})
]

def load_vigencia(filename: str) -> pd.DataFrame:
    filepath = os.path.join(VIGENCIA_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath, dtype=str, skipinitialspace=True).fillna("")
    return pd.DataFrame()

def save_vigencia(filename: str):
    os.makedirs(VIGENCIA_DIR, exist_ok=True)
    shutil.copy2(os.path.join(EXPORTS_DIR, filename), os.path.join(VIGENCIA_DIR, filename))

def processar_diff_e_salvar(db: Session, filename: str, model, mappings: dict | None):
    novo_df = pd.read_csv(os.path.join(EXPORTS_DIR, filename), dtype=str, skipinitialspace=True).fillna("")
    novo_df.columns = novo_df.columns.str.strip()
    
    antigo_df = load_vigencia(filename)
    
    # TRUQUE DE RESILIENCIA: Se o banco foi apagado (ex: docker-compose down -v),
    # mas a pasta 'vigencia' sobreviveu, precisamos forcar a re-importacao de tudo.
    if db.query(model).count() == 0:
        print(f"[{filename}] Banco de dados vazio para esta entidade. Forcando sincronizacao completa.")
        antigo_df = pd.DataFrame()
    
    if not antigo_df.empty:
        antigo_df.columns = antigo_df.columns.str.strip()
    
    if not antigo_df.empty:
        diff_df = novo_df.merge(antigo_df, how='outer', indicator=True)
        mudancas = diff_df[diff_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    else:
        mudancas = novo_df
        
    if mudancas.empty:
        print(f"[{filename}] Nenhuma mudanca detectada.")
        return False

    print(f"[{filename}] Detectado {len(mudancas)} alteracoes/insercoes. Sincronizando...")
    
    for _, row in mudancas.iterrows():
        raw_id = str(row['ID']).strip()
        if not raw_id or raw_id == 'None':
            cod_ibge = abs(hash(row.get('NOME', 'unknown'))) % 1000000
        else:
            cod_ibge = int(raw_id)
        
        obj = db.query(model).filter(model.codigo_ibge == cod_ibge).first()
        if not obj:
            obj = model(codigo_ibge=cod_ibge)
            db.add(obj)
            
        obj.nome = row.get('NOME', str(cod_ibge))
        
        if mappings:
            if "sigla" in mappings and mappings["sigla"] in row:
                obj.sigla = row[mappings["sigla"]]
            
            if "fk" in mappings:
                local_col, f_model, csv_col = mappings["fk"]
                if csv_col in row and row[csv_col]:
                    f_obj = db.query(f_model).filter(f_model.codigo_ibge == int(row[csv_col])).first()
                    if f_obj:
                        setattr(obj, local_col, f_obj.id)
            
            if "fk1" in mappings:
                local_col, f_model, csv_col = mappings["fk1"]
                if csv_col in row and row[csv_col]:
                    f_obj = db.query(f_model).filter(f_model.codigo_ibge == int(row[csv_col])).first()
                    if f_obj:
                        setattr(obj, local_col, f_obj.id)
            if "fk2" in mappings:
                local_col, f_model, csv_col = mappings["fk2"]
                if csv_col in row and row[csv_col]:
                    f_obj = db.query(f_model).filter(f_model.codigo_ibge == int(row[csv_col])).first()
                    if f_obj:
                        setattr(obj, local_col, f_obj.id)

    db.commit()
    return True

def popular_tipos_logradouro(db: Session):
    from core.models.ibge_models import TipoLogradouro
    
    tipos = [
        ("Aeroporto", "Aer"), ("Alameda", "Al"), ("Area", "A"), ("Avenida", "Av"), 
        ("Campo", "Cpo"), ("Chacara", "Ch"), ("Colonia", "Col"), ("Condominio", "Cond"), 
        ("Conjunto", "Conj"), ("Distrito", "Dist"), ("Esplanada", "Esp"), ("Estacao", "Est"), 
        ("Estrada", "Estr"), ("Favela", "Fav"), ("Fazenda", "Faz"), ("Feira", "Feira"), 
        ("Jardim", "Jd"), ("Ladeira", "Lad"), ("Lago", "Lago"), ("Lagoa", "Lagoa"), 
        ("Largo", "Lgo"), ("Loteamento", "Lot"), ("Morro", "Morro"), ("Nucleo", "Nuc"), 
        ("Parque", "Pq"), ("Passarela", "Pass"), ("Patio", "Pat"), ("Praca", "Pc"), 
        ("Quadra", "Qd"), ("Recanto", "Rec"), ("Residencial", "Res"), ("Rodovia", "Rod"), 
        ("Rua", "R"), ("Setor", "St"), ("Sitio", "Sit"), ("Travessa", "Tv"), 
        ("Trecho", "Tre"), ("Trevo", "Trv"), ("Vale", "Vale"), ("Vereda", "Ver"), 
        ("Via", "Via"), ("Viaduto", "Vd"), ("Viela", "Vla"), ("Vila", "Vl")
    ]
    
    print("Sincronizando Tipos de Logradouro (Correios)...")
    inseridos = 0
    for desc, sigla in tipos:
        existe = db.query(TipoLogradouro).filter(TipoLogradouro.descricao == desc).first()
        if not existe:
            db.add(TipoLogradouro(descricao=desc, sigla=sigla))
            inseridos += 1
            
    if inseridos > 0:
        db.commit()
        print(f"[{inseridos}] Novos tipos de logradouro inseridos com sucesso!")
    else:
        print("[0] Nenhuma mudanca detectada nos Tipos de Logradouro.")




def invalidar_cache_redis():
    import asyncio
    from core.cache import cache_service
    print("\n[Cache] Invalidando chaves defasadas no Redis...")
    async def flush_all_domain_keys():
        await cache_service.deletar_padrao("municipios:v1:*")
        await cache_service.deletar_padrao("ufs:v1:*")
        await cache_service.deletar_padrao("paises:v1:*")
        await cache_service.deletar_padrao("regioes:v1:*")
        await cache_service.deletar_padrao("regioes_imediatas:v1:*")
        await cache_service.deletar_padrao("regioes_intermediarias:v1:*")
        await cache_service.deletar_padrao("mesorregioes:v1:*")
        await cache_service.deletar_padrao("microrregioes:v1:*")
    asyncio.run(flush_all_domain_keys())
    print("[Cache] Chaves invalidadas com sucesso.")


def main():
    print("Iniciando rotina de coleta do IBGE...")
    coletar_ibge()
    
    print("\nIniciando sincronizacao inteligente com PostgreSQL...")
    from core.banco_dados import Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        popular_tipos_logradouro(db)
        
        teve_mudanca = False
        for filename, model, mappings in ORDEM_ARQUIVOS:
            mudou = processar_diff_e_salvar(db, filename, model, mappings)
            if mudou:
                teve_mudanca = True
            save_vigencia(filename)
            
        print("\nSincronizacao concluida com sucesso!")
        if teve_mudanca:
            invalidar_cache_redis()
        else:
            print("[Cache] Nenhuma mudanca nos dados. Invalidacao do cache ignorada.")
    except Exception as e:
        print(f"Erro na sincronizacao: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
