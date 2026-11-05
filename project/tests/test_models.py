from pathlib import Path
import time
import numpy as np
import onnxruntime as ort
import pytest

@pytest.mark.parametrize('name',['mainInGameModel.onnx','tileDetector.onnx','closeTileDetector.onnx'])
def test_bundled_model_cpu_inference(name):
    path=Path(__file__).resolve().parents[1]/'models'/name
    options=ort.SessionOptions()
    options.intra_op_num_threads=2
    session=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])
    inputs={}
    for spec in session.get_inputs():
        shape=[d if isinstance(d,int) and d>0 else 1 for d in spec.shape]
        inputs[spec.name]=np.zeros(shape,dtype=np.float32)
    outputs=session.run(None,inputs)
    assert outputs and all(np.isfinite(o).all() for o in outputs)

def test_actual_detect_pipeline(application):
    from detect import Detect
    import utils
    cfg=utils.load_toml_as_dict('cfg/general_config.toml').copy()
    cfg.update(cpu_or_gpu='cpu',used_threads=2)
    utils.save_dict_as_toml(cfg,'cfg/general_config.toml')
    root=Path(__file__).resolve().parents[1]
    for name in ('mainInGameModel.onnx','tileDetector.onnx'):
        detector=Detect(str(root/'models'/name))
        result=detector.detect_objects(np.zeros((1080,1920,3),dtype=np.uint8))
        assert result is not None
