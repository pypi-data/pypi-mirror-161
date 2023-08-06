"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            mlq__rrcae = set()
            qruzk__dvg = list(self.context._get_attribute_templates(self.key))
            gdpd__wqfa = qruzk__dvg.index(self) + 1
            for foqub__tqbki in range(gdpd__wqfa, len(qruzk__dvg)):
                if isinstance(qruzk__dvg[foqub__tqbki], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    mlq__rrcae.add(qruzk__dvg[foqub__tqbki]._attr)
            self._attr_set = mlq__rrcae
        return attr_name in self._attr_set
