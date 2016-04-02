#! /usr/bin/env python3

from preprocessing.zoningwriter import get_values
from hmm.trainer import make_model, train, get_success_rate
from utils.mnstreader import get_image_data, get_labels
from PIL import Image
import hmm.trainer as trainer
from time import time
from utils.softmax import softmax, softmax_denom, softmax_numerator

def zone(image_data, shade_count, image_size, resample_size):
    img = Image.new('L', image_size)
    img.putdata(image_data)
    return get_values(img, resample_size, shade_count)

def show_image(data, size):
    img = Image.new('L', size)
    print(size, len(data))
    print(data)

    m = 255 / max(data)
    def to_binary(p, m):
        if p * m < 128:
            return 0
        else:
            return 255

    img.putdata([x * m for x in data])
    img.show()

def get_data_sets(image_file, label_file, count, resample_size):
    images, size = get_image_data(image_file, count)
    labels = get_labels(label_file)[:count]

    data_sets = {}
    for i in range(count):
        label = labels[i]
        image = zone(images[i], shade_count, size, resample_size)

        if label in data_sets:
            data_sets[label].append(image)
        else:
            data_sets[label] = [image]
    return data_sets

def train_models(data_sets, hmms):
    begin = time()
    iterations = 2
    for label in data_sets:
        print('training: {}'.format(label))
        hmms[label] = train(hmms[label], data_sets[label], iterations)

    print('runtime: ', time() - begin, 's')
    return hmms

def run_tests(data_sets, hmms):
    total_count = 0
    total_correct = 0
    rates = {}
    for label, data in test_data_sets.items():
        (correct, total) = get_success_rate(label, data, hmms)
        rates[label] = correct / total

        print('{}: {} / {}'.format(label, correct, total))
        total_count += total
        total_correct += correct

    print('success: {}%'.format(100 * total_correct / total_count))

if __name__ == '__main__':
    import sys
    import hmm.hmmio as hmmio

    # parameters
    count = 80
    test_count = 100
    shade_count = 5
    hmm_size = 5
    resample_size = (7, 7)

    test_image_file = './images/mnst/train-images-idx3-ubyte'
    test_label_file = './images/mnst/train-labels-idx1-ubyte'

    test_data_sets = get_data_sets(test_image_file, test_label_file, test_count, resample_size)

    if len(sys.argv) == 3 and sys.argv[1] == '-r':
        print('loading models...')
        hmms = hmmio.load(sys.argv[2])
        print('models loaded.')
    else:

        image_file = './images/mnst/train-images-idx3-ubyte'
        label_file = './images/mnst/train-labels-idx1-ubyte'

        # initialize data and hmms
        generate_model = lambda: trainer.make_2d_model(hmm_size, hmm_size, 1, shade_count)
        data_sets = get_data_sets(image_file, label_file, count, resample_size)
        test_data_sets = get_data_sets(test_image_file, test_label_file, test_count, resample_size)
        hmms = {label: generate_model() for label in data_sets}

        # train and test
        hmms = train_models(data_sets, hmms)

        if len(sys.argv) == 3 and sys.argv[1] == '-w':
            hmmio.save(hmms.items(), sys.argv[2])

    run_tests(test_data_sets, hmms)
