#! /usr/bin/env python3

from preprocessing.zoningwriter import get_values
from hmm.trainer import make_model, train, get_success_rate
from utils.mnstreader import get_image_data, get_labels
from PIL import Image
import hmm.trainer as trainer

if __name__ == '__main__':
    image_file = './images/mnst/train-images-idx3-ubyte'
    label_file = './images/mnst/train-labels-idx1-ubyte'

    count = 100

    images, size = get_image_data(image_file, count)
    labels = get_labels(label_file)[:count]

    data_sets = {}
    hmms = {}

    shade_count = 3

    def zone(image_data):
        resample_size = (6, 6)
        img = Image.new('L', size)
        img.putdata(image_data)
        return get_values(img, resample_size, shade_count)

    for i in range(count):
        label = labels[i]
        image = zone(images[i])
        if label in data_sets:
            data_sets[label].append(image)
        else:
            data_sets[label] = [image]
            #hmms[label] = make_model(40, shade_count) #make_linear_model(14, shade_count)
            #hmms[label] = trainer.make_linear_model(44, shade_count)
            hmms[label] = trainer.make_2d_model(5, 5, 3, shade_count)
    iterations = 2
    rates = {}
    for label in data_sets:
        print('training: {}'.format(label))
        hmms[label] = train(hmms[label], data_sets[label], iterations)

    total_count = 0
    total_correct = 0
    for label, data in data_sets.items():
        (correct, total) = get_success_rate(label, data, hmms)
        rates[label] = correct / total

        print('{}: {} / {}'.format(label, correct, total))
        total_count += total
        total_correct += correct

    print('success: {}%'.format(100 * total_correct / total_count))
