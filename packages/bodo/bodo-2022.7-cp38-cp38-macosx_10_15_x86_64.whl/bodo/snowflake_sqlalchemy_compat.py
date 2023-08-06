import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    ohilg__qpvze = {}
    qvb__ossls, cbnle__wqen = self._current_database_schema(connection, **kw)
    omop__rgku = self._denormalize_quote_join(qvb__ossls, schema)
    try:
        sumar__zpozq = self._get_schema_primary_keys(connection, omop__rgku,
            **kw)
        tevn__hlgw = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as msefk__xdd:
        if msefk__xdd.orig.errno == 90030:
            return None
        raise
    for table_name, ezd__hhjhb, neupb__xkbdf, zfk__cgjp, hjf__psduc, ywqy__vwwig, jdzr__dyiis, cmze__ornj, kkpfl__ftmkp, fjck__tcmmh in tevn__hlgw:
        table_name = self.normalize_name(table_name)
        ezd__hhjhb = self.normalize_name(ezd__hhjhb)
        if table_name not in ohilg__qpvze:
            ohilg__qpvze[table_name] = list()
        if ezd__hhjhb.startswith('sys_clustering_column'):
            continue
        fwri__kzwwl = self.ischema_names.get(neupb__xkbdf, None)
        agonr__lqhv = {}
        if fwri__kzwwl is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(neupb__xkbdf, ezd__hhjhb))
            fwri__kzwwl = sqltypes.NULLTYPE
        elif issubclass(fwri__kzwwl, sqltypes.FLOAT):
            agonr__lqhv['precision'] = hjf__psduc
            agonr__lqhv['decimal_return_scale'] = ywqy__vwwig
        elif issubclass(fwri__kzwwl, sqltypes.Numeric):
            agonr__lqhv['precision'] = hjf__psduc
            agonr__lqhv['scale'] = ywqy__vwwig
        elif issubclass(fwri__kzwwl, (sqltypes.String, sqltypes.BINARY)):
            agonr__lqhv['length'] = zfk__cgjp
        rskau__bba = fwri__kzwwl if isinstance(fwri__kzwwl, sqltypes.NullType
            ) else fwri__kzwwl(**agonr__lqhv)
        lurxh__ain = sumar__zpozq.get(table_name)
        ohilg__qpvze[table_name].append({'name': ezd__hhjhb, 'type':
            rskau__bba, 'nullable': jdzr__dyiis == 'YES', 'default':
            cmze__ornj, 'autoincrement': kkpfl__ftmkp == 'YES', 'comment':
            fjck__tcmmh, 'primary_key': ezd__hhjhb in sumar__zpozq[
            table_name]['constrained_columns'] if lurxh__ain else False})
    return ohilg__qpvze


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    ohilg__qpvze = []
    qvb__ossls, cbnle__wqen = self._current_database_schema(connection, **kw)
    omop__rgku = self._denormalize_quote_join(qvb__ossls, schema)
    sumar__zpozq = self._get_schema_primary_keys(connection, omop__rgku, **kw)
    tevn__hlgw = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, ezd__hhjhb, neupb__xkbdf, zfk__cgjp, hjf__psduc, ywqy__vwwig, jdzr__dyiis, cmze__ornj, kkpfl__ftmkp, fjck__tcmmh in tevn__hlgw:
        table_name = self.normalize_name(table_name)
        ezd__hhjhb = self.normalize_name(ezd__hhjhb)
        if ezd__hhjhb.startswith('sys_clustering_column'):
            continue
        fwri__kzwwl = self.ischema_names.get(neupb__xkbdf, None)
        agonr__lqhv = {}
        if fwri__kzwwl is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(neupb__xkbdf, ezd__hhjhb))
            fwri__kzwwl = sqltypes.NULLTYPE
        elif issubclass(fwri__kzwwl, sqltypes.FLOAT):
            agonr__lqhv['precision'] = hjf__psduc
            agonr__lqhv['decimal_return_scale'] = ywqy__vwwig
        elif issubclass(fwri__kzwwl, sqltypes.Numeric):
            agonr__lqhv['precision'] = hjf__psduc
            agonr__lqhv['scale'] = ywqy__vwwig
        elif issubclass(fwri__kzwwl, (sqltypes.String, sqltypes.BINARY)):
            agonr__lqhv['length'] = zfk__cgjp
        rskau__bba = fwri__kzwwl if isinstance(fwri__kzwwl, sqltypes.NullType
            ) else fwri__kzwwl(**agonr__lqhv)
        lurxh__ain = sumar__zpozq.get(table_name)
        ohilg__qpvze.append({'name': ezd__hhjhb, 'type': rskau__bba,
            'nullable': jdzr__dyiis == 'YES', 'default': cmze__ornj,
            'autoincrement': kkpfl__ftmkp == 'YES', 'comment': fjck__tcmmh if
            fjck__tcmmh != '' else None, 'primary_key': ezd__hhjhb in
            sumar__zpozq[table_name]['constrained_columns'] if lurxh__ain else
            False})
    return ohilg__qpvze


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
