# Beam Search NLP

## Beam Search

条件付き確率場とも考えられる単語の連なりから、ネットワークの探索範囲を限定することでそれなりの良い答えを得る方法。  

<div align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/49210846-77fcc900-f401-11e8-920f-3341bca0837b.png">
</div>
<div align="center"> 図1. 幅2の探索例 </div>


難しいのは、単語同士の関連する確率の表現で、できるだけながい語を見るほうが望ましいというネットワークの結合の重要度を与える必要がある。  

# 処理フロー

## 分かち書き
```console
$ python3 10-tokenize.py 
```

## 条件付き確率場の生成
```console
$ python3 20-term_chaine.py
```

## DBの結合
```console
$ python3 30-scan_level_db.py
```

## DBの内容の書き出し
```console
$ python3 40-dump_level.py
```

## pythonのデータタイプに変換
```console
$ python3 50-make_term_term_freq.py
```

## 探索
単純にビーム数4でやるとそれなりに安定したそれっぽい言葉の連なりが得られます

例:
```
```



