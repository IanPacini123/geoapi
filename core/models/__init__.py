from core.banco_dados import Base
from core.models.ibge_models import Pais, Regiao, Uf, Mesorregiao, Microrregiao, RegiaoIntermediaria, RegiaoImediata, Municipio, TipoLogradouro
from core.models.cep_model import Cep
from core.models.auditoria_model import AuditoriaRequisicao
from core.models.sistema_autorizado_model import SistemaAutorizado

# Isso garante que todos os modelos sejam carregados quando Base for importado daqui
