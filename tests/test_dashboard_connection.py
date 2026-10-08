import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('fleet_dashboard_db',Path(__file__).resolve().parents[1]/'dashboard_streamlit/utils/db.py')
db=importlib.util.module_from_spec(spec);spec.loader.exec_module(db)

def test_password_reserved_characters_are_preserved(monkeypatch):
    monkeypatch.setattr(db,'_get_cfg',lambda:{'user':'user@demo','password':'fake@:/#?','host':'localhost','port':'5432','dbname':'fleetlogix'})
    engine=db.get_engine.__wrapped__()
    assert engine.url.password=='fake@:/#?' and engine.url.username=='user@demo'
    engine.dispose()
