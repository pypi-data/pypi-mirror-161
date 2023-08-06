"""
Fake science task
"""
from astropy.io import fits
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin


class GenerateCalibratedData(WorkflowTaskBase, FitsDataMixin):

    record_provenance = True

    def run(self):
        count = 1  # keep a running count to increment the dsps repeat number
        with self.apm_task_step("Looping over inputs"):
            for path, hdu in self.fits_data_read_hdu(tags=Tag.input()):
                header = hdu.header
                with self.apm_processing_step("Doing some calculations"):
                    header["DSPSNUM"] = count
                    data = hdu.data
                    output_hdu = fits.PrimaryHDU(data=data, header=header)

                with self.apm_writing_step("Writing data"):
                    output_hdul = fits.HDUList([output_hdu])
                    self.fits_data_write(
                        hdu_list=output_hdul,
                        tags=[
                            Tag.calibrated(),
                            Tag.frame(),
                            Tag.stokes("I"),
                            Tag.dsps_repeat(count),
                        ],
                    )
                count += 1
