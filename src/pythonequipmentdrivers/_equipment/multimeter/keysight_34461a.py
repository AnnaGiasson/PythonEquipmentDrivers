from pythonequipmentdrivers._equipment.multimeter.hp_34401a import HP_34401A

# TODO: Add in additional measurement functionallity not written in the
# original HP_34401A Class. Look into adding functionallity for adjusting the
# triggering settings


class Keysight_34461A(HP_34401A):
    """
    Keysight_34461A()

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    Object for accessing basic functionallity of the Keysight_34461A multimeter
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).

    Additional Information:
    https://literature.cdn.keysight.com/litweb/pdf/34460-90901.pdf
    """

    valid_ranges = {"AUTO", "MIN", "MAX", "DEF", "0.1", "1", "10", "100", "1000"}

    valid_cranges = {
        "AUTO",
        "MIN",
        "MAX",
        "DEF",
        "0.0001",
        "0.001",
        "0.01",
        "0.1",
        "1",
        "3",
    }

    valid_Rranges = {
        "AUTO",
        "MIN",
        "MAX",
        "DEF",
        "100",
        "1E3",
        "10E3",
        "100E3",
        "1E6",
        "10E6",
        "100E6",
    }

    def set_display_text(self, text: str) -> None:
        self.write_resource(f'DISP:TEXT "{text}"')

    def get_display_text(self) -> str:
        response = self.query_resource("DISP:TEXT?")
        return response.replace('"', "")

    def clear_display_text(self) -> None:
        self.set_display_text("")

    def set_display_state(self, state: bool) -> None:
        if state:
            self.write_resource("DISP ON")
        else:
            self.write_resource("DISP OFF")

    def get_display_state(self) -> bool:
        response = self.query_resource("DISP?")
        return bool(int(response))

    def set_display_mode(self, mode: str) -> None:

        mode = str(mode).upper()
        if mode not in {"NUM", "HIST", "TCH", "MET"}:
            raise ValueError(f'Invalid mode for arg "mode" ({mode})')

        self.write_resource(f"DISP:VIEW {mode}")

    def get_display_mode(self) -> str:
        response = self.query_resource("DISP:VIEW?")
        return response

    def set_label_text(self, label: str) -> None:
        self.write_resource(f'SYSTEM:LABEL "{label}"')

    def get_label_text(self) -> str:
        response = self.query_resource("SYSTEM:LABEL?")
        return response.replace('"', "")

    def clear_label_text(self) -> None:
        self.set_label_text("")
