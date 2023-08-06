# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['thunder',
 'thunder.citrinet',
 'thunder.data',
 'thunder.huggingface',
 'thunder.quartznet',
 'thunder.text_processing']

package_data = \
{'': ['*']}

install_requires = \
['editdistance>=0.6.0,<0.7.0',
 'hydra-core>=1.1.2,<2.0.0',
 'importlib-metadata>=4.12.0,<5.0.0',
 'num2words>=0.5.10,<0.6.0',
 'protobuf==3.18.1',
 'pytorch-lightning>=1.7.0,<2.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'torch>=1.12,<2.0',
 'torchaudio>=0.12,<0.13',
 'torchmetrics>=0.8,<0.10',
 'transformers>=4.20.1,<5.0.0',
 'wget>=3.2,<4.0']

setup_kwargs = {
    'name': 'thunder-speech',
    'version': '3.2.0',
    'description': 'A Hackable speech recognition library',
    'long_description': '[![codecov](https://codecov.io/gh/scart97/thunder-speech/branch/master/graph/badge.svg?token=USCEGEGM3D)](https://codecov.io/gh/scart97/thunder-speech)\n![Test](https://github.com/scart97/thunder-speech/workflows/Test/badge.svg)\n[![docs](https://img.shields.io/badge/docs-read-informational)](https://scart97.github.io/thunder-speech/)\n\n# Thunder speech\n\n> A Hackable speech recognition library.\n\nWhat to expect from this project:\n\n- End-to-end speech recognition models\n- Simple fine-tuning to new languages\n- Inference support as a first-class feature\n- Developer oriented api\n\nWhat it\'s not:\n\n- A general-purpose speech toolkit\n- A collection of complex systems that require thousands of gpu-hours and expert knowledge, only focusing on the state-of-the-art results\n\n\n## Quick usage guide\n\n### Install\n\nInstall the library from PyPI:\n\n```\npip install thunder-speech\n```\n\n\n### Load the model and train it\n\n```py\nfrom thunder.registry import load_pretrained\nfrom thunder.quartznet.compatibility import QuartznetCheckpoint\n\n# Tab completion works to discover other QuartznetCheckpoint.*\nmodule = load_pretrained(QuartznetCheckpoint.QuartzNet5x5LS_En)\n# It also accepts the string identifier\nmodule = load_pretrained("QuartzNet5x5LS_En")\n# Or models from the huggingface hub\nmodule = load_pretrained("facebook/wav2vec2-large-960h")\n```\n\n### Export to a pure pytorch model using torchscript\n\n```py\nmodule.to_torchscript("model_ready_for_inference.pt")\n\n# Optional step: also export audio loading pipeline\nfrom thunder.data.dataset import AudioFileLoader\n\nloader = AudioFileLoader(sample_rate=16000)\nscripted_loader = torch.jit.script(loader)\nscripted_loader.save("audio_loader.pt")\n```\n\n### Run inference in production\n\n``` python\nimport torch\nimport torchaudio\n\nmodel = torch.jit.load("model_ready_for_inference.pt")\nloader = torch.jit.load("audio_loader.pt")\n# Open audio\naudio = loader("audio_file.wav")\n# transcriptions is a list of strings with the captions.\ntranscriptions = model.predict(audio)\n```\n\n## More quick tips\n\nIf you want to know how to access the raw probabilities and decode manually or fine-tune the models you can access the documentation [here](https://scart97.github.io/thunder-speech/quick%20reference%20guide/).\n\n## Contributing\n\nThe first step to contribute is to do an editable installation of the library:\n\n```\ngit clone https://github.com/scart97/thunder-speech.git\ncd thunder-speech\npoetry install\npre-commit install\n```\n\nThen, make sure that everything is working. You can run the test suit, that is based on pytest:\n\n```\nRUN_SLOW=1 poetry run pytest\n```\n\nHere the `RUN_SLOW` flag is used to run all the tests, including the ones that might download checkpoints or do small training runs and are marked as slow. If you don\'t have a CUDA capable gpu, some tests will be unconditionally skipped.\n\n\n## Influences\n\nThis library has heavy influence of the best practices in the pytorch ecosystem.\nThe original model code, including checkpoints, is based on the NeMo ASR toolkit.\nFrom there also came the inspiration for the fine-tuning and prediction api\'s.\n\nThe data loading and processing is loosely based on my experience using fast.ai.\nIt tries to decouple transforms that happen at the item level from the ones that are efficiently implemented for the whole batch at the GPU.\nAlso, the idea that default parameters should be great.\n\nThe overall organization of code and decoupling follows the pytorch-lightning ideals, with self-contained modules that try to reduce the boilerplate necessary.\n\nFinally, the transformers library inspired the simple model implementations, with a clear separation in folders containing the specific code that you need to understand each architecture and preprocessing, and their strong test suit.\n',
    'author': 'scart97',
    'author_email': 'scart.lucas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://scart97.github.io/thunder-speech/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
