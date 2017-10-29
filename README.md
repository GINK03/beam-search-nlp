# Generic-N-Gram Markov Chaine

## Markov Chaineを実装する

## 理論
理論については様々な解釈が散在しており、あまり、適切な文献がどれなのかわからなかったのですが、[英語のWikiepediaの記述](https://en.wikipedia.org/wiki/Markov_chain)をベースに行なっています 

1. N階マルコフ連鎖と呼ばれるもので実装していまして、3つ前までの携帯素から次の単語の確率分布を生成します  

2. 確率分布に従う形で、一つの出力確率として採択して、文章に続く文字とします。

3. 1に戻ります

## Requirements(必要用件)
- Python3
- nvme(高速なディスクでないとKVSがパフォーマンスを発揮できませんが、実行だけなら必要ないかも)
- leveldb(確率分布を保存するKVS)
- plyvel(leveldbのpythonラッパー)
- numpy
- MeCab(形態素解析機)
- メモリできるだけたくさん
- コーパス(600万テキストほど)

今回使用したデータセットだけなら、[minioというサーバで公開](http://121.2.69.245:10001/minio/markov-chaine-data/)します  

## 学習

**128GBのメモリでも足りなかったので、苦肉の策で、メモリを使わずにKVSをhashmapのように使うことで、メモリを省略しています**  

#### 分かち書きしてコーパスを形態素粒度に変換する  
```console
$ python3 prepare.py --wakati
```

#### ngramの特徴量を抽出し、発生頻度をカウントします(要KVSと時間)
```console
$ python3 prepare.py --term_chaine
```

#### 出現頻度から確率分布を作成して、モデルを統合します
```console
$ python3 prepare.py --numpy
$ python3 prepare.py --wrapup
```

## 予想

**初期値を適当にハードコードで与えていますが、任意の文字を与えることもできますが、KVSのキーに入っている必要があります**  

```console
$ python3 prepare.py --sample
```



