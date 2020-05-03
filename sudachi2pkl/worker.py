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
import glob
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from sudachi2pkl.parser import Parser


def worker(in_file, out_path, wkc_path):
    """ Worker

    :param in_file: 入力パス (knp file)
    :param out_path: 出力パス (directory)
    :param wkc_path: 分かち書き出力パス (directory)
    :return:
    """
    p = Parser(in_file, out_path, wkc_path)
    p()


def main():
    """ main

    :return:
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--in_path', help='in directory path', required=True)
    arg_parser.add_argument('-o', '--out_path', help='output path', default="out/")
    arg_parser.add_argument('-w', '--wakachi_path', help='output wakachi path', default=None)
    arg_parser.add_argument('-p', '--proc_num', help='process num', default=2)
    args = arg_parser.parse_args()

    out_path = os.path.abspath(args.out_path)
    wkc_path = os.path.abspath(args.wakachi_path)

    # リスト作成
    in_file_list = glob.glob(args.in_path + "/*.txt")
    with ProcessPoolExecutor(max_workers=args.proc_num) as pool:
        with tqdm(total=len(in_file_list)) as progress:
            futures = []

            for file in in_file_list:
                future = pool.submit(worker, file, out_path, wkc_path)
                future.add_done_callback(lambda p: progress.update())
                futures.append(future)

            results = []
            for future in futures:
                result = future.result()
                results.append(result)


if __name__ == "__main__":
    main()
