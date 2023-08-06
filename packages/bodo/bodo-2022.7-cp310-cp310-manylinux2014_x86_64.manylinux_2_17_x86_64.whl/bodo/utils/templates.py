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
            njw__hpxh = set()
            zwaq__foede = list(self.context._get_attribute_templates(self.key))
            dwha__umkh = zwaq__foede.index(self) + 1
            for ifc__soo in range(dwha__umkh, len(zwaq__foede)):
                if isinstance(zwaq__foede[ifc__soo], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    njw__hpxh.add(zwaq__foede[ifc__soo]._attr)
            self._attr_set = njw__hpxh
        return attr_name in self._attr_set
