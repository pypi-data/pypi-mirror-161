"""
Fake MakeMovieFrames and AssembleTestMovie
"""
from astropy.io import fits
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess
from dkist_processing_common.tasks import AssembleMovie
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin
from PIL import ImageDraw


class MakeTestMovieFrames(WorkflowTaskBase, FitsDataMixin):
    """
    Take each output frame, copy the header and data and write out
    as a movie frame
    """

    def run(self):
        for d in range(1, self.constants.num_dsps_repeats + 1):
            with self.apm_task_step(f"Workign on dsps repeat {d}"):
                for path, hdu in self.fits_data_read_hdu(tags=[Tag.output(), Tag.dsps_repeat(d)]):
                    header = hdu.header
                    data = hdu.data
                    output_hdu = fits.PrimaryHDU(data=data, header=header)
                    output_hdul = fits.HDUList([output_hdu])

                    with self.apm_writing_step("Writing data"):
                        self.fits_data_write(
                            hdu_list=output_hdul,
                            tags=[Tag.movie_frame(), Tag.dsps_repeat(d)],
                        )


class AssembleTestMovie(AssembleMovie):
    """
    A shell to extend the AssembleMovie class for the end-to-end test.
    """

    @property
    def fits_parsing_class(self):
        return L1FitsAccess

    def write_overlay(self, draw: ImageDraw, fits_obj: L1FitsAccess) -> None:
        pass
