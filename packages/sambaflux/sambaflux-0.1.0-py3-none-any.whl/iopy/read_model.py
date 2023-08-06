"""
Model type detection and import.
"""

from cobra import io
from pathlib import Path
import logging
log = logging.getLogger(__name__)


def get_model_type(model_file):
    file_format = Path(model_file).suffix
    log.info("Detected " + file_format + " model.")
    if not (file_format == '.sbml' or file_format == '.xml' or file_format == '.json' or file_format == ".mat"):
        raise ValueError('Please use a json or sbml or mat file as your model.')
    return file_format


def import_model(model_file):
    log.info("Importing model...")
    file_format = get_model_type(model_file)
    if file_format == ".xml":
        model = io.read_sbml_model(model_file)
    elif file_format == '.json':
        model = io.load_json_model(model_file)
    elif file_format == '.mat':
        model = io.load_matlab_model(model_file)
    # TODO: Add checks for ID name formats (_LPAREN or _92_) (read_sbml_model has f_replace)
    # TODO: Add checks for SUBSYSTEM
    # TODO: Add checks for extra boundary reactions
    # TODO: Remove blocked reactions?
    # TODO: Fix GENE ASSOCIATION? Not sure if need genes
    return model
