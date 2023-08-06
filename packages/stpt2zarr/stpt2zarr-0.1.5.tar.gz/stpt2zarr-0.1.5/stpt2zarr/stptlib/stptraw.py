from pathlib import Path
from dateutil.parser import parse as dateparser

from .mosaicdict import MosaicDict
from .stptsectionraw import StptSectionRaw

IMAGE_TS_FORMAT = '%m%d%Y-%H%M'

"""
    StptRaw: holds metadata about raw STPT scan and all of its sections
"""


class StptRaw:

    def __init__(self, input_dir):
        self.input_dir = Path(input_dir)
        self.name = self.input_dir.name
        self.timestamp = None  # run timestamp
        self.code = None
        # maximum number of channels which can vary between slices or tiles due to missing files
        self.n_channels = 0
        self.n_tiles_physical = 0
        self.n_tiles_optical = 0

    def parse(self):
        # check if mosaic file exists
        files = list(self.input_dir.glob('Mosaic*.txt'))
        if not files:
            # attempt to use a mosaic file of one of the sections
            files = list(self.input_dir.glob('**/Mosaic*.txt'))
            # raise exception if still no mosaic files found
            if not files:
                raise Exception('No mosaic file was found in the root folder')
        elif len(files) > 1:
            raise Exception('More than one mosaic file were found in the root folder')
        # parse the root file into dictionary
        with open(files[0], 'r') as f:
            try:
                content = f.readlines()
                if not content:
                    raise Exception('Root mosaic file is empty')
                self.meta = MosaicDict()
                _ = [
                    self.meta.update({a[0]: a[1]})
                    for a in list(map(lambda x: x.strip().split(':', 1), content))
                    if len(a) == 2
                ]
                # assign run timestamp and cpde
                self.timestamp = dateparser(self.meta['acqDate'])
                self.code = 'STPT-{}'.format(self.timestamp.strftime(IMAGE_TS_FORMAT))
            except Exception as e:
                raise Exception('Error while parsing root mosaic file: {}'.format(str(e)))
        # set number of physical and optical tiles
        self.n_tiles_physical = self.meta['mrows'] * self.meta['mcolumns']
        self.n_tiles_optical = self.n_tiles_physical * self.meta['layers']
        # find the actual number of sections ('sections' doesn't always provide a reliable number)
        self._find_sections()
        # raise exception if all sections are missing
        n_missing_sections = [s for s in self.sections if s.missing]
        if n_missing_sections == len(self.sections):
            raise Exception('Could not find any sections to process.')
        # parse metadata for each section
        self._parse_sections()

    def _find_sections(self):
        self.sections = []
        try:
            # look for available section folders
            section_dirs = sorted(self.input_dir.glob('{}-????'.format(self.meta['Sample ID'])))
            if not section_dirs:
                raise Exception('Could not locate any section folders for this STPT scan')
            for section_dir in section_dirs:
                section_num = int(str(section_dir)[-4:])
                self.sections.append(StptSectionRaw(
                    section_num, section_dir, self
                ))
            n_sections_avail = len(self.sections)
            n_sections_meta = self.meta['sections']
            if n_sections_meta != n_sections_avail:
                # find which sections are missing
                n_sections = n_sections_meta if n_sections_meta > self.sections[-1].num else self.sections[-1].num
                for s in range(1, n_sections + 1):
                    avail = [a for a in self.sections if a.num == s]
                    if not avail:
                        self.sections.append(StptSectionRaw(s))
                if n_sections_meta < n_sections_avail:
                    self.meta['sections'] = n_sections_avail
                # sort sections by assigned number
                self.sections.sort(key=lambda x: x.num)
        except Exception as e:
            raise Exception('Error while searching for section folders: {}'.format(str(e)))

    def _parse_sections(self):
        try:
            for section in self.sections:
                if not section.missing:
                    section.parse()
        except Exception as e:
            raise Exception('Error while parsing section #{} metadata: {}'.format(section.num, str(e)))
        pass
