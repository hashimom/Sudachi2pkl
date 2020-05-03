# -*- coding: utf-8 -*-
"""
 Copyright (c) 2020 Masahiko Hashimoto <hashimom@geeko.jp>
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""
import os
import argparse
import spacy
import pickle
import jaconv


class Parser:
    def __init__(self, in_file, out_path, wkc_path=None, encoding="utf-8-sig"):
        """ 解析

        :param in_file: 入力パス
        :param out_path: 出力パス (directory)
        """
        base, _ = os.path.splitext(os.path.basename(in_file))
        self._in_file = in_file
        self._nlp = spacy.load('ja_ginza')
        self._encoding = encoding

        self._out_file = out_path + "/" + base + ".pkl"
        if not os.path.isdir(out_path):
            os.makedirs(out_path)

        self._wkc_file = wkc_path + "/" + base + "_wkc.txt"
        if wkc_path is not None:
            if not os.path.isdir(out_path):
                os.makedirs(out_path)

    def __call__(self, file_type="pkl"):
        results = []
        for line in open(self._in_file, 'r', encoding=self._encoding):
            # 改行文字の削除
            line = line.replace('\n', '')

            # 「。」毎にパースを行う ※それ以外は未対応
            for context in line.replace("。", "。___").split("___"):
                if len(context) == 0:
                    continue

                # parse
                results.append(self._parse_context(context))

        with open(self._out_file, "wb") as of:
            pickle.dump(results, of)

        if self._wkc_file is not None:
            self.write_wkc(results)

    def _parse_context(self, context):
        infos = []
        doc = self._nlp(context)

        for sent in doc.sents:
            for token in sent:
                info = {
                    "text": token.orth_,          # テキスト
                    "reading": jaconv.kata2hira(token._.reading),  # 読みカナ
                    "lemma": token.lemma_,        # 基本形
                    "pos": token.pos_,            # 品詞
                    "tag": token.tag_,            # 品詞詳細
                    "inf": token._.inf,           # 活用情報
                    "dep": token.dep_,            # 係り受けの関係性
                    "dep_i": token.head.i,        # 係り受けの相手トークン番号
                    "dep_text": token.head.text,  # 係り受けの相手のテキスト
                }
                infos.append(info)

        return infos

    def write_wkc(self, results):
        with open(self._wkc_file, "w") as of:
            for result in results:
                text = ""
                for info in result:
                    text += info["text"] + " "

                of.writelines(text + "\n")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--in_path', help='in file path', required=True)
    arg_parser.add_argument('-o', '--out_path', help='out directory path', default="out/")
    arg_parser.add_argument('-w', '--wkc_path', help='out wakachi directory path', default=None)
    args = arg_parser.parse_args()

    p = Parser(args.in_path, args.out_path, args.wkc_path)
    p()
