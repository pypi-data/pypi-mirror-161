#### OVERVIEW
WordSet provides several ways to generate images of text. Various aspects can be configured to be randomly determined: text font, text color, background color, and padding. Additionally, image augmentation can be applied to the images in order to generate data for contrastive learning approaches.

![example image](/examples/WordSet_3_3.png)

#### USAGE
###### minimal configuration
```
from word_image import WordSet

ws = WordSet()
image = ws.get_wordimage('test')
```

###### all random features
```
from word_image import WordSet

ws = WordSet()
generator_fn = ws.get_augword_generator()
image = generator_fn('test')
```

###### random and fixed image features
```
from word_image import WordSet

ws = WordSet()
generator_fn = ws.get_augword_generator(
    bg_color=(255,0,0),
    text_color=(0,0,255),
    font_name="times",
    font_size=50,
    x_pad=5,
    y_pad=5,
    config=None)
image = generator_fn('test')
```

###### batch generation
```
from word_image import WordSet

ws = WordSet()

# get wordimages of randomly generated words
words, images = ws.get_random_batch(10)

# get wordimages from sampling a wordlist
wordlist = ['book', 'cat', 'artichoke', 'dinosaur', ...
ws.set_wordlist(wordlist)
words, images = ws.get_wordlist_batch(10)

# get specific wordimages
images = ws.get_batch(wordlist[10:20])
```


#### INTERFACE
###### core operations
- `get_wordimage_generator` - get a function that will return wordimages, you can specify which aspects of the resulting images will be constant or random.

###### batch operations
- `get_random_batch` - get a batch of wordimages using randomly generated text
- `get_wordlist_batch` - get a batch of wordimages sampled from the wordlist
- `get_batch` - get a batch of wordimages from a list of words

###### wordimage generation
- `get_wordimage` - straighforward wordimage generation, returns a black text on white background wordimage

###### configuration
- `add_default_fonts` - add a set of fonts to the wordset
- `add_font` - add a single font to the wordset
- `set_wordlist` - set a list of words to use when sampling wordimages

###### utility functions
- `get_imgaug_pipeline` - get a function that performs several image augmentation operations
- `get_random_text` - get a randomly generated string
- `get_biased_rgb` - get an RGB color: either a specific color or a randomly generated one. You specify the probability of returning the base color.



#### FONTS
By default, WordSet loads Times New Roman and Arial from the `msttcorefonts` set, and Computer Modern Serif and Computer Modern Sans Serif from the `cmu` fonts package. In Ubuntu, thses can be installed as follows:
```
sudo apt install ttf-mscorefonts-installer
sudo apt install fonts-cmu
```
This can be bypassed by setting add_default_fonts to False in the WordSet constructor:
```
from word_image import WordSet

ws = WordSet(add_default_fonts = False)
ws.add_font(<font_name>, <font_path>)
```


#### LIMITATIONS
- word_image has only been tested on Ubuntu 20
