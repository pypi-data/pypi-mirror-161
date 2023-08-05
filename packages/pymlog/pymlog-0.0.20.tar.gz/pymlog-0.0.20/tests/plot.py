import random
import mlog_test as mlog
import matplotlib.pyplot as plt

from argparse import ArgumentParser


def main(args):

    # Retrieve data
    df = mlog.get('epoch', 'loss')
    df = df.groupby('epoch').agg(['mean', 'std', 'min', 'max'])

    # Plot
    fig, ax = plt.subplots()
    ax.plot(df.index, df['loss']['mean'])
    ax.fill_between(df.index,
                    df['loss']['mean'] - df['loss']['std'],
                    df['loss']['mean'] + df['loss']['std'],
                    alpha=0.4)
    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser()
    args = parser.parse_args()
    main(args)
