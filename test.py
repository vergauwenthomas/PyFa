import pyfa_tool as pyfa

# Create a new instance of the PyFa class
sfx_file="/dodrio/scratch/projects/2022_200/project_output/RMIB-UGent/vsc46032_kobe/run_ALARO_sfx/runs/DOMAIN_TEST_ERA5_25_5_ALARO1SFX_BE_MEDIUM/run_19960826/output/1996/08/ICMSHABOF+0001.sfx"
file="/dodrio/scratch/projects/2022_200/project_output/RMIB-UGent/vsc46032_kobe/run_ALARO_sfx/runs/DOMAIN_TEST_ERA5_25_5_ALARO1SFX_BE_MEDIUM/run_19960826/output/1996/08/ICMSHABOF+0001"

cls_wind_data = pyfa.FaDataset(fafile=file)
cls_wind_data.import_2d_field(fieldname='CLSVENT.ZONAL')
print(cls_wind_data) 


#Collections

fa1 = pyfa.FaDataset(fafile="/dodrio/scratch/projects/2022_200/project_output/RMIB-UGent/vsc46032_kobe/run_ALARO_sfx/runs/DOMAIN_TEST_ERA5_25_5_ALARO1SFX_BE_MEDIUM/run_19960826/output/1996/08/ICMSHABOF+0001")
fa2 = pyfa.FaDataset(fafile="/dodrio/scratch/projects/2022_200/project_output/RMIB-UGent/vsc46032_kobe/run_ALARO_sfx/runs/DOMAIN_TEST_ERA5_25_5_ALARO1SFX_BE_MEDIUM/run_19960826/output/1996/08/ICMSHABOF+0002")
fa1.import_2d_field(fieldname='CLSVENT.ZONAL')
fa2.import_2d_field(fieldname='CLSVENT.ZONAL')

my_collection = pyfa.FaCollection(FaDatasets=[fa1,fa2],combine_by_validate=True)
time_series = my_collection.get_time_series(y=50000,x=600)

