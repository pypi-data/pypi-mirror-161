from dateutil.parser import parse as dateparser

from .mosaicdict import MosaicDict
from .stpttileraw import StptTileRaw

IMAGE_TS_FORMAT = '%m%d%Y-%H%M'
IMAGE_FN_FILTERS = ['{}-{}_{}.tif', '{}-{}_{}.tif.gz']

"""
    StptSectionRaw: holds metadata about a section as part of a raw STPT scan
"""


class StptSectionRaw:

    def __init__(self, num, input_dir=None, stpt=None):
        self.num = num
        self.input_dir = input_dir
        self.stpt = stpt
        self.missing = input_dir is None
        self.tiles = []
        self.timestamp = None  # section timestamp
        self.missing_images = []

    def parse(self):
        mosaic_fn = 'Mosaic_{}-{}.txt'.format(self.stpt.meta['Sample ID'], str(self.num).zfill(4))
        self.mosaic_fn = self.input_dir.joinpath(mosaic_fn)
        if not self.mosaic_fn.exists():
            # if the mosaic file is missing for this section then label section as missing
            self.missing = True
        else:
            with open(self.mosaic_fn, 'r') as f:
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
                    # assign section timestamp
                    self.timestamp = dateparser(self.meta['acqDate'])
                except Exception as e:
                    raise Exception('(section-{}) {}'.format(self.num, str(e)))
            # make sure that Sample ID is the same as STPT mosaic
            if self.meta['Sample ID'] != self.stpt.meta['Sample ID']:
                raise Exception('(section-{}) {}'.format(self.num, 'has different Sample ID'))
            # format timestamp to parse image files
            self._ts_formated = self.timestamp.strftime(IMAGE_TS_FORMAT)
            # varify number of channels
            self.n_channels = self._check_num_channels()
            if self.n_channels > self.stpt.n_channels:
                self.stpt.n_channels = self.n_channels
            elif self.n_channels == 0:
                # if no files found for this section then label it as missing
                self.missing = True
                return
            # create tile objects
            self._create_tiles()

    def _create_tiles(self):
        # look for and validate image filenames
        file_list = self._validate_image_files()
        # create tile objects
        n_layers = self.meta['layers']
        n_x_pos = len(self.meta['XPos'])
        n_y_pos = len(self.meta['YPos'])
        for t in range(self.stpt.n_tiles_physical):
            x_pos = (self.meta['XPos'][t] * 0.1) if t < n_x_pos else None
            y_pos = (self.meta['YPos'][t] * 0.1) if t < n_y_pos else None
            tile = StptTileRaw(x_pos, y_pos)
            for layer in range(n_layers):
                optical_idx = (t + layer * self.stpt.n_tiles_physical) * self.n_channels
                for c in range(self.n_channels):
                    file_idx = optical_idx + c
                    file = file_list[file_idx]
                    if file['missing']:
                        # add the indices of the missing file - channel index starts at 1
                        self.missing_images.append([t, layer, c + 1])
                    tile.files.append(file)
            self.tiles.append(tile)

    def _find_files_multiple_pattern(self, t, ch):
        files = []
        for image_fn_filter in IMAGE_FN_FILTERS:
            file_filter = image_fn_filter.format(self._ts_formated, t, ch)
            files.extend(self.input_dir.glob(file_filter))
        return files

    def _check_num_channels(self):
        # Look for the files that satisfy filenameTemplate_image for the first tile
        # The first tile could be missing a channel image file, so we need to find
        #  - the maximum number of channels available
        image_files = self._find_files_multiple_pattern('*', '??')
        num_files_threshold = 1
        if len(image_files) < num_files_threshold:
            return 0
        return max([int(x.stem.rpartition('_')[2].replace('.tif', '')) for x in image_files])

    # def _find_image_files(self):
    #     file_filter = IMAGE_FN_FILTER.format(self._ts_formated, '*', '??')
    #     return list(self.input_dir.glob(file_filter))

    def _check_if_file_exists(self, t, ch):
        missing = True
        file_path = ''
        for image_fn_filter in IMAGE_FN_FILTERS:
            file_path = image_fn_filter.format(self._ts_formated, t, ch)
            file_path = self.input_dir.joinpath(file_path)
            if file_path.exists():
                missing = False
                break
            else:
                file_path = ''
        return missing, file_path

    def _validate_image_files(self):
        file_list = []
        start_num = self.meta['startnum']
        for t in range(start_num, start_num + self.stpt.n_tiles_optical):
            for c in range(1, self.stpt.n_channels + 1):
                missing, file_path = self._check_if_file_exists(t, str(c).zfill(2))
                file_info = {
                    'fp': file_path,
                    'missing': missing,
                }
                file_list.append(file_info)
        return file_list
