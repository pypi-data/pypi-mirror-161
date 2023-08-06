import time
from typing import Any, Dict
import os
import dill


def am_tracking(
        pickle_obj: Any,
        pickle_file_main_name: str,
        metrics: Dict = None,
        pickle_file_path: str = None,
        ext_file_name=".pkl"
):
    '''建模调参过程的记录工具

    Parameters
    ----------
    pickle_obj: Any
        pickle对象
    pickle_file_main_name: str
        pickle文件前缀
    metrics: Dict
        评价指标字典
    pickle_file_path: str
        pickle文件夹位置
    ext_file_name: str
        pickle文件扩展名，默认.pkl

    Returns
    -------
    final_file_name:str
        最终文件名称
    '''
    metrics_str = ""
    if metrics:
        for k, v in metrics.items():
            metrics_str = metrics_str + "_" + "..".join([str(k), str(v)])

    if not pickle_file_path:
        pickle_file_path = ""

    if not os.path.exists(pickle_file_path):
        os.makedirs(pickle_file_path)

    time_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    final_file_name = "_".join([pickle_file_main_name + metrics_str, time_str])
    final_file_name = final_file_name + ext_file_name
    abs_final_file_name = os.path.join(pickle_file_path, final_file_name)
    with open(abs_final_file_name, "wb") as dill_file:
        dill.dump(pickle_obj, dill_file)

    return final_file_name
