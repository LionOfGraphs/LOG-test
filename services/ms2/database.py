from decouple import config
from sqlalchemy import Boolean, Column, Engine, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists

SETTINGS = {
    "user": config("PGUSER"),
    "password": config("PGPASSWORD"),
    "host": config("PGHOST"),
    "port": config("PGPORT", cast=int),
    "db": config("PGDB"),
}

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    user_id = Column(
        "user_id", Integer, primary_key=True, unique=True, autoincrement=True
    )
    username = Column("username", String)
    usertype = Column("usertype", String)
    fullname = Column("fullname", String)
    email = Column("email", String)
    hashed_password = Column("hashed_password", String)
    disabled = Column("disabled", Boolean)

    def __init__(
        self, user_id, username, usertype, fullname, email, hashed_password, disabled
    ) -> None:
        self.user_id = user_id
        self.username = username
        self.usertype = usertype
        self.fullname = fullname
        self.email = email
        self.hashed_password = hashed_password
        self.disabled = disabled

    def __repr__(self):
        return "[ {} | {} ] type: {} | fullname: {} | disabled: {}".format(
            self.user_id, self.username, self.usertype, self.fullname, self.disabled
        )


class DB_Session:
    """
    Database Session Object
    """

    def __init__(self) -> None:
        self.user = config("PGUSER")
        self.password = config("PGPASSWORD")
        self.host = config("PGHOST")
        self.port = config("PGPORT", cast=int)
        self.db = config("PGDB")

        self.engine = self.get_engine()
        self.session = self.get_session()

    def get_engine(self) -> Engine:
        url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        if not database_exists(url):
            create_database(url)
        engine = create_engine(url)
        return engine

    def get_session(self) -> Session:
        Base.metadata.create_all(bind=self.engine, checkfirst=True)

        session = sessionmaker(bind=self.engine)()
        return session

    def get_user_by_username(self, username: str) -> User:
        user = self.session.query(User).filter(User.username == username).first()
        return user

    def get_user_by_user_id(self, user_id: int) -> User:
        user = self.session.query(User).filter(User.user_id == user_id).first()
        return user

    def get_user_hash(self, username: str) -> str:
        user = self.session.query(User).filter(User.username == username).first()
        if user:
            return user.hashed_password
        else:
            return None


# user0 = User(user_id=1,
#              username="admin",
#              usertype="admin",
#               fullname="Administrator",
#              email="admin@log.com",
#              hashed_password="$2b$12$5WLUvQ5ws7DTuyqbl/0kIOxOtx9My0AqiR61TZH6EAO5CY0nFpEwW",
#              disabled=False)
# session.add(user0)
# session.commit()
