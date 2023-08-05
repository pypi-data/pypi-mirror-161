from typing import Dict, Tuple, Union, List, Optional, Any

from qm.octave.calibration_db import CalibrationResult
from qm.octave.enums import OctaveLOSource, RFOutputMode, RFInputLOSource, IFMode
from qm.octave.octave_manager import OctaveManager


class QmOctave:
    def __init__(self, qm, octave_manager) -> None:
        super().__init__()
        self._qm = qm
        self._octave_manager: OctaveManager = octave_manager
        self._elements_to_rf_in: Dict[str, Tuple[str, int]] = {}
        self._elements_lo_frequency: Dict[str, float] = {}

    def _get_element_opx_output(
        self, element
    ) -> Tuple[Tuple[str, int], Tuple[str, int]]:
        opx_config = self._qm.get_config()
        if element not in opx_config["elements"]:
            raise ValueError(f"could not find element {element}")
        if "mixInputs" not in opx_config["elements"][element]:
            raise ValueError(f"Element {element} is not of type mixInputs")
        i_port = opx_config["elements"][element]["mixInputs"]["I"]
        q_port = opx_config["elements"][element]["mixInputs"]["Q"]
        return i_port, q_port

    def _get_element_lo_frequency(
        self, element
    ) -> Tuple[Tuple[str, int], Tuple[str, int]]:
        opx_config = self._qm.get_config()
        if element not in opx_config["elements"]:
            raise ValueError(f"could not find element {element}")
        if "mixInputs" not in opx_config["elements"][element]:
            raise ValueError(f"Element {element} is not of type mixInputs")
        frequency = opx_config["elements"][element]["mixInputs"]["lo_frequency"]
        return frequency

    def _get_element_octave_output_port(self, element: str) -> (int, Any):
        opx_i_port, opx_q_port = self._get_element_opx_output(element)
        return self._octave_manager._get_output_port(opx_i_port, opx_q_port)

    def _get_lo_from_element_config(self, element):
        opx_config = self._qm.get_config()
        if element not in opx_config["elements"]:
            raise ValueError(f"could not find element {element}")
        if "mixInputs" not in opx_config["elements"][element]:
            raise ValueError(f"Element {element} is not of type mixInputs")
        lo_frequency = opx_config["elements"][element]["mixInputs"]["lo_frequency"]
        return lo_frequency

    def _get_if_from_element_config(self, element):
        opx_config = self._qm.get_config()
        if element not in opx_config["elements"]:
            raise ValueError(f"could not find element {element}")
        if_frequency = opx_config["elements"][element]["intermediate_frequency"]
        return if_frequency

    def _get_element_downconversion_input_port_and_client(
        self, element: str
    ) -> (str, int):
        if element in self._elements_to_rf_in:
            name, port = self._elements_to_rf_in[element]
            return name, port
        else:
            raise ValueError("Element has no readout port associated")

    def set_qua_element_octave_rf_in_port(self, element, octave_name, rf_input_index):
        opx_config = self._qm.get_config()
        if element not in opx_config["elements"]:
            raise ValueError(f"could not find element {element}")
        self._elements_to_rf_in[element] = (octave_name, rf_input_index)

    def load_lo_frequency_from_config(self, elements: Union[List, str]):
        """
            Loads into the octave synthesizers the LO frequencies specified for elements
            in the element list
        :param elements:
        """
        opx_config = self._qm.get_config()
        for element in elements:
            if element not in opx_config["elements"]:
                raise ValueError(f"could not find element {element}")
            if "mixInputs" not in opx_config["elements"][element]:
                raise ValueError(f"Element {element} is not of type mixInputs")

        for element in elements:
            lo_frequency = opx_config["elements"][element]["mixInputs"]["lo_frequency"]
            self.set_lo_frequency(element, lo_frequency)

    def set_lo_frequency(
        self, element: str, lo_frequency: float, set_source: bool = True
    ):
        """
            Sets the LO frequency of the synthesizer associated to element
        :param element:
        :param lo_frequency:
        :param set_source:
        """
        octave_port = self._get_element_octave_output_port(element)
        self._octave_manager.set_lo_frequency(octave_port, lo_frequency, set_source)

    def update_external_lo_frequency(
        self,
        element: str,
        lo_frequency: float,
    ):
        """
            Updates Octave on the external LO frequency (provided by the user)
            associated with element
        :param element:
        :param lo_frequency:
        """
        self._elements_lo_frequency[element] = lo_frequency

    def set_lo_source(self, element: str, lo_port: OctaveLOSource):
        """
            Sets the source of LO going to the upconverter associated with element.
        :param element:
        :param lo_port:
        """
        octave_port = self._get_element_octave_output_port(element)
        self._octave_manager.set_lo_source(octave_port, lo_port)

    def set_rf_output_mode(self, element: str, switch_mode: RFOutputMode):
        """
            Configures the output switch of the upconverter associated to element.
            switch_mode can be either: 'always_on', 'always_off', 'normal' or 'inverted'
            When in 'normal' mode a high trigger will turn the switch on and a low
                trigger will turn it off
            When in 'inverted' mode a high trigger will turn the switch off and a low
                trigger will turn it on
            When in 'always_on' the switch will be permanently on. When in 'always_off'
                mode the switch will be permanently off.
        :param element:
        :param switch_mode:
        """
        octave_port = self._get_element_octave_output_port(element)
        self._octave_manager.set_rf_output_mode(octave_port, switch_mode)

    def set_rf_output_gain(self, element: str, gain_in_db: float):
        """
            Sets the RF output gain for the upconverter associated with element.
            RF_gain is in steps of 0.5dB from -X to +Y (X and Y TBD) and is referring
            to the maximum OPX output power of 4dBm (=0.5V pk-pk) So for a value of -24
            for example, an IF signal coming from the OPX at max power (4dBm) will be
            upconverted and come out of Octave at -20dBm
        :param element:
        :param gain_in_db:
        """
        # a. use value custom set in qm.octave.update_external
        # b. use value from config
        if element in self._elements_lo_frequency:
            frequency = self._elements_lo_frequency[element]
        else:
            frequency = self._get_element_lo_frequency(element)

        octave_port = self._get_element_octave_output_port(element)
        self._octave_manager.set_rf_output_gain(octave_port, gain_in_db, frequency)

    def set_downconversion(
        self,
        element: str,
        lo_source: Optional[RFInputLOSource] = None,
        lo_frequency: Optional[float] = None,
        if_mode_i: IFMode = IFMode.direct,
        if_mode_q: IFMode = IFMode.direct,
        disable_warning: bool = False,
    ):
        """
            Sets the LO source for the downconverters.
            The LO source will be the one associated with the upconversion of element
        :param element:
        :param lo_source:
        :param lo_frequency:
        :param if_mode_i:
        :param if_mode_q:
        :param disable_warning:
        """
        self._set_downconversion_lo(
            element, lo_source, lo_frequency, disable_warning=disable_warning
        )
        self._set_downconversion_if_mode(
            element, if_mode_i, if_mode_q, disable_warning=disable_warning
        )

    def _set_downconversion_lo(
        self,
        element: str,
        lo_source: Optional[RFInputLOSource] = None,
        lo_frequency: Optional[float] = None,
        disable_warning=False,
    ):
        """
            Sets the LO source for the downconverters.
            If no value is given the LO source will be the one associated with the
            upconversion of element
        :param element:
        :param lo_frequency:
        :param lo_source:
        :param disable_warning:
        """
        # TODO check if the downconversion shared between elements(from same rf_in or both rf_ins)
        # if we have two elements for the same downconversion:
        # warning when setting for port that has multiple elements
        # “element x shares the input port with elements [y],
        # any settings applied will affect all elements”
        octave_input_port = self._get_element_downconversion_input_port_and_client(
            element
        )
        if lo_source is None:
            octave_port = self._get_element_octave_output_port(element)
            rf_output_port = octave_port[1]
            if rf_output_port == 1:
                lo_source = RFInputLOSource.RFOutput1_LO
            elif rf_output_port == 2:
                lo_source = RFInputLOSource.RFOutput2_LO
            elif rf_output_port == 3:
                lo_source = RFInputLOSource.RFOutput3_LO
            elif rf_output_port == 4:
                lo_source = RFInputLOSource.RFOutput4_LO
            elif rf_output_port == 5:
                lo_source = RFInputLOSource.RFOutput5_LO
            else:
                raise ValueError(f"RF output {rf_output_port} is not found")

        self._octave_manager.set_downconversion_lo_source(
            octave_input_port, lo_source, lo_frequency, disable_warning
        )

    def _set_downconversion_if_mode(
        self,
        element: str,
        if_mode_i: IFMode = IFMode.direct,
        if_mode_q: IFMode = IFMode.direct,
        disable_warning=False,
    ):
        octave_input_port = self._get_element_downconversion_input_port_and_client(
            element
        )
        self._octave_manager.set_downconversion_if_mode(
            octave_input_port, if_mode_i, if_mode_q, disable_warning
        )

    def calibrate_element(
        self,
        element: str,
        lo_if_frequencies_tuple_list: Optional[List[Tuple]] = None,
        save_to_db=True,
        **kwargs,
    ) -> Dict[Tuple[int, int], CalibrationResult]:

        octave_port = self._get_element_octave_output_port(element)

        # get IF and LO frequencies from element
        if lo_if_frequencies_tuple_list is None:
            if_frequency = self._get_if_from_element_config(element)
            lo_frequency = self._get_lo_from_element_config(element)
            lo_if_frequencies_tuple_list = [(if_frequency, lo_frequency)]

        return self._octave_manager.calibrate(
            octave_port, lo_if_frequencies_tuple_list, save_to_db, **kwargs
        )
