
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    rol = Column(String(50), nullable=False, default="Admisión")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    especialidad = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(10), nullable=False)
    motivo = Column(String(250), nullable=True)
    estado = Column(String(30), nullable=False, default="Pendiente")


class HistoriaClinica(Base):
    __tablename__ = "historias_clinicas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    antecedentes = Column(Text, nullable=True)
    diagnostico = Column(Text, nullable=True)
    tratamiento = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)