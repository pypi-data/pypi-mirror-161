# -*- coding: utf-8 -*-
import cantera as ct


class FlowUnits:
    """ Management of flow rate units for different applications.

    Conversion is performed assuming ideal gas law. Concentration at normal
    condition is multiplied by gas molar weight and this value is used as
    base conversion factor.

    Attributes
    ----------
    T_NORMAL : float
        Reference temperature for normal flow rates, default is 288.15 K.
    """
    T_NORMAL: float = 288.15

    @property
    def normal_concentration(self) -> float:
        """ Ideal gas concentration at normal conditions [kmol/m³]. """
        return ct.one_atm / (ct.gas_constant * self.__class__.T_NORMAL)

    def normal_flow_to_mass_flow(self, q: float, mw: float) -> float:
        """ Convert flow given in Nm³/h to kg/s for a solution.
        
        Parameters
        ----------
        q: float
            Flow rate to be converted in Nm³/h.
        mw: float
            Solution mean molecular weight in kg/kmol.

        Returns
        -------
        float
            Flow rate converted to kg/s.
        """
        return self.normal_concentration * mw * q / 3600
