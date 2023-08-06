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
            lru__ata = set()
            xcxqe__tia = list(self.context._get_attribute_templates(self.key))
            tbsp__gswz = xcxqe__tia.index(self) + 1
            for mbqn__jqc in range(tbsp__gswz, len(xcxqe__tia)):
                if isinstance(xcxqe__tia[mbqn__jqc], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    lru__ata.add(xcxqe__tia[mbqn__jqc]._attr)
            self._attr_set = lru__ata
        return attr_name in self._attr_set
