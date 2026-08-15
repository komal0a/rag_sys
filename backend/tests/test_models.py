import importlib.util
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

spec = importlib.util.spec_from_file_location(
    "models",
    str(Path(__file__).parent.parent / "app" / "models.py"),
)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

engine = create_engine("sqlite:///:memory:")
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def test_crud_models():
    s = Session()
    # create user
    user = models.User(email="test@example.com", hashed_password="hash")
    s.add(user)
    s.commit()
    s.refresh(user)
    assert user.id is not None

    # create document
    doc = models.Document(user_id=user.id, filename="doc.pdf", num_pages=2)
    s.add(doc)
    s.commit()
    s.refresh(doc)
    assert doc.id is not None

    # create chunk
    chunk = models.DocumentChunk(document_id=doc.id, chunk_index=0, page_number=1, content="hello world")
    s.add(chunk)
    s.commit()
    s.refresh(chunk)
    assert chunk.id is not None

    # conversation & message
    conv = models.Conversation(user_id=user.id, title="conv1")
    s.add(conv)
    s.commit()
    s.refresh(conv)

    msg = models.Message(conversation_id=conv.id, sender="user", content="hi")
    s.add(msg)
    s.commit()
    s.refresh(msg)
    assert msg.id is not None

    s.close()
