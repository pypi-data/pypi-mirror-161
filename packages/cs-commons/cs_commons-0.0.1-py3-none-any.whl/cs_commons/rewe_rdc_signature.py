import re
# TODO: MOVE THIS TO NEW CS COMMONS PROJECT/rewe

SUB_PATTERN = re.compile(r"1[012345679]\.\d{1,2}")
FULL_PATTERN = re.compile(rf"0?[1234789]\.{SUB_PATTERN.pattern}")
C_SIGNATURE_PATTERN = re.compile(r"0?(?:[1234789]\.)?1[012345679]\.\d{1,2}")
RANGE_SIGNATURE_PATTERN = re.compile(f"{C_SIGNATURE_PATTERN.pattern}[+-]{C_SIGNATURE_PATTERN.pattern}")
RANGE_SIGNATURE_SEPARATOR = "[+-]"

# TODO: Write tests!
# TODO: Make enum?
STRUCTURAL_DATA_BY_INDEX = {
    10: ("shelf", "horizontal"),
    11: ("counter", "horizontal"),
    12: ("island", "horizontal"),
    13: ("chest", "horizontal"),
    14: ("cabinet", "vertical"),
    15: ("set", "combined"),
    16: ("cold_room", None),
    17: ("self_service_bar", "horizontal"),
    19: ("chiller", "vertical")
}


class Signature:
    COMPOUND_SYSTEMS = [1, 2, 3, 4, 7, 8, 9]
    LOW_TEMPERATURE_COMPOUND_SYSTEMS = [4, 9]
    MEDIUM_TEMPERATURE_COMPOUND_SYSTEMS = [1, 2, 8]
    PLUGIN_COMPOUND_SYSTEMS = [8, 9]
    REMOTE_COMPOUND_SYSTEMS = [1, 2, 3, 4, 7]

    @property
    def orientation(self):
        return STRUCTURAL_DATA_BY_INDEX.get(self.structural_type_index)[1]

    @property
    def heat_dissipation_technology(self):
        return "integral" if self.compound_system_index in self.PLUGIN_COMPOUND_SYSTEMS else "remote"

    @property
    def temperature_classification(self):
        """
        # Section below might be needed when creating frigoweb names.
        if self.compound_system_index == 3:
            return "meat"
        """
        return "lt" if self.compound_system_index in self.LOW_TEMPERATURE_COMPOUND_SYSTEMS else "mt"

    @property
    def structural_type(self):
        return STRUCTURAL_DATA_BY_INDEX.get(self.structural_type_index)[0]

    def inferred_data(self):
        return {
            "orientation": self.orientation,
            "heat_dissipation_technology": self.heat_dissipation_technology,
            "temperature_classification": self.temperature_classification,
            "structural_type": self.structural_type
        }

    @staticmethod
    def to_string(signature: tuple):
        if len(signature) == 2:
            return f"{signature[0]}.{signature[1]}"
        return f"{signature[0]}.{signature[1]}.{str(signature[2]).zfill(2)}"

    def __init__(self, *components):
        if components[0] < 10:
            self.compound_system_index = components[0]
            self.structural_type_index = components[1]
            self.rdc_index = components[2] if len(components) == 3 else None
        else:
            self.compound_system_index = None
            self.structural_type_index = components[0]
            self.rdc_index = components[1]

    def __str__(self):
        rdc_index = str(self.rdc_index).zfill(2) if self.rdc_index else "__"
        return f"{self.compound_system_index or '_'}.{self.structural_type_index or '__'}.{rdc_index}"

    def is_complete(self):
        return all(x is not None for x in [self.compound_system_index, self.structural_type_index, self.rdc_index])

    @classmethod
    def from_title(cls, title: str):
        if extracted := extract_signature(title):
            return cls(*[int(c) for c in extracted.split(".")])


def _get_range_signature(title):
    """
    Returns a tuple containing the start of the range, the separator and the end of the range
    Eg. 2.10.01+2.10.02 Mo.Regale 750 Monaxis82.B4DEL -> ('2.10.01', '+', '2.10.02')
    """
    if not (matches := C_SIGNATURE_PATTERN.findall(title)):
        return
    for match in matches:
        common = ".".join(match.split(".")[:-1])
        # range_pattern = rf"{s}[+-]{common}\.\d\d?"
        range_pattern = rf"({match})\s?({RANGE_SIGNATURE_SEPARATOR})\s?((?:{common}\.)?\d\d?)"

        if range_matches := re.compile(range_pattern).findall(title):
            return range_matches[0]


def _get_signature(title, pattern):
    if not (matches := [m for m in pattern.findall(title)]):
        return
    return matches[0] if len(set(matches)) == 1 else None


def extract_signature(title: str) -> str:
    if title is None:
        return
    # original = title
    if rs := _get_range_signature(title):
        rs_string = "".join(rs)
        title = title.replace(rs_string, "")
    if extracted := _get_signature(title, FULL_PATTERN) or _get_signature(title, SUB_PATTERN):
        return extracted
    # TODO: For now, dont allow range signatures with no compound system index (would mean only one valid index in the signature)
    if rs and (components := rs[0].split(".")) and len(components) > 2:
        return ".".join([c for c in components][:-1])


def extract_signature_debug(title: str) -> str:
    print(f"Evaluating: extract_signature({title})...")
    if title is None:
        print("Title is None. Returning.")
        return
    # original = title
    print(f"Evaluating: _get_range_signature({title})...")
    if rs := _get_range_signature(title):
        print(f"_get_range_signature returned {rs}.")
        rs_string = "".join(rs)
        before = title
        title = title.replace(rs_string, "")
        print(f"Cutting out range signature: {before} -> {title}")
    if extracted := _get_signature(title, FULL_PATTERN) or _get_signature(title, SUB_PATTERN):
        print(f"Evaluating: _get_signature({title})...")
        print(f"_get_signature returned {extracted}.")

        return extracted
    # TODO: For now, dont allow range signatures with no compound system index (would mean only one valid index in the signature)
    if rs and (components := rs[0].split(".")) and len(components) > 2:
        result = ".".join([c for c in components][:-1])
        print(f"No complete signature found. Returning partial signature {result}.")
        return result


if __name__ == '__main__':

    """
    
    print(Signature.from_title("2.10.01+2.10.02 Mo.Regale 750 Monaxis82.B4DEL Pilotmodul 2.10.02 (0)"))
    print(Signature.from_title("1.14.10 - 12 Käse 1075 Monaxeco 63 M2-1L 1.14.12 Käse"))

    exit(0)


    print(_RDCS_PATH)

    print(Signature.from_title("1 4.14.01-4 TK-SCHRANK VELANDO AFA8L 4.14.04"))
    s = Signature.from_title("4.15.07-08 Doppel TK-Insel FKL 250 IRIOS Pilotmodul (4) (2.)")
    print(s)
    print(s.is_complete())
    s = Signature.from_title("14.05-7 MO.SCHRANK 5 KMW MR2A37VSST Pilotmodul (4)")
    print(s)

    rdcs = []
    for market_rdcs in _RDCS_PATH.iterdir():
        with open(market_rdcs, "r", encoding="utf-8") as inp:
            rdcs.extend(json.load(inp))
    results = []

    previous_results = file_to_list("results.txt", remove_empty_trailing=True)

    valid = 0
    for rdc in rdcs:
        title = rdc.get("ColdLocationTitle")
        signature = Signature.from_title(title)
        if signature:
            valid += 1



            #if "istwerte" in args[0].lower():
            #    print(args[0])
            # print(f"{str(signature):12} -> {signature.inferred_data()}")
        result = f"{title:80}{signature}"
        results.append(result)
        # print(result)

    # Valid results: 6034 / 10181
    # Valid results: 6049 / 10181 with range signatures
    print(f"Valid results: {valid} / {len(rdcs)}")
    list_to_file(results, "results.txt")
    if previous_results != results:
        raise RuntimeError("Results changed!")

    print(Signature.from_title("14.10 - 12 Käse 1075 Monaxeco 63 M2-1L 14.12 Käse"))
    print(Signature.from_title("14.10 - 12 Käse 1075 Monaxeco 63 M2-1L 14.12 Käse"))
    """
