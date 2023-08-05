import argparse
import numpy as np
from PIL import Image
from word_image import WordSet
import matplotlib.pyplot as plt


def get_args():
    parser = argparse.ArgumentParser(description='word image generation demo')
    parser.add_argument('--word', help='the word to render')
    parser.add_argument('--nw', type=int, help='the number of words to generate', default=5)
    parser.add_argument('--na', type=int, help='the number of image augmentations per word', default=10)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    ws = WordSet()
    aug_gen_fn = ws.get_wordimage_generator()
    aug_pipeline = ws.get_imgaug_pipeline()

    n_words = args.nw
    n_augs = args.na

    if args.word is None:
        min_len = ws.word_cfg.text_len[0]
        max_len = ws.word_cfg.text_len[1]
        letters = ws.word_cfg.text_letters
        freqs = ws.word_cfg.letter_freqs
        words = [ws.get_random_text(min_len, max_len, letters, freqs) for _ in range(n_words)]
    else:
        words = [args.word for _ in range(n_words)]

    images = []
    for word in words:
        base_image = aug_gen_fn(word)
        images.append(base_image)
        for j in range(n_augs):
            aug_image = aug_pipeline(image=np.array(base_image, dtype=np.uint8))
            images.append(Image.fromarray(np.uint8(aug_image)))

    _, axs = plt.subplots(n_words, n_augs+1, figsize=(10,10))
    axs = axs.flatten()
    for ax, image in zip(axs, images):
        ax.imshow(image)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()
