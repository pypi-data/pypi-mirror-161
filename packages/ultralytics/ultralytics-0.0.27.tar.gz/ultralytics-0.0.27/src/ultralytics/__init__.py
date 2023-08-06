__version__ = '0.0.27'  # print(ultralytics.__version__)

import requests

from .main import connect_to_hub, train_model
from .yolov5_utils.general import LOGGER, PREFIX, check_requirements, colorstr, emojis, is_colab


def checks(verbose=True):
    # Check system software and hardware
    from .yolov5_wrapper import clone_yolo

    clone_yolo()

    print('Checking setup...')

    import os
    import shutil

    from .yolov5_utils.torch_utils import select_device  # imports

    check_requirements(('psutil', 'IPython'))
    import psutil
    from IPython import display  # to display images and clear console output

    if is_colab():
        shutil.rmtree('sample_data', ignore_errors=True)  # remove colab /sample_data directory

    if verbose:
        # System info
        # gb = 1 / 1000 ** 3  # bytes to GB
        gib = 1 / 1024 ** 3  # bytes to GiB
        ram = psutil.virtual_memory().total
        total, used, free = shutil.disk_usage("/")
        display.clear_output()
        s = f'({os.cpu_count()} CPUs, {ram * gib:.1f} GB RAM, {(total - free) * gib:.1f}/{total * gib:.1f} GB disk)'
    else:
        s = ''

    select_device(newline=False, version=__version__)
    print(emojis(f'Setup complete ✅ {s}'))


def login(api_key=''):
    # Login to Ultralytics HUB
    connect_to_hub(api_key, verbose=True)


def start(key=''):
    # Start training models with Ultralytics HUB. Usage: from src.ultralytics import start; start('API_KEY')
    api_key, model_id = split_key(key)
    train_model(api_key=api_key, model_id=model_id)


def reset_model(key=''):
    # Reset a trained model to an untrained state
    api_key, model_id = split_key(key)
    r = requests.post('https://api.ultralytics.com/model-reset',
                      json={"apiKey": api_key, "modelId": model_id})

    if r.status_code == 200:
        LOGGER.info(f"{PREFIX}model reset successfully")
        return
    LOGGER.warning(f"{PREFIX}model reset failure {r.status_code} {r.reason}")


def split_key(key=''):
    # Verify and split a 'api_key[sep]model_id' string, sep is one of '.' or '_'
    # key = 'ac0ab020186aeb50cc4c2a5272de17f58bbd2c0_RqFCDNBxgU4mOLmaBrcd'  # example
    # api_key='ac0ab020186aeb50cc4c2a5272de17f58bbd2c0', model_id='RqFCDNBxgU4mOLmaBrcd'  # example
    import getpass

    s = emojis(f'{PREFIX}Invalid API key ⚠️\n')  # error string
    if not key:
        key = getpass.getpass('Enter model key: ')
    sep = '_' if '_' in key else '.' if '.' in key else None  # separator
    assert sep, s
    api_key, model_id = key.split(sep)
    assert len(api_key) and len(model_id), s
    return api_key, model_id
