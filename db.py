from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

DATABASE_URL="mysql+pymysql://8ExeRy4D2nNMPra.root:g0hJSAivkheANpTK@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test?ssl_ca=<CA_PATH>&ssl_verify_cert=true&ssl_verify_identity=true"
engine=create_engine( # this line use for setup a connection 
    DATABASE_URL, # database connection 
    pool_pre_ping=True, # check the connected databse ite connected or not 
    connect_args={"ssl":{"ssl":True}}
)

SessionLocal = sessionmaker(# we have to use this for write sql queries or nay update or delete 
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base=declarative_base()# thia is use for creating a tables 