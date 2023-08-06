import re
import sys
import warnings
import zipfile
from io import BytesIO
from os import linesep
from pathlib import Path
from typing import BinaryIO, Dict, List

from bs4 import BeautifulSoup
from oletools.olevba import VBA_Parser

# be strict about warnings and turn them into errors
warnings.filterwarnings("error")


class OXMLToTxt(object):
    """XL formula and macro extractor

    This class uses the path to an XL file and by using the `get_content_as_str`
    function returns all formulas and vba code as a formatted string.
    """

    def __init__(self, path: Path = Path(), xml_tags: List[str] = ["f"]):
        # Create the in-memory file-like object for working w/IMZ
        self.in_memory_zip: Dict[str, str]
        self.path = Path()
        self.filedata: BinaryIO
        self.xml_tags = xml_tags
        if path != Path():
            self.path = path
            with open(self.path, "rb") as tmpfile:
                # parse file content into memory to speed up in case of vba content
                self.filedata = BytesIO(tmpfile.read())
            self.in_memory_zip = self._extract_content_from_file()

    def _extract_content_from_file(self) -> Dict[str, str]:
        input_zip = zipfile.ZipFile(self.filedata)
        result_dict: Dict[str, str] = {}
        if any(".bin" in s for s in input_zip.namelist()):
            # if condition is true, we need to assume that vba is contained
            # we reread the file from memory using the oletools to search for code
            # Unfortunately we need to read the file a second time, but only from memory
            print(
                "Found binary file in XL workbook zip. Extracting potentially contained vba code ..."
            )
            self.filedata.seek(0)
            vba_parser = VBA_Parser(self.path, data=self.filedata.read())
            vba_str = ""
            spacer = "  "
            regex = re.compile(r"^(.*)", re.MULTILINE)
            for (
                filename,
                stream_path,
                vba_filename,
                vba_code,
            ) in vba_parser.extract_all_macros():
                vba_str += (
                    f"{spacer}<!--- START {filename} {stream_path} {vba_filename} --->"
                    + linesep
                )
                vba_str += regex.sub(f"{spacer}{spacer}\\1", vba_code) + linesep
                vba_str += (
                    f"{spacer}<!--- END {filename} {stream_path} {vba_filename} --->"
                ) + linesep
            result_dict["VBACode"] = vba_str

        for name in input_zip.namelist():
            # Loop through all files in zip except .bin files
            try:
                result_str: str = ""
                if ".bin" not in name:
                    try:
                        bs_file_cont = BeautifulSoup(
                            input_zip.read(name).decode("cp1252"),
                            features="xml",
                        )
                    except Exception as e:
                        # Some files seem to have different encoding
                        # Maybe utf-8 works if cp1252 fails
                        print("Falling back to utf-8 decoding ...")
                        bs_file_cont = BeautifulSoup(
                            input_zip.read(name).decode("utf-8"),
                            features="xml",
                        )
                    if self.xml_tags == []:
                        # result_dict[name] = bs_file_cont.prettify(encoding = "utf-8")
                        result_dict[name] = bs_file_cont.prettify()
                    else:
                        try:
                            bs_file_cont = bs_file_cont.find_all(self.xml_tags)
                        except Exception as e:
                            print(
                                f"Could not find tag {self.xml_tags} in file {name}.\n{e}"
                            )
                        for s in bs_file_cont:
                            # result_str += s.prettify(encoding = "utf-8")
                            result_str += s.prettify()
                            # result_str += s.prettify()
                        result_dict[name] = result_str
            except Exception as e:
                print(
                    f"Warning: could not format file {name}. The error message is {linesep}{e} ..."
                )
        return result_dict

    def get_content_as_str(self) -> str:
        """_summary_

        Returns:
            str: Content of (possibly _tag filtered_) xml content.
        """
        tmp_str = ""
        for file, content in self.in_memory_zip.items():
            try:
                enc_cont = content.encode("cp1252", errors="replace").decode("utf-8")
                tmp_str += (
                    f"<!---- Start of file {file} ----!>{linesep}"
                    f"{enc_cont}{linesep}"
                    f"<!---- End of file {file} ----!>{linesep}"
                )
            except Exception as e:
                print(f"Unable to extract {file}. Issue:\n{e}")
        return tmp_str


if __name__ == "__main__":
    content = OXMLToTxt(
        Path(sys.argv[-1]), xml_tags=sys.argv[1:-1]
    ).get_content_as_str()
    try:
        print(content)
    except Exception as e:
        print(f"Could not decode file {sys.argv[-1]} ...")
