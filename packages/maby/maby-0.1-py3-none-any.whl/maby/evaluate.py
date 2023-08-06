import argparse
import logging
import sys
from pathlib import Path

from sklearn import metrics
from torch.utils.data import DataLoader

from maby.data import load_data
from maby.model import UNet
from maby.preprocessing import preprocess_target
from maby.train import Trainer


def dice_coef(pred, target):
    """
    Dice = (2*|X & Y|)/ (|X|+ |Y|)
         =  2*sum(|A*B|)/(sum(A^2)+sum(B^2))
    ref: https://arxiv.org/pdf/1606.04797v1.pdf
    """
    smooth = 1.
    iflat = pred.flatten().astype(bool)
    tflat = target.flatten().astype(bool)
    intersection = (iflat * tflat).sum()
    return (2. * intersection + smooth) / (iflat.sum() + tflat.sum() + smooth)


def iou_score(pred, target):
    """
    IoU = |X & Y| / (|X| + |Y| - |X & Y|)
    """
    smooth = 1.
    iflat = pred.flatten().astype(bool)
    tflat = target.flatten().astype(bool)
    intersection = (iflat * tflat).sum()
    return (intersection + smooth) / (iflat.sum() + tflat.sum() - intersection
                                      + smooth)


def mAP_score(pred, target):
    """Compute mean average precision"""
    pred = pred.flatten()
    target = target.flatten()
    pred = pred.astype(bool)
    target = target.astype(bool)
    return metrics.average_precision_score(target, pred)


def evaluate_main(data_directory, model_checkpoint):
    """
    Evaluate the model on the test set
    """
    logger = logging.getLogger(__name__)
    logger.info('Evaluating model...')

    # Load data
    logger.info('Loading data...')
    test_data = load_data(data_directory, transform=None,
                          target_transform=preprocess_target)
    test_dataloader = DataLoader(test_data, batch_size=1, shuffle=False)

    # Load model
    logger.info('Loading model...')
    model = UNet(5, 1)
    trainer = Trainer(model)
    trainer.load(model_checkpoint)

    # Evaluate
    logger.info('Evaluating...')
    loss, dice, iou, mAP = trainer.validate(test_dataloader)
    logger.info('Loss: {:.4f}'.format(loss))
    logger.info('Dice: {:.4f}'.format(dice))
    logger.info('IoU: {:.4f}'.format(iou))
    logger.info('mAP: {:.4f}'.format(mAP))


def Parser():
    parser = argparse.ArgumentParser(description='Evaluate the model')
    parser.add_argument('--directory', type=Path, required=True,
                        help='Path to the data directory')
    parser.add_argument('--model-checkpoint', type=Path, required=True,
                        help='Path to the model checkpoint')
    return parser


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse_args()
    directory = Path(args.directory)
    model_checkpoint = Path(args.model_checkpoint)
    evaluate_main(directory, model_checkpoint)
