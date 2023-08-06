import openbayes_serving as serv


class Predictor:
    def __init__(self):
        """
        负责加载相应的模型以及对元数据的初始化
        """
        pass

    def predict(self, json):
        """
        在每次请求都会被调用
        接受 HTTP 请求的内容（`json`)
        进行必要的预处理（preprocess）后预测结果，
        最终将结果进行后处理（postprocess）并返回给调用方

        Args:
            json: 请求的数据

        Returns:
            预测结果
        """
        return json

if __name__ == '__main__':  # 如果直接执行了 predictor.py，而不是被其他文件 import
    serv.run(Predictor)     # 开始提供服务
