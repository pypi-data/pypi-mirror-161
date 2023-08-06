from sqlalchemy.orm import relationship

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    Float,
    BLOB,
)

from .models import (
    AlphaTable,
    AlphaTableId,
    AlphaColumn,
    AlphaFloat,
    AlphaInteger,
    AlphaTableIdUpdateDate,
    AlphaTableUpdateDate,
)

from core import core, DB


class Test(DB.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "MAIN"
    __tablename__ = "test"

    id = AlphaColumn(Integer, autoincrement=True)

    name_ = AlphaColumn(String(30), primary_key=True)
    text_ = AlphaColumn(String(300))
    number_ = AlphaColumn(Integer)
    date_ = AlphaColumn(DateTime)

    test_child_id = AlphaColumn(
        "test_child_id", Integer, ForeignKey("test_child.id"), nullable=True
    )
    test_child = relationship("TestChild")

    test_childs = relationship("TestChilds", cascade="all,delete")


class TestChild(DB.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "MAIN"
    __tablename__ = "test_child"

    id = AlphaColumn(Integer, autoincrement=True)

    name_ = AlphaColumn(String(30), primary_key=True)
    text_ = AlphaColumn(String(300))
    number_ = AlphaColumn(Integer)
    date_ = AlphaColumn(DateTime)

    test_childs = relationship("TestChilds", cascade="all,delete")


class TestChilds(DB.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "MAIN"
    __tablename__ = "test_childs"

    id = AlphaColumn(Integer, autoincrement=True)

    parent_id = AlphaColumn(
        Integer, ForeignKey(f"{Test.__tablename__}.{Test.id.name}"), nullable=False,
    )
    child_parent_id = AlphaColumn(
        Integer,
        ForeignKey(f"{TestChild.__tablename__}.{TestChild.id.name}"),
        nullable=False,
    )

    name_ = AlphaColumn(String(30), primary_key=True)
    text_ = AlphaColumn(String(300))
    number_ = AlphaColumn(Integer)
    date_ = AlphaColumn(DateTime)

