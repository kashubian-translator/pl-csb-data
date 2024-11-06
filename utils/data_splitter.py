import random


def load_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sentences = f.readlines()
    return sentences


def save_sentences(file_path, sentences):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(sentences)


def split_data(train_size=0.8, val_size=0.1, test_size=0.1):
    src_sentences = load_sentences('dataset.csb.txt')
    trg_sentences = load_sentences('dataset.pl.txt')
    assert len(src_sentences) == len(trg_sentences), "Source and target files must have the same number of sentences."

    num_sentences = len(src_sentences)
    indices = list(range(num_sentences))
    random.shuffle(indices)

    train_split = int(train_size * num_sentences)
    val_split = int(val_size * num_sentences)

    train_indices = indices[:train_split]
    val_indices = indices[train_split:train_split + val_split]
    test_indices = indices[train_split + val_split:]

    train_src = [src_sentences[i] for i in train_indices]
    train_trg = [trg_sentences[i] for i in train_indices]
    save_sentences('../data/input/train.src', train_src)
    save_sentences('../data/input/train.trg', train_trg)

    val_src = [src_sentences[i] for i in val_indices]
    val_trg = [trg_sentences[i] for i in val_indices]
    save_sentences('../data/input/val.src', val_src)
    save_sentences('../data/input/val.trg', val_trg)

    test_src = [src_sentences[i] for i in test_indices]
    test_trg = [trg_sentences[i] for i in test_indices]
    save_sentences('../data/input/test.src', test_src)
    save_sentences('../data/input/test.trg', test_trg)
