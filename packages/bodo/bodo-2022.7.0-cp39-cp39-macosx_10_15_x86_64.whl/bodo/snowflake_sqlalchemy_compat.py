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
    zwee__lsyc = {}
    hcgt__iha, ebf__kig = self._current_database_schema(connection, **kw)
    plt__oqajt = self._denormalize_quote_join(hcgt__iha, schema)
    try:
        bxszr__nrybf = self._get_schema_primary_keys(connection, plt__oqajt,
            **kw)
        xnfbc__rqud = connection.execute(text(
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
    except sa_exc.ProgrammingError as sqni__cgcgx:
        if sqni__cgcgx.orig.errno == 90030:
            return None
        raise
    for table_name, doeei__pahe, fugf__mqqs, ebpev__wpphh, gzde__tvbkb, wpkg__ywvz, ofnf__kzowa, lrrih__vfuh, ggkel__whlry, jmx__jus in xnfbc__rqud:
        table_name = self.normalize_name(table_name)
        doeei__pahe = self.normalize_name(doeei__pahe)
        if table_name not in zwee__lsyc:
            zwee__lsyc[table_name] = list()
        if doeei__pahe.startswith('sys_clustering_column'):
            continue
        byr__fnzhb = self.ischema_names.get(fugf__mqqs, None)
        vxd__tph = {}
        if byr__fnzhb is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(fugf__mqqs, doeei__pahe))
            byr__fnzhb = sqltypes.NULLTYPE
        elif issubclass(byr__fnzhb, sqltypes.FLOAT):
            vxd__tph['precision'] = gzde__tvbkb
            vxd__tph['decimal_return_scale'] = wpkg__ywvz
        elif issubclass(byr__fnzhb, sqltypes.Numeric):
            vxd__tph['precision'] = gzde__tvbkb
            vxd__tph['scale'] = wpkg__ywvz
        elif issubclass(byr__fnzhb, (sqltypes.String, sqltypes.BINARY)):
            vxd__tph['length'] = ebpev__wpphh
        hjke__hmra = byr__fnzhb if isinstance(byr__fnzhb, sqltypes.NullType
            ) else byr__fnzhb(**vxd__tph)
        ijjsl__upkg = bxszr__nrybf.get(table_name)
        zwee__lsyc[table_name].append({'name': doeei__pahe, 'type':
            hjke__hmra, 'nullable': ofnf__kzowa == 'YES', 'default':
            lrrih__vfuh, 'autoincrement': ggkel__whlry == 'YES', 'comment':
            jmx__jus, 'primary_key': doeei__pahe in bxszr__nrybf[table_name
            ]['constrained_columns'] if ijjsl__upkg else False})
    return zwee__lsyc


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
    zwee__lsyc = []
    hcgt__iha, ebf__kig = self._current_database_schema(connection, **kw)
    plt__oqajt = self._denormalize_quote_join(hcgt__iha, schema)
    bxszr__nrybf = self._get_schema_primary_keys(connection, plt__oqajt, **kw)
    xnfbc__rqud = connection.execute(text(
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
    for table_name, doeei__pahe, fugf__mqqs, ebpev__wpphh, gzde__tvbkb, wpkg__ywvz, ofnf__kzowa, lrrih__vfuh, ggkel__whlry, jmx__jus in xnfbc__rqud:
        table_name = self.normalize_name(table_name)
        doeei__pahe = self.normalize_name(doeei__pahe)
        if doeei__pahe.startswith('sys_clustering_column'):
            continue
        byr__fnzhb = self.ischema_names.get(fugf__mqqs, None)
        vxd__tph = {}
        if byr__fnzhb is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(fugf__mqqs, doeei__pahe))
            byr__fnzhb = sqltypes.NULLTYPE
        elif issubclass(byr__fnzhb, sqltypes.FLOAT):
            vxd__tph['precision'] = gzde__tvbkb
            vxd__tph['decimal_return_scale'] = wpkg__ywvz
        elif issubclass(byr__fnzhb, sqltypes.Numeric):
            vxd__tph['precision'] = gzde__tvbkb
            vxd__tph['scale'] = wpkg__ywvz
        elif issubclass(byr__fnzhb, (sqltypes.String, sqltypes.BINARY)):
            vxd__tph['length'] = ebpev__wpphh
        hjke__hmra = byr__fnzhb if isinstance(byr__fnzhb, sqltypes.NullType
            ) else byr__fnzhb(**vxd__tph)
        ijjsl__upkg = bxszr__nrybf.get(table_name)
        zwee__lsyc.append({'name': doeei__pahe, 'type': hjke__hmra,
            'nullable': ofnf__kzowa == 'YES', 'default': lrrih__vfuh,
            'autoincrement': ggkel__whlry == 'YES', 'comment': jmx__jus if 
            jmx__jus != '' else None, 'primary_key': doeei__pahe in
            bxszr__nrybf[table_name]['constrained_columns'] if ijjsl__upkg else
            False})
    return zwee__lsyc


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
