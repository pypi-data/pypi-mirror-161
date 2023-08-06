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
            gqmn__hps = set()
            ehtsv__uuo = list(self.context._get_attribute_templates(self.key))
            had__ktyiw = ehtsv__uuo.index(self) + 1
            for mal__zmcwk in range(had__ktyiw, len(ehtsv__uuo)):
                if isinstance(ehtsv__uuo[mal__zmcwk], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    gqmn__hps.add(ehtsv__uuo[mal__zmcwk]._attr)
            self._attr_set = gqmn__hps
        return attr_name in self._attr_set
