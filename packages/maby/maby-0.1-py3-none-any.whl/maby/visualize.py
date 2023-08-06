import logging
import logging.config
from importlib.resources import path
from pathlib import Path

import napari
import torch
from magicgui import magicgui
from magicgui.widgets import ComboBox

from maby.data import MabyDataset
from maby.model import UNet
from maby.preprocessing import preprocess_target


@magicgui(model={"label": "Choose a model.", "filter": "*.pkl"},
          call_button="Load model")
def model_picker(model: Path):
    """Choose a model to load"""
    return model


@magicgui(image={"label": "Choose a image.", "filter": "*.tif"},
          call_button="Load image")
def image_picker(image: Path):
    """Choose an image to visualize"""
    return image


@magicgui(image={'label': 'Pick an Image'})
def inference(image: napari.layers.Image):
    """ Run image on the model given a path to an image."""
    return image


# Model choice
model_choice = ComboBox(name="Model", value="nucleus",
                        choices=["nucleus", "vacuole", "custom"])


def visualize_main():
    """Visualize the results on an image"""
    logger = logging.getLogger(__name__)
    logger.info('Visualizing model outputs...')
    models = dict(nucleus=UNet(5, 1), vacuole=UNet(5, 1))
    with path("maby", "models") as source:
        for name, model in models.items():
            model_path = source / f"{name}_model.pth"
            if model_path.exists():
                model.load_state_dict(torch.load(model_path)["model"])
    # Create viewer elements
    viewer = napari.Viewer()

    # Model loader
    def load_model(model_checkpoint):
        logger.info('Loading model checkpoint...')
        model = models[model_choice.get_value()]
        model.load_state_dict(torch.load(model_checkpoint)["model"])
        model.eval()
    model_picker.called.connect(load_model)

    # Image loader
    def load_image(image_path, name_suffix=""):
        logger.info('Loading image...')
        transform = None
        x, y = MabyDataset(image_path, transform=transform,
                           target_transform=preprocess_target).get_all()
        viewer.add_image(x.numpy(), name='Input' + name_suffix)
        viewer.add_image(y.numpy(), name='Target' + name_suffix,
                         colormap='green', opacity=0.5)
        return
    image_picker.called.connect(load_image)

    # Running inference
    def make_prediction(image):
        data = torch.from_numpy(image.data)
        model = models[model_choice.get_value()]
        with torch.no_grad():
            prediction = model(data).numpy()
        viewer.add_image(prediction, name='Prediction',
                         colormap='magenta', opacity=0.5)
    inference.called.connect(make_prediction)

    # Add a default image
    with path("maby", "examples") as source:
        load_image(source / "nucleus_example.tif", name_suffix=" Example")

    # Run the GUI
    viewer.window.add_dock_widget(inference)
    viewer.window.add_dock_widget(model_choice)
    viewer.window.add_dock_widget(model_picker)
    viewer.window.add_dock_widget(image_picker)
    napari.run()
    return


if __name__ == "__main__":
    model = visualize_main()
