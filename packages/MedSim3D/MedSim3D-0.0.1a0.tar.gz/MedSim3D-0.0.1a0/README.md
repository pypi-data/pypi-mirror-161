## MedSim3D: Medical Simulation Framework in the 3D environment

The `MedSim3D` framework aims to provide a general programmable platform for 3D modeling and simulation in medical education.

### Examples

Example 1: Download datasets from [the Visible Human Project](https://www.nlm.nih.gov/databases/download/vhp.html). 

```python
from medsim3d.vhp.downloader import VHPDownloader
vhp_downloader=VHPDownloader()
vhp_downloader.download_datasets(
    gender="Male", # Male or Female
    body_part="head", # Options: abdomen, head, legs, pelvis, thighs, thorax
    save_folder="datasets/male/head")
```

### Credits

- [The NLM Visible Human Project](https://www.nlm.nih.gov/research/visible/visible_human.html)

### License

The `MedSim3D` toolkit is provided by [Donghua Chen](https://github.com/dhchenx) with MIT License.

