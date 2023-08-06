# Morphology annotation for budding yeasts

## Installation

```sh
pip install maby
```

Once installed, use command `maby-init` to download the pre-trained models and example images. These will be stored in your python environment, so you may need to use special permissions. We recommend using a pythong environment, such as `conda`.

## Training
Once the package is installed, the command `maby-train` will be accessible from the command line.

```sh
maby-train --directory /path/to/image
```

## Evaluating
To evaluate the performance of the trained model on the validation data, use the command  `maby-evaluate`.

It requires a path to a results directory as input.
```sh
maby-evaluate --directory /path/to/directory --checkpoint /path/to/model.pt
```

## Visualizing results with napari
We visualize results with [napari](https://napari.org/index.html) using the command:

```sh
maby-visualize
```

By default, it loads a network to predict the location of the nucleus, as well as an example time-lapse.
Click `Run` to make a prediction on the example. This may take up to a minute, depending on your hardware.

You can choose which model to run the prediction with in the dropdown menu. The `nucleus` and `vacuole` models are pre-trained, but the `custom`  model is loaded with random initial weights.

If you want to predict on a different `.tif` file, you can choose an image and press `Load Image` to load it into the viewer. The bright field data will be automatically normalized between -1 and 1.

If you want to use a different model trained with `maby-train` on your own dataset, locate the checkpoint file and click `Load model`. Note that this will overwrite which ever model is currently loaded, so we suggest that you first switch to the `custom` model in the model picking pane.
