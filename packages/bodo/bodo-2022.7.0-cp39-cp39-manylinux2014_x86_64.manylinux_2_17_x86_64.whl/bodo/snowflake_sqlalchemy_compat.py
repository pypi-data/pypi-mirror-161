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
    skpl__jbbi = {}
    nyd__mpocm, dqrf__scgaw = self._current_database_schema(connection, **kw)
    uxe__msxi = self._denormalize_quote_join(nyd__mpocm, schema)
    try:
        wylep__ibz = self._get_schema_primary_keys(connection, uxe__msxi, **kw)
        ojids__wza = connection.execute(text(
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
    except sa_exc.ProgrammingError as iop__lnwe:
        if iop__lnwe.orig.errno == 90030:
            return None
        raise
    for table_name, cbq__mqjmz, akeyl__enh, gch__ycyu, zrlb__zhv, coe__csqh, ncjve__lplme, xss__obxdw, tnkgz__exg, fsaad__djlo in ojids__wza:
        table_name = self.normalize_name(table_name)
        cbq__mqjmz = self.normalize_name(cbq__mqjmz)
        if table_name not in skpl__jbbi:
            skpl__jbbi[table_name] = list()
        if cbq__mqjmz.startswith('sys_clustering_column'):
            continue
        fwkt__nju = self.ischema_names.get(akeyl__enh, None)
        qdg__lzgc = {}
        if fwkt__nju is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(akeyl__enh, cbq__mqjmz))
            fwkt__nju = sqltypes.NULLTYPE
        elif issubclass(fwkt__nju, sqltypes.FLOAT):
            qdg__lzgc['precision'] = zrlb__zhv
            qdg__lzgc['decimal_return_scale'] = coe__csqh
        elif issubclass(fwkt__nju, sqltypes.Numeric):
            qdg__lzgc['precision'] = zrlb__zhv
            qdg__lzgc['scale'] = coe__csqh
        elif issubclass(fwkt__nju, (sqltypes.String, sqltypes.BINARY)):
            qdg__lzgc['length'] = gch__ycyu
        ptwc__ncrz = fwkt__nju if isinstance(fwkt__nju, sqltypes.NullType
            ) else fwkt__nju(**qdg__lzgc)
        dqxg__vkn = wylep__ibz.get(table_name)
        skpl__jbbi[table_name].append({'name': cbq__mqjmz, 'type':
            ptwc__ncrz, 'nullable': ncjve__lplme == 'YES', 'default':
            xss__obxdw, 'autoincrement': tnkgz__exg == 'YES', 'comment':
            fsaad__djlo, 'primary_key': cbq__mqjmz in wylep__ibz[table_name
            ]['constrained_columns'] if dqxg__vkn else False})
    return skpl__jbbi


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
    skpl__jbbi = []
    nyd__mpocm, dqrf__scgaw = self._current_database_schema(connection, **kw)
    uxe__msxi = self._denormalize_quote_join(nyd__mpocm, schema)
    wylep__ibz = self._get_schema_primary_keys(connection, uxe__msxi, **kw)
    ojids__wza = connection.execute(text(
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
    for table_name, cbq__mqjmz, akeyl__enh, gch__ycyu, zrlb__zhv, coe__csqh, ncjve__lplme, xss__obxdw, tnkgz__exg, fsaad__djlo in ojids__wza:
        table_name = self.normalize_name(table_name)
        cbq__mqjmz = self.normalize_name(cbq__mqjmz)
        if cbq__mqjmz.startswith('sys_clustering_column'):
            continue
        fwkt__nju = self.ischema_names.get(akeyl__enh, None)
        qdg__lzgc = {}
        if fwkt__nju is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(akeyl__enh, cbq__mqjmz))
            fwkt__nju = sqltypes.NULLTYPE
        elif issubclass(fwkt__nju, sqltypes.FLOAT):
            qdg__lzgc['precision'] = zrlb__zhv
            qdg__lzgc['decimal_return_scale'] = coe__csqh
        elif issubclass(fwkt__nju, sqltypes.Numeric):
            qdg__lzgc['precision'] = zrlb__zhv
            qdg__lzgc['scale'] = coe__csqh
        elif issubclass(fwkt__nju, (sqltypes.String, sqltypes.BINARY)):
            qdg__lzgc['length'] = gch__ycyu
        ptwc__ncrz = fwkt__nju if isinstance(fwkt__nju, sqltypes.NullType
            ) else fwkt__nju(**qdg__lzgc)
        dqxg__vkn = wylep__ibz.get(table_name)
        skpl__jbbi.append({'name': cbq__mqjmz, 'type': ptwc__ncrz,
            'nullable': ncjve__lplme == 'YES', 'default': xss__obxdw,
            'autoincrement': tnkgz__exg == 'YES', 'comment': fsaad__djlo if
            fsaad__djlo != '' else None, 'primary_key': cbq__mqjmz in
            wylep__ibz[table_name]['constrained_columns'] if dqxg__vkn else
            False})
    return skpl__jbbi


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
