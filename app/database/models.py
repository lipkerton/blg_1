from sqlalchemy import BigInteger, String, Text, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "post"
    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    content: Mapped[str] = mapped_column(Text())

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="chk_length_title"),
        CheckConstraint("length(content) > 0", name="chk_length_content")
    )
