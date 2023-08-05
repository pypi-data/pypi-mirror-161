from __future__ import annotations
_A=None
import json,logging,sqlite3
from abc import ABC
from typing import Any,Dict,Final,List,Optional,Set,Tuple
from localstack.utils.files import new_tmp_file,save_file
from localstack.utils.strings import long_uid,to_bytes,to_str
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AssetByNameType,AssetNameType,AssetValueType
from localstack_ext.bootstrap.state_merge import merge_3way
LOG=logging.getLogger(__name__)
class DDBAttribute:
	_PRIMARY_KEY='PRIMARY KEY';_NOT_NULLABLE='NOT NULL';_DEFAULT='DEFAULT';_NULL='NULL';_TEXT_TYPES={'TEXT'};_NUMERIC_TYPES={'NUMERIC','BOOLEAN','DATE','DATETIME'};_INTEGER_TYPES={'INT','INTEGER'};_REAL_TYPES={'REAL','DOUBLE','FLOAT'};_BLOB_TYPES={'BLOB'}
	def __init__(A,name,typ,nullable,default,primary):A.name=name;A.typ=typ;A.nullable=nullable;A.default=default;A.primary=primary
	@classmethod
	def from_table_info(B,table_info):A=table_info;C=str(A[1]);D=str(A[2]);E=not bool(A[3]);F=A[4];G=bool(A[5]);return B(C,D,E,F,G)
	def _get_well_typed_default(A):
		if A.default is _A:return _A
		B=A._default_of_typ(A.typ);C=type(B);return A._try_cast_to_type_value(C,A.default,B)
	def get_schema(A):
		B=[A.name,A.typ]
		if not A.nullable:B.append(A._NOT_NULLABLE)
		if A.default:B.extend([A._DEFAULT,A.default])
		return ' '.join(B).strip()
	def __str__(A):return A.get_schema()
	def _default_of_typ(A,typ_name):
		B=typ_name
		if B in A._TEXT_TYPES:return str()
		elif B in A._BLOB_TYPES:return bytes()
		elif B in{*A._NUMERIC_TYPES,*A._INTEGER_TYPES}:return int()
		elif B in A._REAL_TYPES:return float()
		else:LOG.warning(f"No type affinities found for type {B}");return _A
	def _try_cast_to_type_value(C,typ,value,def_value):
		B=def_value;A=value
		if A:
			try:
				if isinstance(A,str)and isinstance(B,bytes):return to_bytes(A)
				elif isinstance(A,bytes)and isinstance(B,str):return A
				else:return typ(A)
			except Exception as D:LOG.warning(f"Cannot update value type of '{A}' '{typ}' to be a {C.typ}, hence replaced it with default {B}, error: {D}")
		return B
	def to_compatible_type_value(A,value):
		B=value
		if B is _A and A.nullable:return B
		if B is _A and A.default is not _A:return A.default
		C=A._get_well_typed_default()if A.default is not _A else A._default_of_typ(A.typ);D=type(C);E=type(B)
		if D==E:return B
		else:return A._try_cast_to_type_value(D,B,C)
class DDBIndex:
	def __init__(A,index_name,is_unique,table_name,field_by_index):A.index_name=index_name;A.is_unique=is_unique;A.table_name=table_name;A.field_by_index=field_by_index
	@classmethod
	def from_database(B,index_name,is_unique,table_name,cur):A=index_name;C=DDBIndex._load_fields_by_index(A,cur);return B(A,is_unique,table_name,C)
	@classmethod
	def from_index_list_entry(B,index_spec,table_name,cur):
		A=index_spec
		if A[3]!='c':return _A
		C=str(A[1]);D=bool(A[2]);return B.from_database(C,D,table_name,cur)
	@staticmethod
	def indexes_by_name_of_table(table_name,cur):
		C=table_name;A=cur;E=DDBIndex._sqlite_indexes_of_table(C);A.execute(E);F=A.fetchall();D={}
		for G in F:
			B=DDBIndex.from_index_list_entry(G,C,A)
			if B:D[B.index_name]=B
		return D
	@staticmethod
	def _load_fields_by_index(index_name,cur):
		C=DDBIndex._sqlite_index_info(index_name);cur.execute(C);D=cur.fetchall();A={}
		for B in D:E=int(B[0]);F=str(B[-1]);A[E]=F
		return A
	@staticmethod
	def _sqlite_index_info(index_name):return f'PRAGMA index_info("{index_name}");'
	@staticmethod
	def _sqlite_indexes_of_table(table_name):return f'PRAGMA index_list("{table_name}");'
	def get_create_statement(A,attribute_names):
		E='UNIQUE INDEX'if A.is_unique else'INDEX';B=[A.field_by_index[B]for B in range(len(A.field_by_index))];C=[]
		for D in B:
			if D in attribute_names:C.append(D)
		if C:F=','.join([f'"{A}"'for A in B]);return f'CREATE {E} "{A.index_name}" ON "{A.table_name}" ({F});'
		return _A
class DDBTableSchema:
	def __init__(A,table_name,attributes_by_name,og_schema):A.table_name=table_name;A._attributes_by_name=attributes_by_name;A._og_schema=og_schema
	@classmethod
	def from_database(B,table_name,cur):A=table_name;C=DDBTableSchema._load_fields(A,cur);D=DDBTableSchema._load_og_schema(A,cur);return B(A,C,D)
	@staticmethod
	def _sqlite_table_info(table_name):return f'PRAGMA table_info("{table_name}");'
	@staticmethod
	def _sqlite_table_schema(table_name):return f'SELECT sql FROM sqlite_master WHERE tbl_name="{table_name}" LIMIT 1;'
	@staticmethod
	def _load_fields(table_name,cur):
		C=DDBTableSchema._sqlite_table_info(table_name);cur.execute(C);D=cur.fetchall();A={}
		for E in D:B=DDBAttribute.from_table_info(E);A[B.name]=B
		return A
	@staticmethod
	def _load_og_schema(table_name,cur):A=DDBTableSchema._sqlite_table_schema(table_name);cur.execute(A);B=cur.fetchall();C=B[0][0];return C
	def get_attributes(A):return A._attributes_by_name
	def get_attribute_names(B):
		A=[]
		for C in B._attributes_by_name.values():A.append(C.name)
		return A
	def _get_primary_key_stmt(C):
		A=_A;B=[f'"{A.name}"'for A in C._attributes_by_name.values()if A.primary]
		if B:D=','.join(B);A=f"PRIMARY KEY ({D})"
		return A
	def get_schema(A):
		D=f'CREATE TABLE "{A.table_name}"';B=[B.get_schema()for B in A._attributes_by_name.values()];C=A._get_primary_key_stmt()
		if C:B.append(C)
		E=','.join(B);F=f"{D} ({E});";return F
	def get_insert_statement(A):B=','.join(A._attributes_by_name.keys());C=','.join(['?']*len(A._attributes_by_name));D=f'INSERT INTO "{A.table_name}" ({B}) VALUES ({C});';return D
	def __str__(A):return A.get_schema()
class DDBField(ABC):
	def get_value(A):...
class DDBFieldValue(DDBField):
	def __init__(A,value):A._value=value
	def get_value(A):return A._value
class DDBFieldJSON(DDBField):
	def __init__(A,json_value):B=to_str(json_value);A._json_obj=json.loads(B)
	def get_value(A):B=json.dumps(A._json_obj);return to_bytes(B)
class DDBFieldObjectJSON(DDBFieldJSON):0
class DDBFieldDMTableInfo(DDBFieldJSON):0
class DDBFieldFactory:
	@staticmethod
	def ddb_field_of(table_name,attribute_name,value):
		B=value;A:0
		match(table_name,attribute_name):
			case _,'ObjectJSON':A=DDBFieldObjectJSON(B)
			case'dm','TableInfo':A=DDBFieldDMTableInfo(B)
			case _:A=DDBFieldValue(B)
		return A
class DDBRecord:
	def __init__(A,schema,record):B=schema;A.fields_by_name=A._load_fields_by_name(B,record);A.primary_id=A._derive_primary_id(B,A.fields_by_name)
	@staticmethod
	def _derive_primary_id(schema,field_by_name):A=schema.get_attributes().values();B=[B.name for B in A if B.primary]or[B.name for B in A];C=[str(field_by_name[A].get_value())for A in B];D='-'.join(C);return D
	@staticmethod
	def _load_fields_by_name(schema,record):
		A=schema;D=A.table_name;B={};E=A.get_attributes()
		for (F,C) in enumerate(E.keys()):G=record[F];H=DDBFieldFactory.ddb_field_of(D,C,G);B[C]=H
		return B
	def get_insert_tuple(C,schema):
		A=[];D=schema.get_attributes()
		for (E,F) in D.items():B=C.fields_by_name.get(E,_A);G=B.get_value()if B else _A;H=F.to_compatible_type_value(G);A.append(H)
		return tuple(A)
class DDBTable:
	def __init__(A,table_name,schema,index_by_name):A._table_name=table_name;A._schema=schema;A._index_by_name=index_by_name;A._records_by_primary_id={}
	@classmethod
	def from_database(B,table_name,cur):A=table_name;C=DDBTableSchema.from_database(A,cur);D=DDBIndex.indexes_by_name_of_table(A,cur);return B(A,C,D)
	@staticmethod
	def _sql_select_all(table_name):return f'SELECT * FROM "{table_name}";'
	def offload_records(A):A._records_by_primary_id.clear()
	def load_records(A,cur):
		A.offload_records();C=A._sql_select_all(A._table_name);cur.execute(C);D=cur.fetchall()
		for E in D:B=DDBRecord(A._schema,E);A._records_by_primary_id[B.primary_id]=B
	def get_table_name(A):return A._table_name
	def set_table_name(A,table_name):B=table_name;A._table_name=B;A._schema.table_name=B
	def get_table_schema(A):return A._schema
	def dump_records(A,cur):
		if not A._records_by_primary_id:return
		C=A._schema.get_insert_statement()
		for B in A._records_by_primary_id.values():
			D=B.get_insert_tuple(A._schema)
			try:cur.execute(C,D)
			except Exception as E:LOG.warning(f"Could not insert record {B} after merge: {E}")
	def dump_indexes(A,cur):
		D=set(A._schema.get_attributes().keys())
		for B in A._index_by_name.values():
			C=B.get_create_statement(D)
			if C:
				try:cur.execute(C)
				except Exception as E:LOG.warning(f"Could not create index {B} after merge: {E}")
class DDBDatabase:
	_SQLITE_GET_TABLES='SELECT name FROM sqlite_master WHERE type="table";';_SQLITE_GET_INDEXES='SELECT name FROM sqlite_master WHERE type="index";';_SQLITE_GET_VIEWS='SELECT name FROM sqlite_schema WHERE type = "view";'
	def __init__(A,file_path):A._con=sqlite3.connect(file_path);A._con.text_factory=lambda x:to_str(x)if x else _A;A._cur=A._con.cursor();A._tables_by_name=A._find_tables()
	def _find_tables(A):
		A._cur.execute(A._SQLITE_GET_TABLES);D=A._cur.fetchall();B={}
		for E in D:C=E[0];B[C]=DDBTable.from_database(C,A._cur)
		return B
	def close(A):A._cur.close();A._con.close()
	def commit(A):A._con.commit()
	def commit_and_close(A):A.commit();A.close()
	@staticmethod
	def _generate_table_tmp_name(table):return f"{table.get_table_name()}_{long_uid().replace('-','_')}"
	@staticmethod
	def _sql_delete_table(table_name):return f'DROP TABLE IF EXISTS "{table_name}";'
	@staticmethod
	def _sql_rename_table(table_name,new_table_name):return f'ALTER TABLE "{table_name}" RENAME TO "{new_table_name}";'
	@staticmethod
	def _sql_pragma_check_constraints(enabled):A='FALSE'if enabled else'TRUE';return f"PRAGMA ignore_check_constraints={A};"
	def _pragma_constraints_enable(A):B=A._sql_pragma_check_constraints(True);A._cur.execute(B)
	def _pragma_constraints_disable(A):B=A._sql_pragma_check_constraints(False);A._cur.execute(B)
	def _create_table(A,table):B=table.get_table_schema().get_schema();A._cur.execute(B)
	def _delete_table(A,table_name):B=A._sql_delete_table(table_name);A._cur.execute(B)
	def _rename_table(A,table_name,new_table_name):B=A._sql_rename_table(table_name,new_table_name);A._cur.execute(B)
	def load_records(A):
		for B in A._tables_by_name.values():B.load_records(A._cur)
	def offload_records(A):
		for B in A._tables_by_name.values():B.offload_records()
	def merge(A,inject,ancestor):
		D=inject;B=ancestor;A.load_records();D.load_records()
		if B:B.load_records()
		E={*A._tables_by_name.keys()};F=D._tables_by_name;G=B._tables_by_name if B else _A;merge_3way(A._tables_by_name,F,G);A._pragma_constraints_disable()
		for H in E:A._delete_table(H)
		for C in A._tables_by_name.values():A._create_table(C);C.dump_records(A._cur)
		for C in A._tables_by_name.values():C.dump_indexes(A._cur)
		A._pragma_constraints_enable()
def merge_sqlite_dbs(sqlite_file_current,sqlite_file_inject,sqlite_file_ancestor=_A):
	D=sqlite_file_inject;C=sqlite_file_current;A=sqlite_file_ancestor;E=DDBDatabase(C);F=DDBDatabase(D);B=DDBDatabase(A)if A else _A;E.merge(F,B);E.commit_and_close();F.close()
	if B:B.close()
	LOG.debug(f"Successfully merged db {C} with {D} and {A}")
def _sqlite_dump(db,file_path=_A):A=file_path;A=A or new_tmp_file();save_file(A,db);return A
def _sqlite_load(path):
	with open(path,'rb')as A:B=A.read()
	return B
def merge_dynamodb(current,inject,ancestor=_A):
	D=inject;C=ancestor;B=current;M={*B.keys(),*D.keys(),*(C.keys()if C else{})}
	for A in M:
		H=A in B;I=A in D;J=A in C if C else False;N=not H and I and not J;O=H and not I and J;P=A.endswith('.db')
		if N:B[A]=D[A]
		elif O:del B[A]
		else:
			E=B.get(A,b'');F=D.get(A,b'');G=C.get(A,_A)if C else _A
			if P:K=_sqlite_dump(E);Q=_sqlite_dump(F);R=_sqlite_dump(G)if G else _A;merge_sqlite_dbs(K,Q,R);S=_sqlite_load(K);B[A]=S
			else:
				L='no strict injecting update hence accepting current version.';T=E==G and E!=F
				if T:B[A]=F;L='strict injecting update hence accepting injecting version.'
				LOG.warning(f"No handling routine for merging of DynamoDB asset '{A}': {L}")