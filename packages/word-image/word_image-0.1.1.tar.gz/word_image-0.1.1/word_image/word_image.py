import os.path
from dataclasses import dataclass
from random import randint, choice, choices, random, sample
import numpy as np
from imgaug import augmenters as iaa
from PIL import Image, ImageDraw, ImageFont


@dataclass
class WordConfig:
    """a collection of values for word image generation

    Attributes:
        text_len (tuple): min,max ranges for random word length
        font_size (tuple): min,max PIL font size (not font points)
        base_bg_color (tuple): rgb int tuple for the base color
        base_bg_color_proba (float): probability of using the base bg color
        base_text_color (tuple): rgb int tuple for the base text color
        base_text_color_proba (float): probability of using the base text color
        bg_color_r (tuple): min,max ints for random background red value
        bg_color_g (tuple): min,max ints for random background green value
        bg_color_b (tuple): min,max ints for random background blue value
        text_color_r (tuple): min,max ints for random text red value
        text_color_g (tuple): min,max ints for random text green value
        text_color_b (tuple): min,max ints for random text blue value
        x_pad (tuple): min,max ints for x-wise padding
        y_pad (tuple): min,max ints for y-wise padding
        text_letters (list): chars that will be used in random text
        letter_freqs (list): character frequencies for random text
    """
    text_len = (1, 20)
    font_size = (12, 50)

    base_bg_color = (255, 255, 255)
    base_bg_color_proba = 0.75

    base_text_color = (0, 0, 0)
    base_text_color_proba = 0.75

    bg_color_r = (0, 255)
    bg_color_g = (0, 255)
    bg_color_b = (0, 255)
    text_color_r = (0, 255)
    text_color_g = (0, 255)
    text_color_b = (0, 255)

    x_pad = (0, 10)
    y_pad = (0, 10)

    # random word letter frequencies gathered from
    # pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
    text_letters = [
        "e",
        "t",
        "a",
        "o",
        "i",
        "n",
        "s",
        "r",
        "h",
        "d",
        "l",
        "u",
        "c",
        "m",
        "f",
        "y",
        "w",
        "g",
        "p",
        "b",
        "v",
        "k",
        "x",
        "q",
        "j",
        "z",
    ]
    letter_freqs = [
        1202,
        910,
        812,
        768,
        731,
        695,
        628,
        602,
        592,
        432,
        398,
        288,
        271,
        261,
        230,
        211,
        209,
        203,
        182,
        149,
        111,
        69,
        17,
        11,
        10,
        7,
    ]


@dataclass
class AugConfig:
    """a collection of values for image augmentation

    Attributes:
        crop_pct (tuple): min,max floats for horizontal crop
        blur_sigma (tuple): min,max floats for gaussian blur sigma
        g_noise_loc (float): gaussian noise loc
        g_noise_scale (tuple): min,max floats for gaussian noise scale
        sp_noise_proba (tuple): min,max floats for salt & pepper noise
        x_shear (tuple): min,max floats for x shear degrees
        y_shear (tuple): min,max floats for y shear degrees
        rotation (tuple): min,max floats for rotation degrees
    """
    crop_pct = (0.0, 0.25)
    blur_sigma = (0.0, 1.5)
    g_noise_loc = 0
    g_noise_scale = (0, 10)
    sp_noise_proba = (0.01, 0.25)
    x_shear = (-20, 20)
    y_shear = (-20, 20)
    rotation = (-10, 10)


class WordSet(object):
    """a class for managing the generation of word images
    """

    def __init__(self, add_default_fonts=True):
        """constructor for WordSet objects

        Args:
            add_default_fonts (bool): add a set of standard fonts -- assumes fonts live in /usr/share/fonts

        Attributes:
            word_cfg (WordConfig): a collection of word generation values
            aug_cfg (AugConfig): a collection of image augmentation values
            aug_font_choices (list): a list of fonts to use in random word generation
            _wordlist (list): a list of words to generate word images from (use set_wordlist to set this list)
            _fontlib (dict): dict of font filenames indexed by a short name
        """
        super().__init__()

        self._wordlist = None
        self._fontlib = {}

        self.word_cfg = WordConfig()
        self.aug_cfg = AugConfig()
        self.aug_font_choices = []

        if add_default_fonts:
            self.add_default_fonts()

    def add_default_fonts(self):
        """add a set of default fonts to the fontlib

        assumes a linux system with msft & cm fonts are installed:
        ttf-mscorefonts-installer and fonts-cmu

        Args:
            none

        Returns:
            nothing
        """
        self.add_font("times", "/usr/share/fonts/truetype/msttcorefonts/times.ttf")
        self.add_font("arial", "/usr/share/fonts/truetype/msttcorefonts/arial.ttf")
        self.add_font("cm serif", "/usr/share/fonts/truetype/cmu/cmunrm.ttf")
        self.add_font("cm sans", "/usr/share/fonts/truetype/cmu/cmunss.ttf")

    def add_font(self, font_name, font_path):
        """add a font to the fontlib

        Args:
            font_name (str): short name for the font
            font_path (str): file path to the font

        Returns:
            nothing
        """
        # bail out if args are bad
        if font_name in self._fontlib:
            return

        if not os.path.isfile(font_path):
            return

        # add the font to fontlib and the keys to font choices
        self._fontlib[font_name] = font_path
        self.aug_font_choices = list(self._fontlib)

    def get_imgaug_pipeline(self, config=None):
        """get an image augmentation pipeline function

        Calling the pipeline function on an image will apply operations as specified by the config dataclass.
        The pipeline will apply at least one of: crop, blur, shear/rotate, noise

        Args:
            config (AugConfig): the AugConfig object that specifies the desired ranges for the pipeline's operations

        Returns:
            a function that expects a numpy uint8 array image (W,H,C)
        """
        if config is None:
            config = self.aug_cfg

        crop = iaa.CropAndPad(
            percent=(
                [config.crop_pct[0], -config.crop_pct[1]],
                0,
                [config.crop_pct[0], -config.crop_pct[1]],
                0,
            ),
            keep_size=False,
        )
        blur = iaa.GaussianBlur(sigma=config.blur_sigma)
        g_noise = iaa.AdditiveGaussianNoise(
            loc=config.g_noise_loc, scale=config.g_noise_scale
        )
        sp_noise = iaa.SaltAndPepper(p=config.sp_noise_proba)
        # shot_noise = iaa.imgcorruptlike.ShotNoise(severity=2)
        rotate = iaa.Rotate(config.rotation, mode="edge", fit_output=True)
        shear_x = iaa.ShearX(config.x_shear, mode="edge", fit_output=True)
        shear_y = iaa.ShearY(config.y_shear, mode="edge", fit_output=True)

        pipeline = iaa.SomeOf(
            (1, None),
            [
                crop,
                blur,
                iaa.SomeOf((1, None), [shear_x, shear_y, rotate]),
                iaa.OneOf([g_noise, sp_noise]),
            ],
            random_order=False,
        )
        return pipeline

    @staticmethod
    def get_random_text(min_len, max_len, letters, freqs):
        """generate a random text string

        Args:
            min_len (int): the minimum string length to return
            max_len (int): the maximum string length to return
            letters (list): list of chars to sample from
            freqs (list): list of integer letter frequencies

        Returns:
            string
        """
        len = randint(min_len, max_len)
        text = choices(letters, k=len, weights=freqs)
        text = "".join(text)
        if random() > 0.8:
            text = text.capitalize()
        return text

    @staticmethod
    def get_biased_rgb(base_color, base_proba, rand_ranges):
        """generate an RGB color tuple - either the base color or a random one

        base_proba controls how often the base_color will be returned

        Args:
            base_color (tuple): int RGB tuple for the base color
            base_proba (float): probability of returning the base color
            rand_ranges (tuple): int RGB ranges for the random color, formatted as (R_min, R_max, G_min, G_max, B_min, B_max)

        Returns:
            RGB int tuple
        """
        if random() < base_proba:
            return base_color
        else:
            return (
                randint(rand_ranges[0], rand_ranges[1]),
                randint(rand_ranges[2], rand_ranges[3]),
                randint(rand_ranges[4], rand_ranges[5]),
            )

    def get_wordimage_generator(
        self,
        bg_color=None,
        text_color=None,
        font_name=None,
        font_size=None,
        x_pad=None,
        y_pad=None,
        config=None
    ):
        """get a function that will produce a word image

        If an argument is assigned a value, that value will be constant for all images created by the resulting function e.g. if bg_color is set to (0,0,0) every image will have a black background.

        If the argument's value is not assigned (left as None), a function that yields random values from within a desired range will be created. These ranges are defined in the object's WordConfig object or the supplied config arg.

        Args:
            bg_color (tuple): RGB int tuple
            text_color (tuple): RGB int tuple
            font_name (str): font name
            font_size (int): font size
            x_pad (int): x pad in pixels
            y_pad (int): y pad in pixels
            config - a WordConfig object (default: uses self.word_cfg)

        Returns:
            a function with signature: fn(text=None) -> PIL.Image
        """
        if config is None:
            config = self.word_cfg

        # get the background color generator
        if bg_color is None:
            rand_ranges = (
                config.bg_color_r[0],
                config.bg_color_r[1],
                config.bg_color_g[0],
                config.bg_color_g[1],
                config.bg_color_b[0],
                config.bg_color_b[1],
            )
            bg_color_fn = lambda: self.get_biased_rgb(
                config.base_bg_color, config.base_bg_color_proba, rand_ranges
            )
        else:
            bg_color_fn = lambda: bg_color

        # get the text color generator
        if text_color is None:
            rand_ranges = (
                config.text_color_r[0],
                config.text_color_r[1],
                config.text_color_g[0],
                config.text_color_g[1],
                config.text_color_b[0],
                config.text_color_b[1],
            )
            text_color_fn = lambda: self.get_biased_rgb(
                config.base_text_color, config.base_text_color_proba, rand_ranges
            )
        else:
            text_color_fn = lambda: text_color

        # get the font name generator
        if font_name is None:
            font_name_fn = lambda: choice(self.aug_font_choices)
        else:
            font_name_fn = lambda: font_name

        # get the font size generator
        if font_size is None:
            font_size_fn = lambda: randint(config.font_size[0], config.font_size[1])
        else:
            font_size_fn = lambda: font_size

        # get the x & y pad generators
        if x_pad is None:
            x_pad_fn = lambda: randint(config.x_pad[0], config.x_pad[1])
        else:
            x_pad_fn = lambda: font_size

        if y_pad is None:
            y_pad_fn = lambda: randint(config.y_pad[0], config.y_pad[1])
        else:
            y_pad_fn = lambda: font_size

        # put together the image generation function
        return lambda text: self._get_wordimage(
            text,
            bg_color_fn,
            text_color_fn,
            font_name_fn,
            font_size_fn,
            x_pad_fn,
            y_pad_fn,
        )

    def get_wordimage(self, text=None):
        """simple word image generator with minimal configurability

        Generates a word image with a black text serif font on a white background and no padding

        Args:
            text (str): the word to generate an image of or a random word if None
        """
        if text is None:
            text = self.get_rand_text(
                self.word_cfg.text_len[0],
                self.word_cfg.text_len[1],
                self.word_cfg.text_letters,
                self.word_cfg.letter_freqs,
            )

        bg_color_fn = lambda: (255, 255, 255)
        text_color_fn = lambda: (0, 0, 0)
        font_name_fn = lambda: "cm serif"
        font_size_fn = lambda: 38
        x_pad_fn = lambda: 0
        y_pad_fn = lambda: 0

        return self._get_wordimage(
            text,
            bg_color_fn,
            text_color_fn,
            font_name_fn,
            font_size_fn,
            x_pad_fn,
            y_pad_fn,
        )

    def _get_wordimage(
        self,
        text,
        bg_color_fn,
        text_color_fn,
        font_name_fn,
        font_size_fn,
        x_pad_fn,
        y_pad_fn,
    ):
        """generate a word image using several functions to determine specific details such as color, font, and padding

        Use get_wordimage_generator to get a function that will
        manage all of the argument generation functions expected by this
        method. This allows you to provide specific values for arguments should be
        constant and let the generator create sampling functions for the other
        arguments.

        As a warning, this method has no range checking at all. We're trying to
        eliminate conditionals in here, so this method is (intentionally) brittle.
        All argument functions should take no args

        Args:
            text (string): the text to draw
            bg_color_fn (function): function that returns a tuple of 3 ints
            text_color_fn (function): function that returns a tuple of 3 ints
            font_name_fn (function): function that returns a string
            font_size_fn (function: function that returns an int
            x_pad_fn (function): function that returns an int
            y_pad_fn (function): function that returns an int

        Returns:
            a PIL Image
        """
        # get values from the generator functions
        font_name = font_name_fn()
        font_size = font_size_fn()
        bg_color = bg_color_fn()
        text_color = text_color_fn()
        x_pad = x_pad_fn()
        y_pad = y_pad_fn()

        # generate the image
        font_path = self._fontlib[font_name]
        im_font = ImageFont.FreeTypeFont(font=font_path, size=font_size)

        (text_width, text_height), (x_offset, y_offset) = im_font.font.getsize(text)
        img_shape = (text_width + 2 * x_pad, text_height + 2 * y_pad)

        text_image = Image.new("RGB", img_shape, color=bg_color)

        imdraw = ImageDraw.Draw(text_image)
        xy = (-x_offset + x_pad, 0 + y_pad)
        imdraw.text(xy, text, font=im_font, anchor="lt", fill=text_color)

        return text_image

    def set_wordlist(self, word_list):
        """set the wordlist to use for sampling random words

        Args:
            word_list (list): a list of strings

        Returns:
            nothing
        """
        self.wordlist = word_list.copy()

    def get_random_batch(self, batch_size, do_augmentation=True):
        """get a batch of randomly generated words and images

        Args:
            batch_size (int): the number of wordimages to generate
            do_augmentation (bool): apply image augmentation to the words

        Returns:
            tuple of a list of strings and list of PIL Images
        """
        min_len = self.word_cfg.text_len[0]
        max_len = self.word_cfg.text_len[1]
        letters = self.word_cfg.text_letters
        freqs = self.word_cfg.letter_freqs
        words = [
            self.get_random_text(min_len, max_len, letters, freqs)
            for _ in range(batch_size)
        ]
        return words, self.get_batch(words, do_augmentation)

    def get_wordlist_batch(self, batch_size, do_augmentation=True):
        """get a batch of wordimages sampled from the wordlist

        use set_wordlist to specify a set of words to sample from

        Args:
        batch_size (int): the number of words to return
        do_augmentation (bool): apply image augmentation to the words

        Returns:
            tuple of a list of strings and list of PIL Images
        """
        if self.wordlist is None:
            return None
        words = sample(self.wordlist, k=batch_size)
        return words, self.get_batch(words, do_augmentation)

    def get_batch(self, words, do_augmentation=True):
        """get a list of wordimages from a list of words

        Args:
            words (list): a list of strings
            do_augmentation (bool): apply image augmentation to the words

        Returns:
            a list of images (order preserved)
        """
        wordgen_fn = self.get_wordimage_generator()
        images = [wordgen_fn(word) for word in words]
        import pdb;pdb.set_trace()
        if do_augmentation:
            aug_fn = self.get_imgaug_pipeline()
            images = [aug_fn(image=np.array(image, dtype=np.uint8)) for image in images]
            images = [Image.fromarray(np.uint8(image)) for image in images]
        return images
