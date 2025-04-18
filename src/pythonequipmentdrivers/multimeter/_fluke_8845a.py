from ._hp_34401a import HP_34401A


class Fluke_8845A(HP_34401A):
    """
    Fluke_8845A(address, factor=1)

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    object for accessing basic functionallity of the FLUKE_8845A multimeter.
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).
    """

    def disable_cmd_emulation_mode(self):
        """
        disable_cmd_emulation_mode()

        Disable the Fluke 45 command set emulation mode i.e. use Fluke8845
        native commands.
        """

        self.write_resource("L1")
