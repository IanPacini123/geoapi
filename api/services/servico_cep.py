import re
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from api.repositorios.repositorio_cep import RepositorioCep
from api.services.clientes.clientes_cep import BrasilApiClient, ViaCepClient, CepClientException
from core.models.ibge_models import Uf, Municipio, TipoLogradouro
from core.models.cep_model import Cep

logger = logging.getLogger(__name__)

class ServicoCep:
    """
    Servico responsavel por buscar e enriquecer dados de CEP usando o padrao Cache-aside.
    Service responsible for fetching and enriching CEP data using a Cache-aside padrao.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repository = RepositorioCep(db)

    async def buscar_cep(self, cep_bruto: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados de CEP em APIs externas e atualiza o cache local (upsert).
        Se as APIs externas falharem, faz fallback para o banco de dados local.
        Fetches CEP data from external APIs and updates the local cache (upsert).
        If external APIs fail, falls back to the local database.

        Args:
            cep_bruto (str): The raw CEP string.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with the enriched CEP data, or None if not found.
        
        Raises:
            ValueError: If the CEP is invalid (not 8 digits).
        """
        cep = re.sub(r"\D", "", cep_bruto)
        if len(cep) != 8:
            raise ValueError("CEP invalido")

        dados_externos = None
        try:
            dados_externos = await BrasilApiClient.buscar(cep)
        except CepClientException as e:
            logger.warning(f"BrasilAPI failed for CEP {cep}. Error: {e}")

        if not dados_externos:
            try:
                dados_externos = await ViaCepClient.buscar(cep)
            except CepClientException as e:
                logger.warning(f"ViaCep failed for CEP {cep}. Error: {e}")
        
        if not dados_externos:
            cep_local = self.repository.get_by_cep(cep)
            if cep_local:
                return self._para_dicionario(cep_local)
            return None

        codigo_uf = None
        codigo_municipio = None
        codigo_tipo_logradouro = None

        if dados_externos.get("uf"):
            uf_bd = self.db.query(Uf).filter(Uf.sigla == dados_externos["uf"].upper()).first()
            if uf_bd:
                codigo_uf = uf_bd.id
                
                if dados_externos.get("localidade"):
                    mun_bd_simples = self.db.query(Municipio).filter(Municipio.nome.ilike(dados_externos["localidade"])).first()
                    if mun_bd_simples:
                        codigo_municipio = mun_bd_simples.id

        if dados_externos.get("logradouro"):
            primeira_palavra = dados_externos["logradouro"].split(" ")[0].strip()
            tipo_log_bd = self.db.query(TipoLogradouro).filter(
                or_(
                    TipoLogradouro.descricao.ilike(primeira_palavra),
                    TipoLogradouro.sigla.ilike(primeira_palavra)
                )
            ).first()
            if tipo_log_bd:
                codigo_tipo_logradouro = tipo_log_bd.id

        cep_local = self.repository.get_by_cep(cep)
        
        if cep_local:
            modificado = False
            if cep_local.logradouro != dados_externos.get("logradouro"): 
                cep_local.logradouro = dados_externos.get("logradouro")
                modificado = True
            if cep_local.bairro != dados_externos.get("bairro"): 
                cep_local.bairro = dados_externos.get("bairro")
                modificado = True
            if cep_local.localidade != dados_externos.get("localidade"): 
                cep_local.localidade = dados_externos.get("localidade")
                modificado = True
            if cep_local.uf != dados_externos.get("uf"): 
                cep_local.uf = dados_externos.get("uf")
                modificado = True
            if cep_local.uf_codigo != codigo_uf: 
                cep_local.uf_codigo = codigo_uf
                modificado = True
            if cep_local.municipio_codigo != codigo_municipio: 
                cep_local.municipio_codigo = codigo_municipio
                modificado = True
            if cep_local.tipo_logradouro_codigo != codigo_tipo_logradouro: 
                cep_local.tipo_logradouro_codigo = codigo_tipo_logradouro
                modificado = True
            
            if modificado:
                cep_local.data_criacao = datetime.utcnow()
                self.db.commit()
                
            return self._para_dicionario(cep_local)
        else:
            novo_cep = Cep(
                cep=cep,
                logradouro=dados_externos.get("logradouro"),
                bairro=dados_externos.get("bairro"),
                localidade=dados_externos.get("localidade"),
                uf=dados_externos.get("uf"),
                uf_codigo=codigo_uf,
                municipio_codigo=codigo_municipio,
                tipo_logradouro_codigo=codigo_tipo_logradouro
            )
            salvo = self.repository.create(novo_cep)
            return self._para_dicionario(salvo)

    def _para_dicionario(self, modelo_cep: Cep) -> Dict[str, Any]:
        """
        Converte uma instancia do modelo Cep para um dicionario.
        Converts a Cep model instance to a dictionary.
        """
        return {
            "cep": modelo_cep.cep,
            "logradouro": modelo_cep.logradouro,
            "bairro": modelo_cep.bairro,
            "localidade": modelo_cep.localidade,
            "uf": modelo_cep.uf,
            "uf_codigo": modelo_cep.uf_rel.codigo_ibge if modelo_cep.uf_rel else None,
            "municipio_codigo": modelo_cep.municipio_rel.codigo_ibge if modelo_cep.municipio_rel else None,
            "tipo_logradouro_codigo": modelo_cep.tipo_logradouro_rel.id if modelo_cep.tipo_logradouro_rel else None,
            "data_criacao": modelo_cep.data_criacao.isoformat() if modelo_cep.data_criacao else None
        }
