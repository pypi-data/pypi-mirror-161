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
    zuj__auqkj = {}
    otv__mhw, trq__eptg = self._current_database_schema(connection, **kw)
    msco__errip = self._denormalize_quote_join(otv__mhw, schema)
    try:
        uxky__orxom = self._get_schema_primary_keys(connection, msco__errip,
            **kw)
        ngfy__ouh = connection.execute(text(
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
    except sa_exc.ProgrammingError as vuikt__tksu:
        if vuikt__tksu.orig.errno == 90030:
            return None
        raise
    for table_name, baifo__rdv, nccqw__ndjy, kzi__umba, nnp__fzabq, yihbw__xnr, fvse__ddccs, sffeh__aghs, okmkj__jng, sjvpb__ghpby in ngfy__ouh:
        table_name = self.normalize_name(table_name)
        baifo__rdv = self.normalize_name(baifo__rdv)
        if table_name not in zuj__auqkj:
            zuj__auqkj[table_name] = list()
        if baifo__rdv.startswith('sys_clustering_column'):
            continue
        zzw__vhdpi = self.ischema_names.get(nccqw__ndjy, None)
        vgcex__ozucz = {}
        if zzw__vhdpi is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(nccqw__ndjy, baifo__rdv))
            zzw__vhdpi = sqltypes.NULLTYPE
        elif issubclass(zzw__vhdpi, sqltypes.FLOAT):
            vgcex__ozucz['precision'] = nnp__fzabq
            vgcex__ozucz['decimal_return_scale'] = yihbw__xnr
        elif issubclass(zzw__vhdpi, sqltypes.Numeric):
            vgcex__ozucz['precision'] = nnp__fzabq
            vgcex__ozucz['scale'] = yihbw__xnr
        elif issubclass(zzw__vhdpi, (sqltypes.String, sqltypes.BINARY)):
            vgcex__ozucz['length'] = kzi__umba
        bpeb__wbg = zzw__vhdpi if isinstance(zzw__vhdpi, sqltypes.NullType
            ) else zzw__vhdpi(**vgcex__ozucz)
        yzfih__tmvjn = uxky__orxom.get(table_name)
        zuj__auqkj[table_name].append({'name': baifo__rdv, 'type':
            bpeb__wbg, 'nullable': fvse__ddccs == 'YES', 'default':
            sffeh__aghs, 'autoincrement': okmkj__jng == 'YES', 'comment':
            sjvpb__ghpby, 'primary_key': baifo__rdv in uxky__orxom[
            table_name]['constrained_columns'] if yzfih__tmvjn else False})
    return zuj__auqkj


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
    zuj__auqkj = []
    otv__mhw, trq__eptg = self._current_database_schema(connection, **kw)
    msco__errip = self._denormalize_quote_join(otv__mhw, schema)
    uxky__orxom = self._get_schema_primary_keys(connection, msco__errip, **kw)
    ngfy__ouh = connection.execute(text(
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
    for table_name, baifo__rdv, nccqw__ndjy, kzi__umba, nnp__fzabq, yihbw__xnr, fvse__ddccs, sffeh__aghs, okmkj__jng, sjvpb__ghpby in ngfy__ouh:
        table_name = self.normalize_name(table_name)
        baifo__rdv = self.normalize_name(baifo__rdv)
        if baifo__rdv.startswith('sys_clustering_column'):
            continue
        zzw__vhdpi = self.ischema_names.get(nccqw__ndjy, None)
        vgcex__ozucz = {}
        if zzw__vhdpi is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(nccqw__ndjy, baifo__rdv))
            zzw__vhdpi = sqltypes.NULLTYPE
        elif issubclass(zzw__vhdpi, sqltypes.FLOAT):
            vgcex__ozucz['precision'] = nnp__fzabq
            vgcex__ozucz['decimal_return_scale'] = yihbw__xnr
        elif issubclass(zzw__vhdpi, sqltypes.Numeric):
            vgcex__ozucz['precision'] = nnp__fzabq
            vgcex__ozucz['scale'] = yihbw__xnr
        elif issubclass(zzw__vhdpi, (sqltypes.String, sqltypes.BINARY)):
            vgcex__ozucz['length'] = kzi__umba
        bpeb__wbg = zzw__vhdpi if isinstance(zzw__vhdpi, sqltypes.NullType
            ) else zzw__vhdpi(**vgcex__ozucz)
        yzfih__tmvjn = uxky__orxom.get(table_name)
        zuj__auqkj.append({'name': baifo__rdv, 'type': bpeb__wbg,
            'nullable': fvse__ddccs == 'YES', 'default': sffeh__aghs,
            'autoincrement': okmkj__jng == 'YES', 'comment': sjvpb__ghpby if
            sjvpb__ghpby != '' else None, 'primary_key': baifo__rdv in
            uxky__orxom[table_name]['constrained_columns'] if yzfih__tmvjn else
            False})
    return zuj__auqkj


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
