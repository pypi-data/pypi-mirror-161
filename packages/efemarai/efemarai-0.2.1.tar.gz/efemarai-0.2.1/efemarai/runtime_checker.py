import glob
import importlib
import os
import re
import signal
import sys
import traceback
from contextlib import contextmanager

import numpy as np
from PIL import Image

from efemarai.base_checker import BaseChecker
from efemarai.console import console


@contextmanager
def time_limit(identifier, seconds=5 * 60):
    def signal_handler(signum, frame):
        raise TimeoutError(f"{identifier} has timed out (limit {seconds} seconds)")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)


class RuntimeChecker(BaseChecker):
    def __init__(self, model, parent=None, datasets=None, project=None):
        if parent is None:
            parent = ""

        if datasets is None:
            datasets = []

        self._runtime = self._get_required_item(model, "runtime", parent)

        self._model = model
        self._parent = parent + ".runtime"
        self._datasets = datasets
        self._project = project

        self._variables = self._init_variables()

        self._entrypoints = {
            "load": self._get_entrypoint("load"),
            "predict": self._get_entrypoint("predict"),
        }

        batch = self._runtime.get("batch", {})
        self._batch_size = batch.get("max_size", 1)
        self._image_size = batch.get("image_size")

        if self._image_size is None:
            name = self._runtime["predict"]["entrypoint"]
            self._warning(
                f"Missing field 'image_size' (in '{self._parent}.batch') -"
                f" either provide it or ensure that your '{name}' function works"
                f" with images with different sizes. If all images in your datasets"
                f" have the same size you can ignore this warning."
            )

    def check(self):
        images = self._get_sample_images()

        try:
            self._load()
            predictions = self._predict(images)
        except TimeoutError as e:
            self._error(f"{e}")
        except Exception as e:
            console.print(":poop: Runtime Exception", style="red")

            # Drop stack frames of the checker execution
            lines = traceback.format_exc().split("\n")
            message = lines[:1] + lines[7:]

            console.print("\n".join(message)[:-1])
            raise AssertionError()

        self._check_predictions(images, predictions)

    def _load(self):
        with time_limit("'load' entrypoint"):
            return self._call("load")

    def _predict(self, images):
        self._variables["datapoint.image"] = images

        with time_limit("'predict' entrypoint"):
            return self._call("predict")

    def _init_variables(self):
        variables = {
            "model.runtime.device": self._get_device(),
        }

        for file in self._model.get("files", []):
            name = f"model.files.{file['name']}.url"
            value = file["url"]
            variables[name] = value

        return variables

    def _get_entrypoint(self, name):
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())

        definition = self._get_required_item(self._runtime, name, self._parent)
        entrypoint_parent = self._parent + "." + name

        entrypoint = self._get_required_item(
            definition, "entrypoint", entrypoint_parent
        )
        module_path, function_name = entrypoint.split(":")

        if not os.path.exists(f"{module_path.replace('.', '/')}.py"):
            self._error(
                f"Module '{module_path}' cannot be imported (in '{entrypoint_parent}')"
            )

        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            self._error(
                f"Unable to import '{module_path}' (in '{entrypoint_parent}')",
                print_exception=True,
            )

        try:
            function = getattr(module, function_name)
        except Exception as e:
            self._error(
                f"Unable to load '{function_name}' (in '{entrypoint_parent}')",
                print_exception=True,
            )

        return function

    def _get_device(self):
        device = self._runtime.get("device", "cpu")
        gpu_requested = device in ["gpu", "cuda"]
        return "cuda" if gpu_requested else "cpu"

    def _get_sample_images(self):
        images = []
        for dataset in self._datasets:
            pattern = os.path.join(dataset["data_url"], "**/*.*")
            for filename in glob.glob(pattern):
                try:
                    image = Image.open(filename)
                    if self._image_size is not None:
                        image.resize(self._image_size)
                    images.append(image)

                    if len(images) == self._batch_size:
                        return images
                except IOError:
                    continue

        if images:
            return images

        for _ in range(self._batch_size):
            data = np.random.rand(400, 400, 3) * 255
            images.append(Image.fromarray(data.astype(np.uint8)))
        return images

    def _call(self, function_name):
        function = self._entrypoints[function_name]

        args = {
            arg["name"]: self._resolve_variable(arg["value"])
            for arg in self._runtime[function_name].get("inputs", [])
        }

        self._save_inputs(function_name, args)

        result = function(**args)
        self._save_output(function_name, result)

        return result

    def _save_inputs(self, function_name, args):
        for name, value in args.items():
            self._variables[f"model.runtime.{function_name}.inputs.{name}"] = value

    def _save_output(self, function_name, result):
        output = self._runtime[function_name]["output"]
        name = output["name"]
        self._variables[f"model.runtime.{function_name}.output.{name}"] = result

    def _resolve_variable(self, value):
        if not (isinstance(value, str) and value.startswith("$")):
            return value

        match = re.match("\$\{?(?P<varname>[.\w]+)\}?", value)
        varname = match.group("varname")

        if varname not in self._variables:
            self._error(f"Unknown runtime variable '{varname}' (in '{self._parent}')")

        return self._variables[varname]

    def _check_predictions(self, images, predictions):
        if not isinstance(predictions, list):
            self._error(
                f"Predict function must return a {type([])},"
                f" but got {type(predictions)} (in '{self._parent}')"
            )

        if len(images) != len(predictions):
            self._error(
                f"Invalid number of predictions: expected {len(images)},"
                f" but got {len(predictions)} (in '{self._parent}')"
            )

        for image, prediction in zip(images, predictions):
            self._check_prediction(image, prediction)

    def _check_prediction(self, image, prediction):
        if not isinstance(prediction, dict):
            self._error(
                f"Each prediction must be a dict,"
                f" not {type(prediction)} (in '{self._parent})"
            )
        supported_keys = {
            "classes",
            "scores",
            "boxes",
            "masks",
            "segmentation",
            "regressed_values",
            "image_output",
        }
        actual_keys = set(prediction.keys())

        unsupported_keys = actual_keys - supported_keys
        if unsupported_keys:
            self._error(
                f"Unsupported prediction keys: {unsupported_keys}"
                f" (in '{self._parent}.predict')",
            )

        if self._project is not None:
            expected_keys = {
                "Classification": {"classes", "scores"},
                "ObjectDetection": {"boxes", "classes", "scores"},
                "InstanceSegmentation": {"masks", "boxes", "classes", "scores"},
                "SemanticSegmentation": {"segmentation"},
                "ImageRegression": {"regressed_values"},
            }[self._project["problem_type"]]

            missing_keys = expected_keys - actual_keys
            if missing_keys:
                self._error(
                    f"Missing prediction keys: {missing_keys}"
                    f" (in '{self._parent}.predict')"
                )

        self._check_masks(prediction)
        self._check_boxes(prediction)
        self._check_segmentation(prediction)

    def _check_masks(self, prediction):
        masks = prediction.get("masks")

        if masks is None:
            return

        if not isinstance(masks, list):
            self._error(
                f"Predicted masks per image must be a '{type([])}',"
                f" not '{type(masks)}' (in '{self._parent}.predict')"
            )

        if "classes" not in prediction:
            self._error("Missing 'classes' for predicted 'masks'")

        classes = prediction["classes"]

        if not isinstance(classes, list):
            self._error(
                f"Predicted masks classes per image must be a '{type([])}',"
                f" not '{type(classes)}' (in '{self._parent}.predict')"
            )

        if len(classes) != len(masks):
            self._error(
                f"Invalid prediction: got {len(classes)} class labels,"
                f"  but {len(masks)} masks (in '{self._parent}.predict')"
            )

        for mask in masks:
            mask_shape = np.array(mask).shape
            if len(mask_shape) != 2:
                self._error(
                    f"Invalid mask shape: {mask_shape}, "
                    f" expected mask shape is '[width, height]'"
                    f" (in '{self._parent}.predict')"
                )

            if np.min(mask) < 0 or np.max(mask) > 1:
                self._error(
                    f"Expected mask range is [0; 1], not"
                    f" [{np.min(mask)}; {np.max(mask)}] "
                    f" (in '{self._parent}.predict')"
                )

    def _check_boxes(self, prediction):
        boxes = prediction.get("boxes")

        if boxes is None:
            return

        if not isinstance(boxes, list):
            self._error(
                f"Predicted boxes per image must be a '{type([])}',"
                f" not '{type(masks)}' (in '{self._parent}.predict')"
            )

        if "classes" not in prediction:
            self._error("Missing 'classes' for predicted 'boxes'")

        classes = prediction["classes"]

        if not isinstance(classes, list):
            self._error(
                f"Predicted boxes classes per image must be a '{type([])}',"
                f" not '{type(classes)}' (in '{self._parent}.predict')"
            )

        if len(classes) != len(boxes):
            self._error(
                f"Invalid prediction: got {len(classes)} class labels,"
                f" but {len(boxes)} boxes (in '{self._parent}.predict')"
            )

        for box in boxes:
            x1, y1, x2, y2 = box
            if x1 > x2 or y1 > y2:
                self._error(
                    f"Invalid box coordinates: {box}, expected box format is"
                    f" [x1, y1, x2, y2] where (x1; y1) is the top-left corner"
                    f" and (x2; y2) is the bottom-right corner"
                    f" (in '{self._parent}.predict')"
                )

    def _check_segmentation(self, prediction):
        segmentation = prediction.get("segmentation")
        if segmentation is None:
            return

        segmentation_shape = np.asarray(segementation).shape

        if len(segmentation_shape) != 3 or segmentation_shape[0] != 1:
            self._error(
                f"Invalid mask shape: {mask_shape}, "
                f" expected mask shape is '[1, width, height]'"
                f" (in '{self._parent}.predict')"
            )
