import numpy as np
from copy import deepcopy
from .model import Model
import json


class Logistic(Model):

    def __init__(self, train_data: list=[], signs: list=[], theta: float=10e-6):
        super(Logistic, self).__init__(train_data, signs, theta)

    def predict(self, text: str):
        """
        @param text <str> : 文章
        @return <int> : どちらのクラスに属するかを2値で返す(+1 or -1)
        @return <float> : +1クラスに属する確率
                          (0.5以上ならば1つ目の返り値は+1になる)
        どちらのクラスに属するかと+1クラスに属する確率を返す
        """

        vec = self.getvec(text)
        prob = self.sigmoid(np.dot(vec, self.w))
        class_ = 1 if prob >= 0.5 else -1
        return class_, prob, vec

    def predict_using_vec(self, vec):

        prob = self.sigmoid(np.dot(vec, self.w))
        class_ = 1 if prob >= 0.5 else -1
        return class_, prob, vec

    def train_one_step(self, i: int):
        """
        @param i <int> : 学習データの位置，インデックス
        学習を1ステップ進める
        確率的勾配降下法による実装
        """

        # 学習データをコピー
        w_old = deepcopy(self.w)
        eta = 1.0 / np.sqrt(self.t + 10)
        # 学習する値を取得
        y = self.signs[i]
        f = self.train_data[i]
        s = y * (1 - self.prob_val(y, f)) * f
        self.w += eta * s
        norm = np.linalg.norm(self.w - w_old)
        if self.cnt < 100 and norm > 0.1:
            if self.cnt > 0:
                with open("static/json/" + str(self.cnt - 1) + ".json", "r") as f:
                    before = json.load(f)
                    bline = before["line"]
                    bvec = before["vec"]
            else:
                bline = {"x": 0, "y": 0}
                bvec = []
            dic = {"line": {"x": float(self.w[0]), "y": float(self.w[1])},
                   "bline": {"x": bline["x"], "y": bline["y"]},
                    "vec": bvec +
                    [{"sign": self.signs[i],
                        "x": float(self.train_data[i][0]),
                        "y": float(self.train_data[i][1]),
                        "text": self.sentences[i]}
                    ]
                  }
            self.dict_to_json(dic)
            self.cnt += 1
        if norm > 0.0 and norm < self.theta:
            self.end = True
        self.t += 1

    def prob_val(self, y: int, feature: np.array) -> float:
        """
        @param y <int> : クラス(-1 or 1)
        @param feature <list> : 素性
        @return <float> : ロジスティック回帰モデルにおける確率値(P(y|d))
        指定したクラスへ属する確率を返す(0 ~ 1 の間)
        """

        val = y * np.dot(self.w, feature)
        return self.sigmoid(val)

    def sigmoid(self, t: float) -> float:
        """
        @param t <float> : -∞ ~ +∞までの範囲の値のいずれか
        @return <float> : -1 ~ +1までの値のいずれか
        sigmoid 関数の値を返す
        """

        return 1 / (1 + np.exp(-t))