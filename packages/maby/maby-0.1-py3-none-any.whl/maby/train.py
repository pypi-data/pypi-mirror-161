import argparse
import logging
import logging.config
from pathlib import Path

import torch
from torch import nn
from tqdm import tqdm

from maby.data import load_data
from maby.evaluate import dice_coef, iou_score, mAP_score
from maby.model import UNet
from maby.preprocessing import preprocess_target, segment


class Trainer:
    def __init__(self, model):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters())
        self.loss_fn = nn.L1Loss()

    def train(self, x, y):
        self.optimizer.zero_grad()
        y_pred = self.model(x)
        loss = self.loss_fn(y_pred, y)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def evaluate(self, x, y):
        with torch.no_grad():
            pred = self.model(x)
            loss = self.loss_fn(pred, y)
        # Segmented
        pred = pred.detach().numpy().squeeze()
        # Ground truth
        y = y.detach().numpy().squeeze()
        pred_seg, _ = segment(pred)
        y_seg, _ = segment(y)
        # Dice
        dice = dice_coef(pred_seg, y_seg)
        # IOU
        iou = iou_score(pred_seg, y_seg)
        # mAP
        mAP = mAP_score(pred_seg, y_seg)
        return loss.item(), dice, iou, mAP

    def save(self, epoch, checkpoint):
        state_dict = {"model": self.model.state_dict(),
                      "optimizer": self.optimizer.state_dict(),
                      "epoch": epoch}
        torch.save(state_dict, checkpoint)

    def load(self, checkpoint):
        try:
            state_dict = torch.load(checkpoint)
            self.model.load_state_dict(state_dict["model"])
            self.optimizer.load_state_dict(state_dict["optimizer"])
            return state_dict["epoch"]
        except FileNotFoundError:
            return 0

    def fit(self, dataloader, validation_dataloader,
            epochs=1, checkpoint="checkpoint.pkl"):
        self.model.train()
        current_epoch = self.load(checkpoint)
        for i in range(current_epoch, epochs):
            pbar = tqdm(dataloader, desc=f"Epoch {i}")
            # Train
            for x, y in pbar:
                loss = self.train(x, y)
                pbar.set_postfix({"loss": loss})
            self.save(i, checkpoint)

    def validate(self, validation_dataloader):
        self.model.eval()
        # Evaluate
        pbar = tqdm(validation_dataloader, desc="Validation")
        epoch_loss, epoch_dice, epoch_iou, epoch_mAP, n_samples = 0, 0, 0, 0, 0
        for x, y in pbar:
            loss, dice, iou, mAP = self.evaluate(x, y)
            epoch_loss += loss
            epoch_dice += dice
            epoch_iou += iou
            epoch_mAP += mAP
            n_samples += 1
            pbar.set_postfix({"loss": epoch_loss / n_samples,
                              "dice": epoch_dice / n_samples,
                              "iou": epoch_iou / n_samples,
                              "mAP": epoch_mAP / n_samples})
        epoch_loss /= n_samples
        epoch_dice /= n_samples
        epoch_iou /= n_samples
        epoch_mAP /= n_samples
        return epoch_loss, epoch_dice, epoch_iou, epoch_mAP


def train_main(directory):
    logger = logging.getLogger(__name__)
    logger.info('Training model...')

    # Load data
    logger.info('Loading data...')
    transform = None
    train_dataset, val_dataset = load_data(directory, transform=transform,
                                           target_transform=preprocess_target,
                                           split_validation=1)
    dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=16,
                                             shuffle=True)
    validation_dataloader = torch.utils.data.DataLoader(val_dataset,
                                                        batch_size=1)

    logger.info('Loading model...')
    model = UNet(5, 1)
    trainer = Trainer(model)
    # Train
    logger.info('Training, press Ctl+C to stop')
    try:
        trainer.fit(dataloader, validation_dataloader, epochs=3)
    except KeyboardInterrupt:
        logger.info('Training stopped')
        logger.info('Saving model...')
        trainer.save("interrupted.pkl")
    finally:
        logger.info('Validation...')
        loss, dice, iou, mAP = trainer.validate(validation_dataloader)
        logger.info('Loss: {:.4f}'.format(loss))
        logger.info('Dice: {:.4f}'.format(dice))
        logger.info('IoU: {:.4f}'.format(iou))
        logger.info('mAP: {:.4f}'.format(mAP))
        logger.info('Done')
    return model


def Parser():
    parser = argparse.ArgumentParser(description='Train model')
    parser.add_argument('--directory', type=str, default='data',
                        help='Directory with data')
    return parser


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    parser = Parser()
    args = parser.parse_args()
    directory = Path(args.directory)
    model = train_main(directory)
