from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def create_from_dict(cls, dict_values):
        # Certifique-se de que dict_values é um dicionário
        if not isinstance(dict_values, dict):
            raise TypeError("dict_values deve ser um dicionário")
        
        # Filtre apenas os atributos que pertencem à classe cls
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(cls, k)}
        
        if not filtered_dict or len(filtered_dict) == 0:
            raise ValueError("No attributes found in the dictionary that belong to the class")
        
        # Crie uma instância da classe com os atributos filtrados
        return cls(**filtered_dict)

    def update_from_dict(self, dict_values):
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(self, k)}
        for key, value in filtered_dict.items():
            setattr(self, key, value)

            
# Este método cria todas as tabelas armazenadas na metadata no banco de dados conectado ao engine. As tabelas são criadas no banco de dados usando o engine fornecido. Se uma tabela já existe no banco de dados, o método create_all() irá ignorá-la.
# Base.metadata.create_all(engine)