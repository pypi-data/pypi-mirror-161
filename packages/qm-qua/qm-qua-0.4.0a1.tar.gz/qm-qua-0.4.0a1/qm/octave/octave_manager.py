import re
from typing import Dict, Tuple, Optional, List, Any

from qm.octave._calibration_config import (
    _prep_config,
    _get_frequencies,
)
from qm.octave.calibration_db import (
    CalibrationDB,
    CalibrationResult,
    octave_output_mixer_name,
)
from qm.octave.enums import (
    OctaveOutput,
    OctaveLOSource,
    RFInputRFSource,
    ClockType,
    ClockFrequency,
    ClockInfo,
    RFOutputMode,
    RFInputLOSource,
    IFMode,
)


def _convert_octave_port_to_number(port: str):
    if port == "I1":
        return 1
    elif port == "Q1":
        return 1
    elif port == "I2":
        return 2
    elif port == "Q2":
        return 2
    elif port == "I3":
        return 3
    elif port == "Q3":
        return 3
    elif port == "I4":
        return 4
    elif port == "Q4":
        return 4
    elif port == "I5":
        return 5
    elif port == "Q5":
        return 5


def _convert_number_to_octave_port(name: str, port: int) -> List:
    return [(name, f"I{port}"), (name, f"Q{port}")]


class QmOctaveConfig:
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._devices: Dict[str, Tuple[str, int]] = {}
        self._calibration_db_path: Optional[str] = None
        self._loopbacks: Dict[Tuple[str, OctaveOutput], Tuple[str, OctaveLOSource]] = {}
        self._opx_connections: Dict[Tuple[str, int], Tuple[str, str]] = {}
        self._calibration_db: Optional[CalibrationDB] = None
        self._fan = None
        if "fan" in kwargs:
            self._fan = kwargs.get("fan")

    def set_device_info(self, name, host, port):
        # can be either the router ip or the actual ip (depends on what we have)
        self._devices[name] = (host, port)

    def get_devices(self):
        return self._devices

    def set_calibration_db(self, path):
        self._calibration_db_path = path

    def add_opx_connections(self, connections: Dict[Tuple[str, int], Tuple[str, str]]):
        # ("con1", 1): ("octave1", "I1")
        # validate structure:
        for k, v in connections.items():
            if not (
                isinstance(k, Tuple)
                and len(k) == 2
                and isinstance(k[0], str)
                and isinstance(k[1], int)
            ):
                raise ValueError(
                    f"key {k} is not according to format " f'("con_name", "port_index")'
                )
            pattern = re.compile("([IQ])([12345])")
            if not (
                isinstance(v, Tuple)
                and len(v) == 2
                and isinstance(v[0], str)
                and isinstance(v[1], str)
                and pattern.match(v[1]) is not None
            ):
                raise ValueError(
                    f"value {v} is not according to format "
                    f'("octave_name", "octave_port")'
                )
        for k, v in connections.items():
            self._opx_connections[k] = v

    # def add_lo_loopback(
    #     self,
    #     octave_output_name: str,
    #     octave_output_port: OctaveOutput,
    #     octave_input_name: str,
    #     octave_input_port: OctaveLOSource,
    # ):
    #     if octave_output_name != octave_input_name:
    #         raise ValueError(
    #             "lo loopback between different octave devices are not supported"
    #         )
    #     self._loopbacks[octave_output_name, octave_output_port] = (
    #         octave_input_name,
    #         octave_input_port,
    #     )

    # def get_lo_loopbacks_by_octave(self, octave_name: str):
    #     return {k[1]: v[1] for k, v in self._loopbacks.items() if k[0] == octave_name}

    def get_opx_octave_connections(self):
        if len(self._opx_connections) > 0:
            return self._opx_connections
        else:
            # default connections:
            return {
                ("con1", 1): ("octave1", "I1"),
                ("con1", 2): ("octave1", "Q1"),
                ("con1", 3): ("octave1", "I2"),
                ("con1", 4): ("octave1", "Q2"),
                ("con1", 5): ("octave1", "I3"),
                ("con1", 6): ("octave1", "Q3"),
                ("con1", 7): ("octave1", "I4"),
                ("con1", 8): ("octave1", "Q4"),
                ("con1", 9): ("octave1", "I5"),
                ("con1", 10): ("octave1", "Q5"),
            }

    @property
    def calibration_db(self) -> CalibrationDB:
        if (
            self._calibration_db is None
            or self._calibration_db_path == self._calibration_db.file_path
        ) and self._calibration_db_path is not None:
            self._calibration_db = CalibrationDB(self._calibration_db_path)
        return self._calibration_db

    def get_opx_iq_ports(self, octave_output_port: Tuple[str, int]):
        conns = self.get_opx_octave_connections()
        inv_conns = {v: k for k, v in conns.items()}
        octave_input_port_i, octave_input_port_q = _convert_number_to_octave_port(
            octave_output_port[0], octave_output_port[1]
        )
        return [inv_conns[octave_input_port_i], inv_conns[octave_input_port_q]]


def _run_compiled(compiled_id, qm):
    from qm.octave._calibration_program import _process_results

    pending_job = qm.queue.add_compiled(compiled_id)
    job = pending_job.wait_for_execution()
    all_done = job.result_handles.wait_for_all_values(timeout=30)
    if not all_done:
        _calibration_failed_error()
    res = _get_results(
        [
            "error",
            "i_track",
            "q_track",
            "c00",
            "c01",
            "c10",
            "c11",
        ],
        job,
    )
    # g_track,
    # phi_track,
    # bool_lo_power_small,
    # bool_lo_step_size_small,
    # bool_too_many_iterations,
    # bool_image_power_small,
    # bool_image_step_size_small,
    # final_g = g_track[-1]
    # final_phi = phi_track[-1]
    # import numpy as np
    # lo = lo
    # if lo[-1] == 0:
    #     lo[-1] = 2 ** -28
    # image = image
    # if image[-1] == 0:
    #     image[-1] = 2 ** -28
    # signal = signal
    # if signal[-1] < 0:
    #     signal[-1] = 8 - signal[-1]
    # exit_lo = (
    #     1 * bool_lo_power_small
    #     + 2 * bool_lo_step_size_small
    #     + 4 * bool_too_many_iterations
    # )
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print(
    #     f"LO suppression is {10 * np.log10(signal[-1] / lo[-1]):.4f} dBc at (I,"
    #     f"Q) = ({final_i:.4f},{final_q:.4f}) "
    # )
    # print(exit_lo)
    # #
    # exit_image = (
    #     1 * bool_image_power_small
    #     + 2 * bool_image_step_size_small
    #     + 4 * bool_too_many_iterations
    # )
    # print(
    #     f"Image suppression is {10 * np.log10(signal[-1] / image[-1]):.4f} dBc "
    #     f"at (g,phi) = ({final_g:.4f},{final_phi:.4f}) "
    # )
    # print(exit_image)
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    return _process_results(
        res["error"],
        res["i_track"],
        res["q_track"],
        res["c00"],
        res["c01"],
        res["c10"],
        res["c11"],
    )


def _calibration_failed_error(extra: str = None):
    raise Exception(
        f"There was a problem during calibration. please check opx is on"
        f" and valid. If this continues, please contact QM support{extra}"
    )


def _get_results(names, job):
    res = {}
    for name in names:
        if name not in job.result_handles:
            _calibration_failed_error(f"\nerror in result {name}")
        res[name] = job.result_handles.get(name).fetch_all(flat_struct=True)
    return res


def _convert_rf_output_index_to_input_source(rf_output) -> RFInputRFSource:
    if rf_output == 1:
        return RFInputRFSource.Loopback_RF_out_1
    elif rf_output == 2:
        return RFInputRFSource.Loopback_RF_out_2
    elif rf_output == 3:
        return RFInputRFSource.Loopback_RF_out_3
    elif rf_output == 4:
        return RFInputRFSource.Loopback_RF_out_4
    elif rf_output == 5:
        return RFInputRFSource.Loopback_RF_out_5


class OctaveManager:
    def __init__(self, config: QmOctaveConfig = None, qmm: Optional = None) -> None:
        super().__init__()
        self._octave_config: QmOctaveConfig
        self._qmm = qmm

        self._check_and_set_config(config)
        self._initialize()

    def _check_and_set_config(self, config):
        if config and isinstance(config, QmOctaveConfig):
            self._octave_config: QmOctaveConfig = config
        elif config is None:
            self._octave_config: QmOctaveConfig = QmOctaveConfig()
        else:
            raise TypeError(" config must be of type QmOctaveConfig")

    def _initialize(self):
        self._octave_clients: Dict[str, Any] = {}
        devices = self._octave_config.get_devices()

        if devices is not None and len(devices) > 0:
            from octave_sdk import Octave

            for dev in devices.items():
                # loop_backs = self._octave_config.get_lo_loopbacks_by_octave(dev[0])
                # loop_backs = {
                #     (item[0][0], item[0][1].to_sdk()): (item[1][0], item[1][1].to_sdk())
                #     for item in loop_backs.items()
                # }
                loop_backs = {}
                self._octave_clients[dev[0]] = Octave(
                    host=dev[1][0],
                    port=dev[1][1],
                    port_mapping=loop_backs,
                    octave_name=dev[0],
                    fan=self._octave_config._fan,
                )

    def set_octave_configuration(self, config: QmOctaveConfig):
        """

        :param config:
        """
        self._check_and_set_config(config)
        self._initialize()

    def _get_output_port(self, opx_i_port, opx_q_port) -> (str, int):
        # check both ports are going to the same mixer
        i_octave_port = self._octave_config.get_opx_octave_connections()[opx_i_port]
        q_octave_port = self._octave_config.get_opx_octave_connections()[opx_q_port]
        if i_octave_port[0] != q_octave_port[0]:
            raise Exception("I and Q are not connected to the same octave")
        if i_octave_port[1][-1] != q_octave_port[1][-1]:
            raise Exception("I and Q are not connected to the same octave input")

        return i_octave_port[0], _convert_octave_port_to_number(i_octave_port[1])

    def _get_client(self, octave_port):
        octave = self._octave_clients[octave_port[0]]
        return octave

    def restore_default_state(self, octave_name):
        self._octave_clients[octave_name].restore_default_state()

    def set_clock(
        self,
        octave_name: str,
        clock_type: ClockType,
        frequency: Optional[ClockFrequency],
        **kwargs,
    ):
        if "synth_clock" in kwargs:
            self._octave_clients[octave_name].set_clock(
                clock_type.to_sdk(), frequency.to_sdk(), kwargs.get("synth_clock")
            )
        else:
            self._octave_clients[octave_name].set_clock(
                clock_type.to_sdk(), frequency.to_sdk()
            )
        self._octave_clients[octave_name].save_default_state(only_clock=True)

    def get_clock(self, octave_name: str) -> ClockInfo:
        sdk_clock = self._octave_clients[octave_name].get_clock()
        return ClockInfo(
            ClockType.from_sdk(sdk_clock.clock_type),
            ClockFrequency.from_sdk(sdk_clock.frequency),
        )

    def set_lo_frequency(
        self,
        octave_output_port: Tuple[str, int],
        lo_frequency: float,
        set_source: bool = True,
    ):
        """
            Sets the LO frequency of the synthesizer associated to element
        :param octave_output_port:
        :param lo_frequency:
        :param set_source:
        """
        octave = self._get_client(octave_output_port)
        octave.rf_outputs[octave_output_port[1]].set_lo_frequency(
            OctaveLOSource.Internal.to_sdk(), lo_frequency
        )
        if set_source:
            octave.rf_outputs[octave_output_port[1]].set_lo_source(
                OctaveLOSource.Internal.to_sdk()
            )

        # octave.save_default_state()

    def set_lo_source(
        self, octave_output_port: Tuple[str, int], lo_port: OctaveLOSource
    ):
        """
            Sets the source of LO going to the upconverter associated with element.
        :param octave_output_port:
        :param lo_port:
        """
        octave = self._get_client(octave_output_port)
        octave.rf_outputs[octave_output_port[1]].set_lo_source(lo_port.to_sdk())
        # octave.save_default_state()

    def set_rf_output_mode(
        self, octave_output_port: Tuple[str, int], switch_mode: RFOutputMode
    ):
        """
            Configures the output switch of the upconverter associated to element.
            switch_mode can be either: 'always_on', 'always_off', 'normal' or 'inverted'
            When in 'normal' mode a high trigger will turn the switch on and a low
                trigger will turn it off
            When in 'inverted' mode a high trigger will turn the switch off and a low
                trigger will turn it on
            When in 'always_on' the switch will be permanently on. When in 'always_off'
                mode the switch will be permanently off.
        :param octave_output_port:
        :param switch_mode:
        """
        octave = self._get_client(octave_output_port)
        octave.rf_outputs[octave_output_port[1]].set_output(switch_mode.to_sdk())
        # octave.save_default_state()

    def set_rf_output_gain(
        self,
        octave_output_port: Tuple[str, int],
        gain_in_db: float,
        lo_frequency: Optional[float] = None,
    ):
        """
            Sets the RF output gain for the upconverter associated with element.
            if no lo_frequency is given, and lo source is internal, will use the
            internal frequency
        :param octave_output_port:
        :param gain_in_db:
        :param lo_frequency:
        """
        octave = self._get_client(octave_output_port)
        octave.rf_outputs[octave_output_port[1]].set_gain(gain_in_db, lo_frequency)
        # octave.save_default_state()

    def set_downconversion_lo_source(
        self,
        octave_input_port: Tuple[str, int],
        lo_source: RFInputLOSource,
        lo_frequency: Optional[float] = None,
        disable_warning: Optional[bool] = False,
    ):
        """
            Sets the LO source for the downconverters.
        :param octave_input_port:
        :param lo_source:
        :param lo_frequency:
        :param disable_warning:
        """
        octave = self._get_client(octave_input_port)
        octave.rf_inputs[octave_input_port[1]].set_lo_source(lo_source.to_sdk())
        octave.rf_inputs[octave_input_port[1]].set_rf_source(
            RFInputRFSource.RF_in.to_sdk()
        )
        internal = (
            lo_source == RFInputLOSource.Internal
            or lo_source == RFInputLOSource.Analyzer
        )
        if lo_frequency is not None and internal:
            octave.rf_inputs[octave_input_port[1]].set_lo_frequency(
                source_name=lo_source.to_sdk(), frequency=lo_frequency
            )
        # octave.save_default_state()

    def set_downconversion_if_mode(
        self,
        octave_input_port: Tuple[str, int],
        if_mode_i: IFMode = IFMode.direct,
        if_mode_q: IFMode = IFMode.direct,
        disable_warning: Optional[bool] = False,
    ):
        """
            Sets the IF downconversion stage.
            if_mode can be one of: 'direct', 'mixer', 'envelope_DC', 'envelope_AC','OFF'
            If only one value is given the setting is applied to both IF channels
            (I and Q) for the downconverter associated to element
            (how will we know that? shouldn't this be per downconverter?)
            If if_mode is a tuple, then the IF stage will be assigned to each
            quadrature independently, i.e.:
            if_mode = ('direct', 'envelope_AC') will set the I channel to be
            direct and the Q channel to be 'envelope_AC'
        :param disable_warning:
        :param octave_input_port:
        :param if_mode_q:
        :param if_mode_i:
        """

        octave = self._get_client(octave_input_port)
        octave.rf_inputs[octave_input_port[1]].set_if_mode_i(if_mode_i.to_sdk())
        octave.rf_inputs[octave_input_port[1]].set_if_mode_q(if_mode_q.to_sdk())

    def calibrate(
        self,
        octave_output_port: Tuple[str, int],
        lo_if_frequencies_tuple_list: List[Tuple] = None,
        save_to_db=True,
        **kwargs,
    ) -> Dict[Tuple[int, int], CalibrationResult]:
        """
            calibrates IQ mixer associated with element
        :param octave_output_port:
        :param lo_if_frequencies_tuple_list: A list of LO/IF frequencies for which the
            calibration is to be performed [(LO1, IF1), (LO2, IF2), ...]
        :param save_to_db:
        """

        octave = self._get_client(octave_output_port)
        output_port = octave_output_port[1]
        calibration_input = 2

        sdk_lo_source = octave.rf_outputs[output_port].get_lo_source()
        lo_source = OctaveLOSource.from_sdk(sdk_lo_source)
        only_one_unique_lo = all(
            lo_if_frequencies_tuple_list[0][0] == tup[0]
            for tup in lo_if_frequencies_tuple_list
        )
        if lo_source != OctaveLOSource.Internal:
            if not only_one_unique_lo:
                raise Exception(
                    "If the LO source is external, "
                    "only one lo frequency is allowed in calibration"
                )

        # TODO fix loop bug and remove this error:
        if not only_one_unique_lo:
            raise ValueError("multiple lo frequencies are not yed supported")

        optimizer_parameters = self._get_optimizer_parameters(
            kwargs.get("optimizer_parameters", None),
        )
        first_lo, first_if = lo_if_frequencies_tuple_list[0]
        compiled, qm = self._compile_calibration_program(
            first_lo, first_if, octave_output_port, optimizer_parameters
        )

        state_name_before = self._set_octave_for_calibration(
            octave, calibration_input, output_port
        )

        result = {}
        current_lo = first_lo
        for lo_freq, if_freq in lo_if_frequencies_tuple_list:
            if current_lo != lo_freq and lo_source == OctaveLOSource.Internal:
                octave.rf_outputs[output_port].set_lo_frequency(
                    lo_source.to_sdk(), lo_freq
                )  # if lo_source is not internal then don't do anything
                current_lo = lo_freq

            octave.rf_inputs[calibration_input].set_lo_source(
                RFInputLOSource.Analyzer.to_sdk()
            )

            octave.rf_inputs[calibration_input].set_lo_frequency(
                RFInputLOSource.Analyzer.to_sdk(),
                lo_freq + optimizer_parameters["calibration_offset_frequency"],
            )

            self._set_if_freq(qm, if_freq, optimizer_parameters)

            dc_offsets, correction = _run_compiled(compiled, qm)
            temp = octave.rf_outputs[output_port].get_temperature()

            result[lo_freq, if_freq] = CalibrationResult(
                mixer_id=octave_output_mixer_name(*octave_output_port),
                correction=correction,
                i_offset=dc_offsets[0],
                q_offset=dc_offsets[1],
                temperature=temp,
                if_frequency=if_freq,
                lo_frequency=lo_freq,
                optimizer_parameters=optimizer_parameters,
            )

            if save_to_db and self._octave_config.calibration_db is not None:
                self._octave_config.calibration_db.update_calibration_data(
                    result[lo_freq, if_freq]
                )

        # set to previous state
        octave.restore_state(state_name_before)

        return result

    def _get_optimizer_parameters(self, optimizer_parameters):
        optimizer_parameters_defaults = {
            "average_iterations": 100,
            "iterations": 10000,
            "calibration_offset_frequency": 7e6,
            "keep_on": False,
        }
        if optimizer_parameters is not None:
            for p in optimizer_parameters:
                if p in optimizer_parameters_defaults:
                    optimizer_parameters_defaults[p] = optimizer_parameters[p]
                else:
                    raise ValueError(f"optimizer parameter {p} is not supported")
        return optimizer_parameters_defaults

    def _compile_calibration_program(
        self,
        first_lo,
        first_if,
        octave_output_port,
        optimizer_parameters_defaults,
    ):
        from qm.octave._calibration_program import _generate_program

        iq_channels = self._octave_config.get_opx_iq_ports(octave_output_port)
        controller_name = iq_channels[0][0]
        adc_channels = [(controller_name, 1), (controller_name, 2)]
        config = _prep_config(
            iq_channels,
            adc_channels,
            first_if,
            first_lo,
            optimizer_parameters_defaults,
        )
        prog = _generate_program(optimizer_parameters_defaults)
        qm = self._qmm.open_qm(config)
        compiled = qm.compile(prog)

        return compiled, qm

    def _set_if_freq(self, qm, if_freq, optimizer_parameters):
        down_mixer_offset, signal_freq, image_freq = _get_frequencies(
            if_freq, optimizer_parameters
        )
        qm.set_intermediate_frequency("IQmixer", if_freq)
        qm.set_intermediate_frequency("signal_analyzer", signal_freq)
        qm.set_intermediate_frequency("lo_analyzer", down_mixer_offset)
        qm.set_intermediate_frequency("image_analyzer", image_freq)

    def _set_octave_for_calibration(
        self, octave, calibration_input, output_port
    ) -> str:
        state_name_before = "before_cal"
        octave.snapshot_state(state_name_before)
        # switch to loopback mode to listen in on the RF output
        octave.rf_inputs[calibration_input].set_rf_source(
            _convert_rf_output_index_to_input_source(output_port).to_sdk()
        )
        octave.rf_inputs[calibration_input].set_if_mode_i(IFMode.direct.to_sdk())
        octave.rf_inputs[calibration_input].set_if_mode_q(IFMode.direct.to_sdk())
        octave.rf_inputs[1].set_if_mode_i(IFMode.off.to_sdk())
        octave.rf_inputs[1].set_if_mode_q(IFMode.off.to_sdk())
        octave.rf_outputs[output_port].set_output(RFOutputMode.on.to_sdk())
        return state_name_before
